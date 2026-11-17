# Working with this skills repository

## Installing for a user

If asked to install or use a skill, read its `skills/<name>/SKILL.md`, then any first-use guide it links. For send-to-kobo, use [the agent setup guide](skills/send-to-kobo/references/setup.md). Install the complete folder using the skills CLI or the current agent's supported manual installation path. Never run a real upload just to discover a skill.

Resolve resources relative to the installed skill folder. Use the user's own account. Have the user enter credentials through a private terminal prompt or secret manager, never chat, command-line literals or repository files. Do not copy the maintainer's local configuration. Confirm a test on the user's physical device rather than treating a web/API success as proof.

## Maintaining the repository

Use `skills/<skill-name>/SKILL.md` with matching lowercase hyphenated names. Keep shared instructions short and move one-time setup into a linked reference. Update the root README catalogue and plugin skill list when adding a skill. Keep runtime dependencies explicit and minimal.

Do not add credentials, user data, private account URLs, machine paths or generated reading copies. Configuration and receipts live outside this checkout. Tests must mock network mutations and must never depend on a maintainer's token. Any live upload needs a user-selected item.

Before publishing, run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`, validate skill metadata, and review the exact staged diff for secrets and private details. Test CLI discovery when skill layout changes. Keep publishing claims factual: distinguish installability from search/index visibility and article upload from device confirmation.
