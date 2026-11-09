"""Serve the review page of this folder on 127.0.0.1, save the decisions, notes, replies and edited texts beside it
as they are made, and write the instructions file when the page asks for it. Reads round.json (written by
build_round.py). Python 3, no packages.   Usage: python serve_dashboard.py [--port N] [--no-browser]"""

import argparse
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import math
from pathlib import Path
import threading
import time
from urllib.parse import urlsplit
import webbrowser

FOLDER = Path(__file__).resolve().parent
STATUSES = {'Open', 'Apply', 'Apply with edits', 'Keep as is', 'Discuss', 'Later'}
MAX_NOTE = 20_000
MAX_BODY = 5_000_000
MAX_EDIT_TEXT = 60_000
SAVE_LOCK = threading.Lock()


class ReviewServer(ThreadingHTTPServer):
    daemon_threads = True


def write_atomic(folder, name, text):
    destination = folder / name
    temp = folder / (name + '.tmp')
    temp.write_text(text, encoding='utf-8')
    # A sync client (OneDrive, Dropbox) may briefly hold the file; keep the last good copy until replace succeeds.
    for attempt in range(5):
        try:
            temp.replace(destination)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.1 * 2 ** attempt)


def clean_edits(value):
    """Validate the per-edit state: {"<n>": {"text": str, "include": bool}}."""
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError('Invalid edit state')
    clean = {}
    for key, entry in value.items():
        if not (isinstance(key, str) and key.isdigit() and isinstance(entry, dict)):
            raise ValueError('Invalid edit state')
        item = {}
        if 'text' in entry:
            if not isinstance(entry['text'], str) or len(entry['text']) > MAX_EDIT_TEXT:
                raise ValueError('Invalid edited text')
            item['text'] = entry['text']
        if 'include' in entry:
            if not isinstance(entry['include'], bool):
                raise ValueError('Invalid edit flag')
            item['include'] = entry['include']
        if item:
            clean[key] = item
    return clean


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, names=None, **kwargs):
        self.folder = Path(directory).resolve()
        self.names = names
        super().__init__(*args, directory=str(self.folder), **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()

    def respond(self, code, value):
        payload = json.dumps(value, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def config(self):
        return json.loads((self.folder / self.names['review']).read_text(encoding='utf-8'))

    def saved(self, snapshot):
        path = self.folder / self.names['decisions']
        if path.exists():
            result = json.loads(path.read_text(encoding='utf-8'))
            if result.get('manuscript_sha256') != snapshot:
                raise ValueError('Existing annotations refer to another manuscript snapshot; file preserved.')
            return result
        return {'manuscript_sha256': snapshot, 'decisions': {
            item['id']: {'title': item['title'], 'status': 'Open', 'note': '', 'reply': '', 'updated': 0}
            for item in self.config()['items']
        }}

    def read_json_body(self):
        origin = self.headers.get('Origin')
        if origin and origin != 'http://' + self.headers.get('Host', ''):
            raise PermissionError('Only same-origin local saves are allowed')
        size = int(self.headers.get('Content-Length', '0'))
        if not 0 < size <= MAX_BODY:
            raise ValueError('Invalid payload size')
        return json.loads(self.rfile.read(size))

    def do_GET(self):
        if urlsplit(self.path).path != '/api/decisions':
            return super().do_GET()
        try:
            with SAVE_LOCK:
                result = self.saved(self.config()['metadata']['manuscript_hash'])
            self.respond(200, result)
        except (ValueError, OSError) as error:
            self.respond(409, {'error': str(error)})

    def do_POST(self):
        route = urlsplit(self.path).path
        if route not in ('/api/decisions', '/api/instructions'):
            return self.respond(404, {'error': 'Unknown endpoint'})
        try:
            incoming = self.read_json_body()
            config = self.config()
            snapshot = config['metadata']['manuscript_hash']
            if incoming.get('manuscript_sha256') != snapshot:
                return self.respond(409, {'error': 'Manuscript snapshot mismatch; nothing saved'})
            if route == '/api/instructions':
                markdown = incoming.get('markdown')
                if not isinstance(markdown, str) or not markdown.strip():
                    raise ValueError('Expected the instructions as Markdown text')
                with SAVE_LOCK:
                    write_atomic(self.folder, self.names['instructions'], markdown if markdown.endswith('\n') else markdown + '\n')
                print(f'Saved {self.names["instructions"]}', flush=True)
                return self.respond(200, {'saved': True, 'file': self.names['instructions']})
            entries = incoming.get('decisions')
            if not isinstance(entries, dict):
                return self.respond(400, {'error': 'Expected a decision mapping'})
            titles = {item['id']: item['title'] for item in config['items']}
            clean = {}
            for key, value in entries.items():
                if key not in titles or not isinstance(value, dict):
                    raise ValueError('Unknown review item')
                status, note, reply = value.get('status', 'Open'), value.get('note', ''), value.get('reply', '')
                stamp = float(value.get('updated', 0))
                if status not in STATUSES or not math.isfinite(stamp):
                    raise ValueError('Invalid decision')
                if not (isinstance(note, str) and isinstance(reply, str) and len(note) <= MAX_NOTE and len(reply) <= MAX_NOTE):
                    raise ValueError('Invalid note or reply')
                clean[key] = {'title': titles[key], 'status': status, 'note': note, 'reply': reply, 'updated': stamp,
                              'edits': clean_edits(value.get('edits'))}
            with SAVE_LOCK:
                result = self.saved(snapshot)
                for key, entry in clean.items():
                    old = result['decisions'].get(key)
                    if old is None or entry['updated'] > float(old.get('updated', 0)):
                        result['decisions'][key] = entry
                result['manuscript'] = config['metadata']['manuscript']
                result['saved_at'] = datetime.now(timezone.utc).isoformat()
                write_atomic(self.folder, self.names['decisions'], json.dumps(result, ensure_ascii=False, indent=2))
            self.respond(200, {'saved': True, 'file': self.names['decisions']})
        except PermissionError as error:
            self.respond(403, {'error': str(error)})
        except (ValueError, TypeError, AttributeError, OSError) as error:
            self.respond(400, {'error': str(error)})

    def log_message(self, format, *args):
        # Keep routine autosaves quiet; still show failures.
        if len(args) > 1 and str(args[1]).isdigit() and int(args[1]) < 400:
            return
        super().log_message(format, *args)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    try:
        names = json.loads((FOLDER / 'round.json').read_text(encoding='utf-8'))
    except OSError:
        parser.error('round.json is missing. Run build_round.py first.')
    if not (FOLDER / names['page']).is_file():
        parser.error('The dashboard HTML is missing. Run build_round.py first.')
    port = args.port or int(names.get('port', 8765))
    try:
        server = ReviewServer(('127.0.0.1', port), partial(Handler, directory=str(FOLDER), names=names))
    except OSError as error:
        parser.exit(1, f'Cannot start the dashboard: {error}\nAnother dashboard may be running on port {port}: close its window, or use --port.\n')
    url = f'http://127.0.0.1:{port}/{names["page"]}'
    print(f'Dashboard: {url}\nDecisions: {FOLDER / names["decisions"]}\nInstructions: {FOLDER / names["instructions"]} '
          '(written by the Save instructions button)\nKeep this window open; Ctrl+C stops the server.', flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
