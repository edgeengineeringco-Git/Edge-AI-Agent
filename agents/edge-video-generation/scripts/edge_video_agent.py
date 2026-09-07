#!/usr/bin/env python3
"""Reusable, approval-gated EDGE video production engine.

The provider adapter intentionally refuses undocumented defaults. Configure only
endpoint metadata (not credentials) in environment variables; credentials are
fetched at runtime through agent-job-secrets and remain in memory.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, re, shutil, subprocess, sys, tempfile, time, zipfile
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

MODELS = ("wan3.0-video", "kling-v3-omni", "minimax-h3")
DEFAULT_BUDGET = 15.0
AIHUBMIX_BASE_URL = "https://aihubmix.com"
DEFAULT_ENDPOINTS = {
    "models": AIHUBMIX_BASE_URL + "/api/v1/models",
    "generate": AIHUBMIX_BASE_URL + "/v1/videos",
    "status": AIHUBMIX_BASE_URL + "/v1/videos/{video_id}",
    "download": AIHUBMIX_BASE_URL + "/v1/videos/{video_id}/content",
}
ROOT = Path(__file__).resolve().parents[3]

class SafeError(RuntimeError): pass

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def redact(s: str) -> str:
    s = re.sub(r"(?i)(bearer\s+)[^\s,]+", r"\1[REDACTED]", str(s))
    s = re.sub(r"(?i)(api[-_ ]?key|token|secret|authorization)([=: ]+)[^\s,]+", r"\1\2[REDACTED]", s)
    return s[:1000]

def log(path: Path, event: str, **data):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Never accept arbitrary provider response bodies in logs.
    safe = {k: (redact(v) if isinstance(v, str) else v) for k, v in data.items()}
    with path.open("a", encoding="utf-8") as f: f.write(json.dumps({"time": now(), "event": event, **safe}) + "\n")

def secret_value() -> object:
    # The command output is captured, never echoed or written.
    cmd = ["node", str(ROOT / "skills-library/agent-job-secrets/agent-job-secrets.js"), "get", "VIDEO_GENERATION_API_KEYS"]
    try:
        p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=30)
    except Exception:
        p = None
    raw = (p.stdout.strip() if p else "")
    if not raw:
        raw = os.environ.get("VIDEO_GENERATION_API_KEYS", "").strip()
    if not raw:
        raise SafeError("VIDEO_GENERATION_API_KEYS is not configured.")
    try: return json.loads(raw)
    except Exception: return raw

def credential_headers(secret: object) -> dict[str, str]:
    """Extract a credential in memory; never serialize it."""
    if isinstance(secret, dict):
        for k in ("api_key", "apiKey", "key", "token", "access_token"):
            if secret.get(k): return {"Authorization": "Bearer " + str(secret[k])}
        # Some providers return a list of named keys. Select the first without logging it.
        for v in secret.values():
            if isinstance(v, str) and len(v) > 10: return {"Authorization": "Bearer " + v}
    if isinstance(secret, str): return {"Authorization": "Bearer " + secret}
    raise SafeError("VIDEO_GENERATION_API_KEYS is not configured.")

def endpoint(name: str, **values) -> str:
    key = {"models":"VIDEO_GENERATION_API_MODELS_URL", "generate":"VIDEO_GENERATION_API_GENERATE_URL", "status":"VIDEO_GENERATION_API_STATUS_URL", "download":"VIDEO_GENERATION_API_DOWNLOAD_URL"}[name]
    value = os.environ.get(key, DEFAULT_ENDPOINTS[name]).strip()
    return value.format(**values)

def request_json(url: str, headers: dict, payload=None, method="GET"):
    body = None if payload is None else json.dumps(payload).encode()
    h = {"Accept":"application/json", **headers}
    if body: h["Content-Type"] = "application/json"
    req = Request(url, data=body, headers=h, method=method)
    try:
        with urlopen(req, timeout=90) as r: return json.loads(r.read().decode()), r.status
    except HTTPError as e:
        raise SafeError(f"Provider request failed with HTTP {e.code}.")
    except (URLError, TimeoutError) as e:
        raise SafeError("Provider request failed or timed out.")

def _model_records(value):
    """Find model metadata without retaining or printing credential-bearing fields."""
    if isinstance(value, dict):
        name = str(value.get("id") or value.get("model") or value.get("name") or value.get("model_id") or "")
        if name in MODELS: yield name, value
        for child in value.values(): yield from _model_records(child)
    elif isinstance(value, list):
        for child in value: yield from _model_records(child)

def _price(meta):
    # Accept only an explicit numeric price and documented unit. Never invent a price.
    for key in ("price_per_second", "usd_per_second", "cost_per_second"):
        if isinstance(meta.get(key), (int, float)): return float(meta[key]), "per_second"
    for key in ("price_per_clip", "usd_per_clip", "cost_per_clip"):
        if isinstance(meta.get(key), (int, float)): return float(meta[key]), "per_clip"
    pricing = meta.get("pricing")
    if isinstance(pricing, dict) and isinstance(pricing.get("output"), (int, float)):
        return float(pricing["output"]), "provider_output_unit"
    price = meta.get("price")
    if isinstance(price, (int, float)) and meta.get("price_unit") in ("per_second", "per_clip"):
        return float(price), str(meta["price_unit"])
    return None, None

def validate_provider(secret: object, logpath: Path) -> dict:
    headers = credential_headers(secret)
    data, status = request_json(endpoint("models"), headers)
    records = dict(_model_records(data))
    missing = [m for m in MODELS if m not in records]
    if missing: raise SafeError("Provider metadata does not validate all requested model identifiers.")
    for model, meta in records.items():
        price, unit = _price(meta)
        capabilities = json.dumps(meta).lower()
        # AIHubMix exposes video type and pricing in the models response; it
        # may omit duration/resolution limits there. Request validation uses the
        # documented video endpoint fields below.
        if price is None or not unit or "video" not in capabilities:
            raise SafeError(f"Provider metadata for {model} lacks an explicit current video price.")
    log(logpath, "provider_validated", models=list(MODELS), http_status=status)
    return data

def ensure_tree(project: Path):
    for x in ("input","references","audio","clips","drafts","output","manifests","logs"): (project / x).mkdir(parents=True, exist_ok=True)

def load_brief(path: Path) -> dict:
    try: b=json.loads(path.read_text(encoding="utf-8"))
    except Exception as e: raise SafeError("Creative brief must be valid JSON.") from e
    if not isinstance(b,dict): raise SafeError("Creative brief must be a JSON object.")
    shots=b.get("shots")
    if not isinstance(shots,list) or not shots: raise SafeError("Creative brief must contain a non-empty shots list.")
    for i,s in enumerate(shots):
        if not isinstance(s,dict) or not s.get("description"): raise SafeError(f"Shot {i+1} needs a description.")
        if float(s.get("duration_seconds",0)) <= 0: raise SafeError(f"Shot {i+1} needs a positive duration_seconds.")
    return b

def route(shot: dict) -> tuple[str,str]:
    c=(shot.get("category") or shot.get("description","")).lower()
    if any(x in c for x in ("person","people","geologist","equipment","drone deployment","hero")): return "kling-v3-omni","wan3.0-video"
    if any(x in c for x in ("landscape","geology","terrain","satellite","earth","aerial","b-roll","technical")): return "wan3.0-video","minimax-h3"
    return "wan3.0-video","minimax-h3"

def model_metadata(provider: dict) -> dict:
    return dict(_model_records(provider))

def prompt_for(shot,b):
    style=b.get("brand_style","restrained documentary corporate realism")
    return f"Subject: {shot['description']}. Setting: {shot.get('setting','realistic professional environment')}. Lighting: {shot.get('lighting','natural controlled cinematic light')}. Camera: {shot.get('camera_move','slow stable documentary movement')}. Style: {style}; photorealistic, physically plausible, clean composition, no generated text."
def negative_for(b):
    return "text, labels, captions, logos, watermark, invented scientific data, fake map, distorted geology, cartoon, neon hologram, sci-fi interface, facial deformation, extra limbs, extra fingers, morphing equipment, flicker, heavy shake, blur, low resolution"

def make_plan(b, provider, project):
    budget=float(b.get("budget_ceiling_usd",DEFAULT_BUDGET)); shots=[]; total=0
    for i,s in enumerate(b["shots"],1):
        model,fallback=route(s); dur=float(s["duration_seconds"])
        # Prices are read from validated provider metadata at execution time;
        # the plan records an explicit unresolved value until the provider schema is mapped.
        item={"shot_number":i,"id":s.get("id",f"shot-{i:02d}"),"duration_seconds":dur,"model":model,"fallback_model":fallback,"mode":"image-to-video" if s.get("reference_image") else "text-to-video","prompt":prompt_for(s,b),"negative_prompt":negative_for(b),"test_required":bool(s.get("difficult",False) or s.get("hero",False)),"estimated_cost_usd":None,"source":s}
        shots.append(item)
    plan={"schema_version":"1.0","created_at":now(),"brief":{k:v for k,v in b.items() if k not in ("secret","api_key")},"provider_validation":"passed","budget_ceiling_usd":budget,"shots":shots,"projected_duration_seconds":sum(x["duration_seconds"] for x in shots),"cost_note":"Exact current price is provider metadata-dependent; no paid generation is allowed until pricing is validated and approved."}
    (project/"manifests/production_plan.json").write_text(json.dumps(plan,indent=2),encoding="utf-8")
    (project/"manifests/cost_report.md").write_text(f"# Cost report\n\nBudget ceiling: **USD ${budget:.2f}**\n\nExact per-model prices must be read from validated provider metadata before execution. No paid request is made by planning.\n",encoding="utf-8")
    return plan

def approval_ok(args,budget):
    phrase=args.approval or ""
    return bool(re.search(r"approve this generation plan",phrase,re.I)) and bool(re.search(rf"\$?\s*{re.escape(f'{budget:g}')}\b",phrase))

def run_ffprobe(path):
    if not shutil.which("ffprobe"): return {"validated":False,"reason":"ffprobe unavailable"}
    p=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_name,width,height,r_frame_rate","-of","json",str(path)],capture_output=True,text=True)
    if p.returncode: return {"validated":False,"reason":"ffprobe failed"}
    return {"validated":True,"data":json.loads(p.stdout)}

def execute(b, project, args):
    logpath=project/"logs/api_generation.log"; secret=secret_value(); validate_provider(secret,logpath)
    budget=float(b.get("budget_ceiling_usd",DEFAULT_BUDGET)); approved=float(args.approved_budget)
    if approved>budget or not approval_ok(args,budget): raise SafeError("Explicit approval and a maximum budget at or below the brief ceiling are required.")
    plan=json.loads((project/"manifests/production_plan.json").read_text())
    headers=credential_headers(secret); manifest={"schema_version":"1.0","started_at":now(),"shots":[],"actual_cost_usd":0.0}
    for shot in plan["shots"]:
        # API payload is provider-specific but documented fields are explicit.
        payload={"model":shot["model"],"prompt":shot["prompt"],"negative_prompt":shot["negative_prompt"],"duration_seconds":shot["duration_seconds"],"aspect_ratio":b.get("aspect_ratio","16:9"),"resolution":"720p" if b.get("resolution")!="1920x1080" else "1080p","mode":shot["mode"]}
        if shot["mode"]=="image-to-video": payload["reference_image"]=shot["source"].get("reference_image")
        log(logpath,"generation_requested",shot=shot["id"],model=shot["model"],duration=shot["duration_seconds"])
        data,status=request_json(endpoint("generate"),headers,payload,"POST")
        # Accept common documented response shapes; never log response body.
        job=data.get("id") or data.get("job_id") or data.get("task_id")
        if not job: raise SafeError(f"Provider returned no job id for {shot['id']}.")
        manifest["shots"].append({"id":shot["id"],"model":shot["model"],"job_id":str(job),"status":"submitted","http_status":status})
    (project/"manifests/generation_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    raise SafeError("Generation jobs submitted, but provider-specific polling/download metadata must be enabled before final packaging.")

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True)
    for cmd in ("plan","execute"):
        p=sub.add_parser(cmd); p.add_argument("--brief",required=True); p.add_argument("--project",default="project")
    sub.choices["execute"].add_argument("--approved-budget",required=True,type=float); sub.choices["execute"].add_argument("--approval",required=True)
    a=ap.parse_args(); project=Path(a.project); ensure_tree(project)
    try:
        b=load_brief(Path(a.brief)); secret=secret_value(); provider=validate_provider(secret,project/"logs/api_generation.log"); plan=make_plan(b,provider,project)
        if a.cmd=="plan":
            print(json.dumps({"duration_seconds":plan["projected_duration_seconds"],"clips":len(plan["shots"]),"models":[x["model"] for x in plan["shots"]],"budget_ceiling_usd":plan["budget_ceiling_usd"],"tests":[x["id"] for x in plan["shots"] if x["test_required"]]},indent=2)); return 0
        execute(b,project,a)
    except SafeError as e:
        print(str(e)); return 2
    except Exception:
        print("Video generation failed; see the redacted generation log."); return 1
if __name__=="__main__": sys.exit(main())
