#!/usr/bin/env python3
"""Private report uploads through Instapaper API v2. No third-party dependencies."""
import argparse
import getpass
import hashlib
import html
import json
import os
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

BASE = 'https://www.instapaper.com/api/2'
CONFIG = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'kobo-reading/instapaper.json'
DATA = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'kobo-reading/api'
SOURCE = 'Reading Queue'


class UploadError(Exception):
    pass


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temp = path.with_suffix('.tmp')
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
    os.replace(temp, path)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward bearer credentials through a redirect.
        return None


def request(token, route, payload=None):
    req = Request(BASE + route,
                  data=None if payload is None else json.dumps(payload).encode(),
                  headers={'Authorization': 'Bearer ' + token,
                           'Content-Type': 'application/json',
                           'User-Agent': 'SendToKobo/1.0'})
    try:
        with build_opener(NoRedirect()).open(req, timeout=45) as response:
            return json.load(response)
    except HTTPError as exc:
        # Don't expose request headers or server response bodies containing credentials.
        raise UploadError(f'API HTTP {exc.code}; no automatic retry.') from None
    except (URLError, TimeoutError, OSError, ValueError):
        raise UploadError('Request failed or response was unreadable. Outcome may be unknown; check the list before retrying.') from None


def read_config(path):
    config = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    if not isinstance(config, dict):
        raise UploadError('Configuration must be a JSON object.')
    token = os.environ.get('INSTAPAPER_ACCESS_TOKEN') or config.get('access_token')
    if not token:
        raise UploadError('Missing access_token. Generate an owner token in the registered application; store it in the private configuration.')
    if os.name == 'posix' and path.exists() and path.stat().st_mode & 0o077:
        raise UploadError('Configuration permissions must be 0600 (chmod 600).')
    if not isinstance(token, str) or not token.strip() or any(c.isspace() for c in token):
        raise UploadError('Access token must be a nonempty string without whitespace.')
    return config, token


def reading_copy(path, title):
    text = path.read_text(encoding='utf-8')
    if not text.strip():
        raise UploadError('The reading copy is empty.')
    if path.suffix.lower() in ('.html', '.htm'):
        content = text
    elif path.suffix.lower() == '.txt':
        content = '<article><h1>' + html.escape(title) + '</h1>'
        content += ''.join('<p>' + html.escape(p).replace('\n', '<br>') + '</p>'
                           for p in text.strip().split('\n\n') if p.strip())
        content += '</article>'
    else:
        raise UploadError('Prepare UTF-8 .html or .txt first; Markdown and interactive artifacts need an intentional reading copy.')
    if not content.strip():
        raise UploadError('The reading copy is empty.')
    return content


def upload(token, path, title, root):
    content = reading_copy(path, title)
    digest = hashlib.sha256((title + '\0' + content).encode()).hexdigest()
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    receipt_path = root / (digest + '.json')
    lock = root / (digest + '.lock')
    try:
        lock_fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise UploadError('Another upload holds this report lock. Check its outcome before removing the lock.') from None
    try:
        os.close(lock_fd)
        if receipt_path.exists():
            receipt = json.loads(receipt_path.read_text())
            if receipt['state'] == 'saved':
                return receipt
            raise UploadError('An earlier attempt has an uncertain outcome. Use list and reconcile before retrying.')
        copy = root / (digest + '.html')
        fd = os.open(copy, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(content)
        receipt = {'state': 'pending', 'title': title, 'sha256': digest,
                   'local_copy': str(copy), 'kobo_confirmed': False}
        save_json(receipt_path, receipt)
        # A private_source replaces URL; never invent a source URL or send email.
        result = request(token, '/bookmarks',
                         {'title': title, 'content': content,
                          'private_source': SOURCE, 'archived': False})
        bookmark = result.get('bookmark', result) if isinstance(result, dict) else None
        if not isinstance(bookmark, dict) or not isinstance(bookmark.get('id'), int):
            raise UploadError('Save response lacked an article ID. Check Instapaper before retrying.')
        receipt.update(state='saved', article_id=bookmark['id'],
                       article_url=f"https://www.instapaper.com/read/{bookmark['id']}",
                       category=bookmark.get('category'), private_source=bookmark.get('private_source'))
        save_json(receipt_path, receipt)
        return receipt
    finally:
        lock.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=CONFIG)
    parser.add_argument('--data', type=Path, default=DATA)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('configure', help='Store an owner access token using a hidden prompt')
    sub.add_parser('status')
    sub.add_parser('list')
    send = sub.add_parser('upload')
    send.add_argument('file', type=Path)
    send.add_argument('--title', required=True)
    verify = sub.add_parser('verify')
    verify.add_argument('article_id', type=int)
    args = parser.parse_args()
    try:
        if args.command == 'configure':
            if args.config.exists():
                raise UploadError('Configuration already exists. Do not overwrite a working token; use a separate --config or edit it privately.')
            token = getpass.getpass('Instapaper owner access token (hidden): ').strip()
            if not token or any(c.isspace() for c in token):
                raise UploadError('Access token must be nonempty and contain no whitespace.')
            save_json(args.config, {'access_token': token})
            print('Private token configuration saved. Run status to verify authentication.')
            return 0
        config, token = read_config(args.config)
        if args.command in ('status', 'list'):
            result = request(token, '/bookmarks?section=home&limit=100')
            bookmarks = result.get('bookmarks', [])
            if args.command == 'status':
                output = {'authenticated': True, 'home_total': result.get('total'),
                          'kobo_private_article_confirmed': config.get('kobo_private_article_confirmed', False)}
            else:
                output = [{'id': b['id'], 'title': b.get('title'), 'category': b.get('category'),
                           'private_source': b.get('private_source')} for b in bookmarks]
        elif args.command == 'upload':
            output = upload(token, args.file, args.title, args.data)
        else:
            result = request(token, f'/bookmarks/{args.article_id}/parse')
            output = {'article_id': args.article_id, 'metadata': result.get('metadata'),
                      'content': result.get('content')}
        print(json.dumps(output, ensure_ascii=False, indent=2))
    except UploadError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (OSError, ValueError):
        print('Unable to read or write the configuration, reading copy, receipt, or API response.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
