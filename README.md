# Skills

Agent skills for tasks I want to hand off in one sentence.

## Send this to my Kobo

Finished a research report or a long conversation? Say **“Send this to my Kobo.”** Your agent prepares a readable copy and uploads it privately to your own Instapaper account. Refresh **My Articles** on your Kobo and read it there.

The first skill is [send-to-kobo](skills/send-to-kobo/SKILL.md). It includes a Python uploader, local reading copies and receipts, and an [agent setup guide](skills/send-to-kobo/references/setup.md). It uses the private-content API, because native email imports do not sync to Kobo. No public webpage or custom firmware is needed.

### Install through skills.sh

```bash
npx skills@latest add wapgear/skils --skill send-to-kobo
```

Choose your agent when prompted. Add `-g` for a global installation, or use `-a codex` / `-a claude-code` to select an agent. Update installed copies with `npx skills@latest update`.

You can tell your agent:

> Install the send-to-kobo skill from https://github.com/wapgear/skils. Read its agent setup guide and help me connect my own Instapaper account. Keep my credentials outside the repo and chat. Then send a short test to my Kobo.

Requires Python 3.10+, network access, a personal Instapaper API token, and Kobo's My Articles integration. Setup is once per account/machine. The uploader has no Python dependencies; the skills CLI has its own Node.js requirements.

### Claude Code plugin

```bash
/plugin marketplace add wapgear/skils
/plugin install wapgear-skills@wapgear
```

Use either this plugin or skills.sh for the same agent to avoid duplicate skills. The portable skill folder can also be copied into another compatible agent's skills directory.

### Your data and credentials

Each person generates their own **Owner Only** API token in Instapaper and saves it through a hidden terminal prompt. No API keys, tokens, account IDs, import addresses or personal reports are included here. Reports are sent to Instapaper's service, with a private source label and no public source URL. Local copies and receipts stay outside this repository.

The API route has been tested on a Kobo Libra Colour: the private report appeared and opened. Offline reopening has not yet been verified. Other devices and firmware need their own test. Folders and email imports are excluded from Kobo sync; interactive artifacts need a static reading copy.

### Discovery

This repository uses the open [Agent Skills format](https://agentskills.io/specification), compatible with the [skills CLI](https://github.com/vercel-labs/skills). [skills.sh](https://skills.sh/docs/faq) indexes skills through installation telemetry; publishing a repository does not guarantee immediate search or leaderboard visibility. The GitHub install command works independently of that indexing delay.

## For agents and contributors

Read [AGENTS.md](AGENTS.md). Keep each skill self-contained under `skills/<name>/`, with a `SKILL.md`, only the resources it needs, and no machine-specific configuration. The layout follows conventions used by [Matt Pocock's skills](https://github.com/mattpocock/skills); this repository is independently maintained.

Run the checks before publishing:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

MIT licensed. Not affiliated with or endorsed by Instapaper or Rakuten Kobo.
