# Skills

A collection of skills I use with my AI agents and want to share publicly. Each skill teaches an agent a specific task and includes the instructions, scripts and setup guidance it needs.

## Available skills

| Skill | What it does |
| --- | --- |
| [Send to Kobo](skills/send-to-kobo/SKILL.md) | Prepares selected reports and long answers as private reading copies and sends them to your Kobo through Instapaper. |

Open a skill's page for its requirements, setup instructions and usage.

## Install

Browse and install skills with [skills.sh](https://skills.sh):

```bash
npx skills@latest add wapgear/skills
```

Choose the skills and agent when prompted. Add `-g` to install globally. Run `npx skills@latest update` to update installed copies.

Or tell your agent:

> Look through https://github.com/wapgear/skills, help me choose a skill, install it for this agent, and follow its setup guide.

### Claude Code plugin

```bash
/plugin marketplace add wapgear/skills
/plugin install wapgear-skills@wapgear
```

Choose either the plugin or skills.sh for a given agent to avoid duplicate installations. Skills also use the open [Agent Skills format](https://agentskills.io/specification), so their complete folders can be installed manually in compatible agents.

## For agents and contributors

Read [AGENTS.md](AGENTS.md) for installation and maintenance guidance. Each skill lives under `skills/<name>/` and documents its own dependencies and account setup. Credentials and personal configuration stay outside the repository.

Run the repository checks with:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

MIT licensed.
