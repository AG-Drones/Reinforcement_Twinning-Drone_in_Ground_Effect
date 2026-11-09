"""Apply the instructions saved from a review dashboard to the manuscript.

  python apply_instructions.py INSTRUCTIONS.md MANUSCRIPT REVIEW.json OUT [--allow-changed]

Applies every edit marked "apply" (each OLD block must occur exactly once), then the renames of the cards marked
Apply, in card order. Writes OUT and prints a summary in Markdown: what was applied, and everything that needs a
person: notes, suggestion cards, bibliography entries, renames whose symbol the author changed, undecided cards.
It never writes over MANUSCRIPT. Python 3, no packages.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


def parse(md):
    """Read the instructions line by line, so that a heading-like line inside a fenced block is not a heading.

    Returns one dict per card: id, title, status, note, reply, and its sections (each '### ...' heading with the
    fenced blocks that follow it, as (language, text) pairs)."""
    cards, card, sec, fence, buf, field = [], None, None, None, [], None
    for line in md.split('\n'):
        if fence:
            if line == fence[0]:
                sec['fences'].append((fence[1], '\n'.join(buf)))
                fence = None
            else:
                buf.append(line)
            continue
        head = re.match(r'## (C\d+) \u00b7 (.*) \u2014 ([^\u2014]+)$', line)
        if head:
            card = {'id': head.group(1), 'title': head.group(2), 'status': head.group(3).strip(),
                    'note': '', 'reply': '', 'sections': []}
            cards.append(card)
            sec, field = None, None
            continue
        if line.startswith('# '):
            card, sec, field = None, None, None
            continue
        if card is None:
            continue
        if line.startswith('### '):
            sec = {'head': line, 'text': '', 'fences': []}
            card['sections'].append(sec)
            field = None
            continue
        opening = re.match(r'(```|~~~~)(\w*)$', line)
        if opening and sec is None:
            sec = {'head': '', 'text': '', 'fences': []}
            card['sections'].append(sec)
        if opening:
            fence, buf, field = (opening.group(1), opening.group(2)), [], None
            continue
        if line.startswith('**Note:** '):
            field, card['note'] = 'note', line[10:]
        elif line.startswith('**Reply:** '):
            field, card['reply'] = 'reply', line[11:]
        elif re.match(r'(Remarks:|Flag:|Suggestion:|Keep the current|Later;|Undecided;|Also append to )', line):
            field = None
        elif field:
            card[field] += '\n' + line
        if sec is not None:
            sec['text'] += line + '\n'
    for c in cards:
        c['note'], c['reply'] = c['note'].strip(), c['reply'].strip()
    return cards


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('instructions'); ap.add_argument('manuscript'); ap.add_argument('review'); ap.add_argument('out')
    ap.add_argument('--allow-changed', action='store_true',
                    help='the manuscript is not the snapshot: apply what still matches and list what does not')
    a = ap.parse_args()
    md = Path(a.instructions).read_text(encoding='utf-8').replace('\r\n', '\n')
    raw = Path(a.manuscript).read_bytes()
    review = json.loads(Path(a.review).read_text(encoding='utf-8'))
    sha, snap = hashlib.sha256(raw).hexdigest(), review['metadata']['manuscript_hash']
    if f'`{snap}`' not in md:
        sys.exit('The instructions and the review JSON refer to different manuscript snapshots.')
    if sha != snap and not a.allow_changed:
        sys.exit(f'The manuscript has changed since the round was built.\n  now:      {sha}\n  snapshot: {snap}\n'
                 'Diff it against the snapshot first (the author may have edited it), then rerun with --allow-changed.')
    tex = raw.decode('utf-8')
    crlf = '\r\n' in tex
    tex = tex.replace('\r\n', '\n')
    items = {i['id']: i for i in review['items']}
    report = {'applied': [], 'unmatched': [], 'notes': [], 'suggestions': [], 'bib': [], 'manual_renames': [],
              'not_applied': [], 'replies': [], 'rewritten': [], 'left_out': []}
    spans, renames = [], []
    for card in parse(md):
        cid, title, status = card['id'], card['title'], card['status']
        item = items[cid]
        if card['note']:
            report['notes'].append((cid, status, title, card['note']))
        if card['reply']:
            report['replies'].append((cid, card['reply']))
        if item['kind'] == 'instruction':
            report['suggestions'].append((cid, status, title))
            continue
        if status not in ('Apply', 'Apply with edits'):
            report['not_applied'].append((cid, status, title))
            continue
        if item['kind'] == 'rename':
            sec = card['sections'][0] if card['sections'] else None
            if sec and 'edited by the reviewer' in sec['text']:
                report['manual_renames'].append((cid, title, sec['fences'][-1][1]))
            else:
                renames.append(item)
            continue
        n_app = 0
        for sec in card['sections']:
            label = sec['head'][4:].split(' (')[0]
            if sec['head'].endswith('\u2014 not applied'):
                report['left_out'].append((cid, label, title))
            if not sec['head'].endswith('\u2014 apply'):
                continue
            if 'edited by the reviewer' in sec['text']:
                report['rewritten'].append((cid, label, title))
            tex_blocks = [body for lang, body in sec['fences'] if lang != 'bib']
            assert len(tex_blocks) == 2, f'{cid}: cannot read the OLD and NEW blocks'
            old, new = tex_blocks
            new = '' if new == '% (delete the OLD block)' else new
            if tex.count(old) != 1:
                report['unmatched'].append((cid, tex.count(old), old[:100]))
                continue
            s = tex.index(old)
            spans.append((s, s + len(old), new, cid))
            n_app += 1
        for sec in card['sections']:
            report['bib'] += [(cid, body) for lang, body in sec['fences'] if lang == 'bib']
        report['applied'].append((cid, status, n_app))
    spans.sort()
    for (s1, e1, _, c1), (s2, e2, _, c2) in zip(spans, spans[1:]):
        if s2 < e1:
            sys.exit(f'Edits of {c1} and {c2} overlap after the author\'s changes; apply them by hand.')
    out = tex
    for s, e, new, _ in sorted(spans, reverse=True):
        out = out[:s] + new + out[e:]
    places = []
    for item in renames:
        n = 0
        for pat, repl in item['rename']['subs']:
            if item['rename']['regex_repl']:
                out, c = re.subn(pat, repl, out)
            else:
                out, c = re.subn(pat, lambda m, r=repl: r, out)
            n += c
        places.append((item['id'], item['title'], n, item['rename']['count']))
    Path(a.out).write_bytes((out.replace('\n', '\r\n') if crlf else out).encode('utf-8'))
    p = print
    p(f'# Applied {Path(a.instructions).name}\n')
    p(f'- Manuscript: {sha[:12]}... ({"the snapshot" if sha == snap else "NOT the snapshot " + snap[:12] + "..."}).')
    p(f'- Edits applied: {len(spans)}, on cards {", ".join(x[0] for x in report["applied"] if x[2]) or "none"}. '
      f'Renames applied: {len(places)}.')
    p(f'- Written: {a.out} ({hashlib.sha256(Path(a.out).read_bytes()).hexdigest()[:12]}...).\n')
    if report['rewritten']:
        p('## Texts the author rewrote (applied as he wrote them; re-read each one in place)\n')
        for cid, label, title in report['rewritten']:
            p(f'- {cid}, {label}: {title}')
        p()
    if report['left_out']:
        p('## Edits the author left out (not applied)\n')
        for cid, label, title in report['left_out']:
            p(f'- {cid}, {label}: {title}')
        p()
    if report['unmatched']:
        p('## OLD blocks not found exactly once (NOT applied; locate them by hand)\n')
        for cid, n, old in report['unmatched']:
            p(f'- {cid}: found {n} times: `{old}`...')
        p()
    if places:
        p('## Renames\n')
        for cid, title, n, expected in places:
            p(f'- {cid} {title}: {n} place{"" if n == 1 else "s"}' + ('' if n >= expected else f' (the card counted {expected}: check)'))
        p()
    if report['manual_renames']:
        p('## Renames whose symbol the author changed (apply by hand, adapting the substitutions in the review JSON)\n')
        for cid, title, new in report['manual_renames']:
            p(f'- {cid} {title}: new symbol `{new}`')
        p()
    if report['notes']:
        p('## Notes to act on (quote them in the report)\n')
        for cid, status, title, note in report['notes']:
            p(f'- {cid} [{status}] {title}\n  > ' + note.replace('\n', '\n  > '))
        p()
    if report['suggestions']:
        p('## Suggestion cards (follow the note; without a note, Apply means the stated default)\n')
        for cid, status, title in report['suggestions']:
            p(f'- {cid} [{status}] {title}')
        p()
    if report['bib']:
        p('## Bibliography entries to append\n')
        for cid, entry in report['bib']:
            p(f'- {cid}:\n\n```bib\n{entry}\n```')
        p()
    if report['not_applied']:
        p('## Not applied\n')
        for cid, status, title in report['not_applied']:
            p(f'- {cid} [{status}] {title}')
        p()
    if report['replies']:
        p('## Replies written by the author\n')
        for cid, reply in report['replies']:
            p(f'- {cid}: {reply}')


if __name__ == '__main__':
    main()
