"""Uploader reliability checks; all API calls mocked."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / 'skills/send-to-kobo/scripts/instapaper.py'
spec = importlib.util.spec_from_file_location('uploader', MODULE)
uploader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(uploader)


class UploadTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'report.html'
        self.source.write_text('<article><p>Private report &amp; source.</p></article>')
        self.queue = self.root / 'queue'

    def test_private_upload_and_repeat_do_not_duplicate(self):
        with patch.object(uploader, 'request', return_value={'id': 123, 'category': 0,
                                                          'private_source': 'Reading Queue'}) as api:
            first = uploader.upload('secret', self.source, 'Research', self.queue)
            second = uploader.upload('secret', self.source, 'Research', self.queue)
        self.assertEqual(first, second)
        self.assertEqual(api.call_count, 1)
        payload = api.call_args.args[2]
        self.assertNotIn('url', payload)
        self.assertNotIn('category', payload)
        self.assertEqual(payload['content'], self.source.read_text())
        self.assertFalse(payload['archived'])
        self.assertEqual(Path(first['local_copy']).stat().st_mode & 0o777, 0o600)

    def test_ambiguous_failure_blocks_another_post(self):
        with patch.object(uploader, 'request', side_effect=uploader.UploadError('timeout')) as api:
            with self.assertRaises(uploader.UploadError):
                uploader.upload('secret', self.source, 'Research', self.queue)
            with self.assertRaisesRegex(uploader.UploadError, 'uncertain outcome'):
                uploader.upload('secret', self.source, 'Research', self.queue)
        self.assertEqual(api.call_count, 1)
        self.assertEqual(json.loads(next(self.queue.glob('*.json')).read_text())['state'], 'pending')

    def test_bad_save_response_keeps_pending_receipt(self):
        with patch.object(uploader, 'request', return_value={'error': 'unexpected'}):
            with self.assertRaises(uploader.UploadError):
                uploader.upload('secret', self.source, 'Research', self.queue)
        self.assertEqual(json.loads(next(self.queue.glob('*.json')).read_text())['state'], 'pending')

    def test_text_is_escaped_and_markdown_requires_conversion(self):
        text = self.root / 'report.txt'
        text.write_text('A < B\nnext line\n\nSecond paragraph')
        result = uploader.reading_copy(text, 'Title & source')
        self.assertIn('A &lt; B<br>next line', result)
        self.assertIn('Title &amp; source', result)
        text = text.with_suffix('.md')
        text.write_text('# Report')
        with self.assertRaises(uploader.UploadError):
            uploader.reading_copy(text, 'Report')


class CredentialTests(unittest.TestCase):
    def test_config_requires_private_permissions(self):
        if uploader.os.name != 'posix':
            self.skipTest('POSIX mode check')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'config.json'
            path.write_text(json.dumps({'access_token': 'test-only-placeholder'}))
            path.chmod(0o644)
            with patch.dict(uploader.os.environ, {}, clear=True):
                with self.assertRaisesRegex(uploader.UploadError, '0600'):
                    uploader.read_config(path)
                path.chmod(0o600)
                self.assertEqual(uploader.read_config(path)[1], 'test-only-placeholder')

    def test_secret_manager_token_needs_no_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(uploader.os.environ, {'INSTAPAPER_ACCESS_TOKEN': 'test-only-placeholder'}, clear=True):
                self.assertEqual(uploader.read_config(Path(tmp) / 'missing.json')[1], 'test-only-placeholder')

    def test_http_errors_do_not_reveal_response_or_token(self):
        error = uploader.HTTPError(uploader.BASE + '/bookmarks', 401,
                                   'test-only-secret-in-response', {}, None)
        with patch.object(uploader, 'build_opener') as opener:
            opener.return_value.open.side_effect = error
            with self.assertRaises(uploader.UploadError) as caught:
                uploader.request('test-only-token', '/bookmarks')
        self.assertNotIn('test-only-secret', str(caught.exception))
        self.assertNotIn('test-only-token', str(caught.exception))

    def test_redirect_does_not_forward_bearer_token(self):
        request = uploader.Request(uploader.BASE, headers={'Authorization': 'Bearer test-only-token'})
        self.assertIsNone(uploader.NoRedirect().redirect_request(request, None, 302,
                                                               'Found', {}, 'https://example.org'))


if __name__ == '__main__':
    unittest.main()
