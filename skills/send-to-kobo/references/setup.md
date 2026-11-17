# Agent setup guide

This is the first-use guide for any agent installing `send-to-kobo`. Use the user's own account and local configuration. The repository supplies code and instructions, not a hosted service or shared account.

## Requirements and installation

You need Python 3.10 or newer, access to `https://www.instapaper.com`, an Instapaper account, and a Kobo offering **My Articles → Link with Instapaper**. No custom firmware or Python packages are required. The skills CLI additionally needs a supported Node.js version; check its current requirements if installation fails.

Install with `npx skills@latest add wapgear/skills --skill send-to-kobo`, selecting the user's agent and project/global scope. If the CLI is unavailable, copy the complete `skills/send-to-kobo` directory into the agent's documented skills directory. Keep `scripts/` and `references/` with `SKILL.md`. Avoid duplicate installations through both a plugin and the CLI.

Locate the installed skill and run its script with `--help`. Every command below assumes the working directory is the installed skill folder. On systems using `python` rather than `python3`, use the available Python 3.10+ executable.

You can ask an agent:

> Install the send-to-kobo skill from https://github.com/wapgear/skills. Read its setup guide and help me connect my own Instapaper account. Keep my credentials outside the repo and chat. Then send a short test to my Kobo.

This skill is independently maintained and is not affiliated with or endorsed by Instapaper or Rakuten Kobo.

## Connect the user's account

1. Open [Instapaper applications](https://www.instapaper.com/developers/applications) in a browser the user controls. Have them sign in there; do not request passwords in chat.
2. Register a personal application with a descriptive name, such as **Reading Queue**, and an accurate description of this personal upload use. Use the user's own contact details where required. Review the [API terms](https://www.instapaper.com/developers/overview/api-terms) and obtain any confirmation the agent's environment requires.
3. Leave the application **Owner Only**. It can access its owner's account without public review. Callback URIs and a hosted application are unnecessary for this owner's token workflow.
4. In that application's page, choose **Generate access token**. It is shown once. Do not regenerate an existing working token: regeneration invalidates it. A client ID or client secret is not needed by this uploader.
5. In the user's own interactive terminal, run:

   ```bash
   python3 scripts/instapaper.py configure
   ```

   The user pastes the owner token into the hidden prompt. The script stores it outside the repo in `~/.config/kobo-reading/instapaper.json`, with mode 0600 on POSIX systems. Never put a token in a command argument, committed file, example, screenshot or chat message. On Windows, ensure the config folder is accessible only to the intended user through its ACLs.
6. Run `python3 scripts/instapaper.py status`. It reports authentication status, not credentials.
7. Link the same account on the Kobo, upload one short user-approved test report, and verify its parsed content. Ask the user to refresh My Articles, open it, and then reopen it with Wi-Fi off. Record device and offline confirmation separately from a successful API save.

Alternatively, a secret manager can inject `INSTAPAPER_ACCESS_TOKEN` into the process environment. Do not print it. The script supports `XDG_CONFIG_HOME` and `XDG_DATA_HOME`. Explicit `--config PATH` and `--data PATH` options go **before** the subcommand. Use separate configuration and data directories for separate accounts; receipts are local to that account's setup. Moving machines without the receipts removes local duplicate detection.

## Routine commands

```bash
python3 scripts/instapaper.py status
python3 scripts/instapaper.py list
python3 scripts/instapaper.py upload /absolute/path/report.html --title 'Report title'
python3 scripts/instapaper.py verify ARTICLE_ID
```

Uploads retain HTML and JSON receipts in `~/.local/share/kobo-reading/api/`. Nothing uploads merely because it is placed in that directory. There is no background folder watcher; each report needs an explicit user selection. This also follows Instapaper's per-item API rules.

`verify` returns the parsed article text for inspection; that output can contain private report content. `list` shows the first 100 main-list items. For larger libraries or an old ambiguous upload, inspect the signed-in Instapaper account rather than assuming an absent first-page result proves failure.

## Failed or ambiguous submissions

A pending receipt means a POST may already have saved the article. Don't retry automatically. Inspect Instapaper and run `verify` on a candidate article ID to compare the title and full report. If it matches, update that receipt locally to `state: saved`, with the verified `article_id`, `article_url`, `category` and `private_source`. Keep its original title, digest and local copy. If no matching save exists, only reset the pending receipt after confirming the server-side result and obtaining the user's direction to retry. A leftover `.lock` may indicate a running uploader or a crashed process; check which before removing it.

HTTP 401 usually calls for checking the token or account authorization; don't regenerate tokens reflexively. The uploader never follows redirects with bearer credentials, never retries POSTs automatically, and has no archive or delete command.

## Compatibility boundary

Regular web articles and the tested private API HTML route are suitable for My Articles. Native email imports are not: the website may show them while Kobo silently omits them. Changing the title, tags or folder does not convert an email into an Article. Do not use a fake URL or undocumented category mutation as a workaround.

Official references: [authentication](https://www.instapaper.com/developers/overview/authentication), [bookmarks and private content](https://www.instapaper.com/developers/v2/reference/bookmarks), [Kobo integration](https://www.instapaper.com/docs/ereaders/kobo).
