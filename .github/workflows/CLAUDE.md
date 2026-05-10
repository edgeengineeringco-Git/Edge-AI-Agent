# .github/workflows/ — GitHub Actions (MANAGED)

**These files are auto-synced by `thepopebot init` and `thepopebot upgrade`. Do not edit them — changes will be overwritten.**

## Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `rebuild-event-handler.yml` | Push to `main` | Rebuilds the event handler server |
| `upgrade-event-handler.yml` | Manual dispatch | Creates a PR to upgrade thepopebot |
| `auto-merge.yml` | Job PR opened | Squash-merges PRs within allowed paths |
| `notify-pr-complete.yml` | After auto-merge | Sends job completion notification |

## Customization

If you need custom workflows, create new `.yml` files outside this directory or in a separate workflow path. Do not modify these managed files — they will be reset on upgrade.
