---
name: send-to-kobo
description: Send selected research reports, long answers, and static artifact reading copies to a Kobo through Instapaper's private-content API. Use when the user asks to read something on their Kobo or send it to Instapaper.
license: MIT
---

# Send this to my Kobo

Requires Python 3.10+, network access, a personal API token and a Kobo with My Articles. No Python dependencies.

Use the bundled `scripts/instapaper.py` with the user's own Instapaper API v2 token. Resolve script paths relative to this skill's actual installation directory; do not assume a particular agent, home directory, browser, or operating system.

## First use

Run `python3 scripts/instapaper.py status`. If credentials are missing, follow [the agent setup guide](references/setup.md). Never ask the user to paste tokens or passwords into chat. No credentials are distributed with this skill.

## Prepare the reading copy

Create UTF-8 HTML with a title, headings, paragraphs, lists, simple tables and real source links. Preserve the requested detail, evidence, dates and uncertainty. Replace chat citation tokens and internal note links with readable references. Convert interactive artifacts and PDFs into a static reading copy; explain any meaningful omissions. Plain `.txt` is also accepted; convert Markdown intentionally before uploading.

Upload only the content the user selected. An upload sends it to Instapaper's service. Keep local copies outside source repositories. Do not publish a webpage or invent a source URL.

## Upload and verify

```bash
python3 scripts/instapaper.py upload /absolute/path/report.html --title 'Report title'
python3 scripts/instapaper.py verify ARTICLE_ID
```

The uploader supplies `private_source` and `content`, without a public URL. It keeps private local reading copies and receipts. Verify the parsed response retains the intended report, especially its ending, sources, tables and lists. Report the returned article URL.

Identical title/content reuses the local successful receipt. A changed report creates a new article. If a request's outcome is uncertain, stop: use `list` and inspect the account before retrying. The setup guide explains receipt reconciliation. Never blindly resend or delete a pending receipt. Do not archive, overwrite or delete existing articles without a user request.

## Read on the Kobo

Link the same Instapaper account under **More → My Articles**, then refresh. Keep reports in the main unread list. Folders, email-imported text, videos, PDFs, tags, notes and highlights are not supported by this delivery workflow. Email-imported text is a different content type and does not sync to Kobo.

Private API HTML returned as Article (`category: 0`) was verified to appear and open on a Kobo Libra Colour. Other devices and firmware still need their own test. Do not claim offline delivery until the user confirms the article reopens with Wi-Fi off. Distinguish prepared locally, saved in Instapaper, opened on Kobo, and confirmed offline.

Sources: [API bookmarks](https://www.instapaper.com/developers/v2/reference/bookmarks), [API authentication](https://www.instapaper.com/developers/overview/authentication), [Kobo support and limitations](https://www.instapaper.com/docs/ereaders/kobo).
