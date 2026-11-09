"""Browser test of a built review round, on a copy of its folder and a spare port.

  python test_dashboard.py [ROUND_FOLDER] [--port 8799] [--shots DIR] [--keep]

It makes its own temporary copy of the round folder and serves it on the spare port, so the folder is not touched.

Checks that the page loads and is connected to the local server; that a decision, an edited text, an unticked
edit, a changed symbol and a note are saved, written to the instructions and kept after a reload; and that, with
every card accepted, the saved instructions re-applied by apply_instructions.py reproduce the proposal exactly.
Needs the Python package playwright and a Chromium (set PLAYWRIGHT_BROWSERS_PATH if it is preinstalled).
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('folder', nargs='?', default=str(Path(__file__).resolve().parent))
ap.add_argument('--port', type=int, default=8799)
ap.add_argument('--shots', help='folder for three screenshots of the page')
ap.add_argument('--keep', action='store_true', help='keep the temporary copy (it is kept anyway when a check fails)')
args = ap.parse_args()
SRC = Path(args.folder).resolve()
sys.path.insert(0, str(SRC))
import cards  # noqa: E402

manuscript = (SRC / cards.ROUND.get('manuscript_path', '../../' + cards.ROUND['manuscript'])).resolve()
names = json.loads((SRC / 'round.json').read_text(encoding='utf-8'))
T = Path(tempfile.mkdtemp(prefix='review_test_'))
for f in (names['page'], names['review'], names['proposal'], 'round.json', 'serve_dashboard.py', 'apply_instructions.py'):
    shutil.copy(SRC / f, T / f)
review = json.loads((T / names['review']).read_text(encoding='utf-8'))
items, meta = review['items'], review['metadata']
first = lambda cond: next((i for i in items if cond(i)), None)
c_edit = first(lambda i: i['kind'] == 'edit')
c_multi = first(lambda i: i['kind'] == 'edit' and len(i['edits']) > 1 and i is not c_edit) or first(lambda i: i['kind'] == 'edit' and len(i['edits']) > 1)
c_ren = first(lambda i: i['kind'] == 'rename')
c_sug = first(lambda i: i['kind'] == 'instruction')
ok = True


def check(name, cond, info=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name + (f' \u2014 {info}' if info else ''))
    ok = ok and bool(cond)


def section(md, cid):
    s = md[md.index(f'## {cid} \u00b7 '):]
    end = s.find('\n## ', 5)
    return s if end < 0 else s[:end]


srv = subprocess.Popen([sys.executable, str(T / 'serve_dashboard.py'), '--port', str(args.port), '--no-browser'],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
time.sleep(1.5)
URL = f'http://127.0.0.1:{args.port}/{names["page"]}'
instr = T / names['instructions']
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        errors = []

        def page():
            pg = b.new_context(viewport={'width': 1400, 'height': 1000}).new_page()
            pg.on('pageerror', lambda e: errors.append(str(e)))
            pg.goto(URL)
            pg.wait_for_selector('article.item')
            pg.wait_for_timeout(600)
            return pg
        pg = page()
        check('cards rendered', pg.locator('article.item').count() == len(items), str(pg.locator('article.item').count()))
        check('connected to the local server', pg.locator('#server-warning').is_hidden())
        check('no unresolved card link', '[[' not in pg.inner_text('body'))
        check('all cards undecided at start', pg.locator('#s-open').inner_text() == str(len(items)))
        if c_edit:
            art = pg.locator(f'#{c_edit["id"]}')
            art.locator('.toggle-edit').first.click()
            ta = art.locator('.editor textarea').first
            ta.fill(ta.input_value() + ' EDITED-BY-TEST')
        if c_multi and c_multi is not c_edit:
            pg.locator(f'#{c_multi["id"]} .inc').nth(1).uncheck()
        if c_ren:
            pg.locator(f'#{c_ren["id"]} .toggle-edit').first.click()
            pg.locator(f'#{c_ren["id"]} .editor textarea').first.fill('SYMBOL-BY-TEST')
        target = c_sug or c_edit
        pg.fill(f'#note-{target["id"]}', 'TEST-NOTE first line\nsecond line')
        pg.select_option(f'#decision-{target["id"]}', 'Apply' if target is c_sug else 'Apply with edits')
        pg.wait_for_timeout(900)
        if c_edit:
            check('edited card becomes Apply with edits', pg.input_value(f'#decision-{c_edit["id"]}') == 'Apply with edits')
        pg.click('#save-md')
        pg.wait_for_timeout(800)
        md = instr.read_text(encoding='utf-8') if instr.exists() else ''
        check('instructions written', md.startswith('# '))
        check('note in the instructions', 'TEST-NOTE first line' in md)
        if c_edit:
            check('edited text marked', 'EDITED-BY-TEST' in section(md, c_edit['id']) and 'NEW (edited by the reviewer)' in section(md, c_edit['id']))
        if c_multi and c_multi is not c_edit:
            sec = section(md, c_multi['id'])
            check('unticked edit not applied', '\u2014 not applied' in sec and sec.count('\u2014 apply') == len(c_multi['edits']) - 1)
        if c_ren:
            check('changed symbol marked', 'NEW symbol (edited by the reviewer)' in section(md, c_ren['id']) and 'SYMBOL-BY-TEST' in section(md, c_ren['id']))
        pg.reload()
        pg.wait_for_selector('article.item')
        pg.wait_for_timeout(600)
        check('reload keeps the note', 'TEST-NOTE' in pg.input_value(f'#note-{target["id"]}'))
        if c_multi and c_multi is not c_edit:
            check('reload keeps the unticked edit', not pg.locator(f'#{c_multi["id"]} .inc').nth(1).is_checked())
        if args.shots:
            shots = Path(args.shots)
            shots.mkdir(parents=True, exist_ok=True)
            pg.evaluate('window.scrollTo(0, 0)')
            pg.screenshot(path=str(shots / 'top.png'))
            pg.locator(f'#{(c_edit or items[0])["id"]}').scroll_into_view_if_needed()
            pg.screenshot(path=str(shots / 'edit_card.png'))
            pg.locator(f'#{(c_ren or c_sug or items[-1])["id"]}').scroll_into_view_if_needed()
            pg.screenshot(path=str(shots / 'other_card.png'))
        pg.close()
        time.sleep(0.8)
        # A fresh start: accept everything, save, and re-apply the saved instructions.
        (T / names['decisions']).unlink(missing_ok=True)
        instr.unlink(missing_ok=True)
        pg = page()
        pg.click('#accept-rest')
        pg.wait_for_timeout(300)
        pg.click('#accept-rest')
        pg.wait_for_timeout(800)
        pg.click('#save-md')
        pg.wait_for_timeout(800)
        check('no page error', not errors, '; '.join(errors[:3]))
        b.close()
finally:
    srv.terminate()

out = T / 'reapplied.out'
run = subprocess.run([sys.executable, str(T / 'apply_instructions.py'), str(instr), str(manuscript), str(T / names['review']), str(out)],
                     capture_output=True, text=True)
check('applier runs on the saved instructions', run.returncode == 0, run.stderr.strip()[:300])
same = out.exists() and out.read_bytes() == (T / names['proposal']).read_bytes()
check('instructions re-applied reproduce the proposal', same, f'edits: {meta["n_edits"]}, renames: {meta["n_renames"]}')
print('ALL PASS' if ok else 'SOME FAILED')
if ok and not args.keep:
    shutil.rmtree(T, ignore_errors=True)
else:
    print('Test folder kept:', T)
sys.exit(0 if ok else 1)
