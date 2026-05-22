export const SessionTracker = async ({ $ }) => {
  if (process.env.CONTINUE_SESSION !== "1") return {};
  const fs = await import("fs");
  const path = await import("path");
  const dir = "/home/coding-agent/.opencode-ttyd-sessions";
  const port = process.env.PORT || "7681";
  const file = path.join(dir, port);
  let captured = false;

  return {
    event: async ({ event }) => {
      if (captured) return;
      const sessionID = event?.properties?.sessionID;
      if (!sessionID) return;
      captured = true;
      fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(file, sessionID);
    }
  }
}
