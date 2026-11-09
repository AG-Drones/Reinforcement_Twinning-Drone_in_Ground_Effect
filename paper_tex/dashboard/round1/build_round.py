"""Build one review round from cards.py (same folder).

Checks that the manuscript is the snapshot the cards were written against, resolves every OLD block (found
exactly once, no two overlapping), counts the places of every rename, and writes:
  review_<id>.json, review_<id>.html, round.json, and <manuscript>_<id>_proposal (every edit, then every rename).
Python 3, no packages.   Usage: python build_round.py [--note "compile note"] [--sha]
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def pattern(snippet):
    """Regex for a snippet in which any run of whitespace matches any run of whitespace."""
    return re.compile(r'\s+'.join(re.escape(t) for t in snippet.split()))


def line_of(text, pos):
    return text.count('\n', 0, pos) + 1


def compact(lines):
    """[3, 4, 5, 9] -> '3\u20135, 9'."""
    out, i = [], 0
    while i < len(lines):
        j = i
        while j + 1 < len(lines) and lines[j + 1] == lines[j] + 1:
            j += 1
        out.append(str(lines[i]) if i == j else f'{lines[i]}\u2013{lines[j]}')
        i = j + 1
    return ', '.join(out)


def apply_rename(text, ren):
    """Apply the substitutions of a rename; return the new text and the number of places changed."""
    total = 0
    for pat, repl in ren['subs']:
        if ren.get('regex_repl'):
            text, n = re.subn(pat, repl, text)
        else:
            text, n = re.subn(pat, lambda m, r=repl: r, text)
        total += n
    return text, total


def plural(n, word):
    return f'{n} {word}' + ('' if n == 1 else 's')


def junction_warning(tex, s, e, find, new):
    """What an edit would leave behind that its writer probably did not intend."""
    before = tex[s - 1] if s else '\n'
    after = tex[e] if e < len(tex) else '\n'
    if not new.strip():
        if tex[tex.rfind('\n', 0, s) + 1:s].strip() == '' and after == '\n':
            return ('the deletion leaves an empty line; to remove the line too, take the last word of the previous '
                    'line into find and repeat it in new')
        if before in ' \t' and after in ' \t':
            return 'the deletion leaves two spaces; take the word before it into find and repeat it in new'
        if before in ' \t' and after == '\n':
            return 'the deletion leaves a space at the end of the line'
        if before in ' \t' and after in '.,;:)':
            return 'the deletion leaves a space before the punctuation; take the word before it into find and repeat it in new'
    elif (new[-1:] in ' \t' and after in ' \t') or (new[:1] in ' \t' and before in ' \t'):
        return 'new begins or ends with a space next to a space of the manuscript: two spaces'
    elif find != find.strip() and (find[:1].isspace() != new[:1].isspace() or find[-1:].isspace() != new[-1:].isspace()):
        return 'the ends of find are trimmed before matching, so its leading or trailing space is not replaced'
    return ''


def reindent(text, unit):
    """Leading groups of four spaces in a NEW block become the manuscript's own indentation unit."""
    if not unit:
        return text
    out = []
    for line in text.split('\n'):
        n = (len(line) - len(line.lstrip(' '))) // 4
        out.append(unit * n + line[4 * n:])
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--note', default='', help='last line of "Please look at these first", e.g. the compile result')
    ap.add_argument('--sha', action='store_true', help='print the SHA-256 of the manuscript and stop')
    args = ap.parse_args()
    import cards
    R = cards.ROUND
    rid = R['id']
    path = (HERE / R.get('manuscript_path', '../../' + R['manuscript'])).resolve()
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if args.sha:
        print(sha)
        return
    if sha != R.get('snapshot'):
        sys.exit(f'{path.name} is not the snapshot the cards were written against.\n  now:   {sha}\n  cards: {R.get("snapshot")}\n'
                 'Nothing written. Diff the two versions and rebase the cards; do not just replace the hash.')
    tex = raw.decode('utf-8')
    crlf = '\r\n' in tex
    tex = tex.replace('\r\n', '\n')
    width = 3 if len(cards.C) > 99 else 2
    items, spans, warnings = [], [], []
    for n, c in enumerate(cards.C, 1):
        cid = f'C{n:0{width}d}'
        edits = []
        for find, new in c['edits']:
            hits = list(pattern(find).finditer(tex))
            if len(hits) != 1:
                sys.exit(f'{cid} ({c["title"]}): OLD block found {len(hits)} times: {find[:90]!r}')
            m = hits[0]
            a, b = line_of(tex, m.start()), line_of(tex, m.end())
            edits.append({'old': m.group(0), 'new': reindent(new, R.get('indent')), 'lines': str(a) if a == b else f'{a}\u2013{b}'})
            warn = junction_warning(tex, m.start(), m.end(), find, new)
            if warn:
                warnings.append(f'{cid}, edit {len(edits)}: {warn}')
            spans.append((m.start(), m.end(), cid, len(edits) - 1))
        lines = ''
        if c['kind'] == 'edit':
            first = int(edits[0]['lines'].split('\u2013')[0])
            last = max(int(e['lines'].split('\u2013')[-1]) for e in edits)
            lines = str(first) if first == last else f'{first}\u2013{last}'
        rem = [dict(r) for r in c['remarks']]
        items.append({'id': cid, 'group': c['group'], 'title': c['title'], 'lines': lines, 'kind': c['kind'],
                      'grade': c['grade'], 'reviewers': sorted({r['who'] for r in rem}),
                      'remark_ids': [r['rid'] for r in rem], 'remarks': rem, 'why': c['why'],
                      'suggestion': c['suggestion'], 'extra': c['extra'], 'flags': list(c['flags']),
                      'sources': [dict(s) for s in c['sources']], 'edits': edits, 'rename': c['rename']})
    spans.sort()
    for (s1, e1, c1, _), (s2, e2, c2, _) in zip(spans, spans[1:]):
        if s2 < e1:
            sys.exit(f'Overlapping edits: {c1} and {c2}. Merge them into one card or shorten an OLD block.')
    by_id = {i['id']: i for i in items}
    proposal = tex
    for s, e, cid, k in sorted(spans, reverse=True):
        proposal = proposal[:s] + by_id[cid]['edits'][k]['new'] + proposal[e:]
    n_places = 0
    for item in items:
        if item['kind'] != 'rename':
            continue
        ren = item['rename']
        where = sorted({line_of(tex, m.start()) for pat, _ in ren['subs'] for m in re.finditer(pat, tex)})
        proposal, count = apply_rename(proposal, ren)
        if not count:
            sys.exit(f'{item["id"]} ({item["title"]}): the rename matches nothing')
        n_places += count
        item['lines'] = compact(where)
        item['edits'] = [{'old': ren['frm'], 'new': ren['to'],
                          'lines': f'{plural(count, "place")} \u00b7 {"line" if len(where) == 1 else "lines"} {compact(where)}'}]
        item['rename'] = {'subs': [list(s) for s in ren['subs']], 'regex_repl': bool(ren.get('regex_repl')), 'count': count}

    def resolve(text):
        def link(m):
            for i in items:
                if i['title'].startswith(m.group(1)):
                    return f'[[{i["id"]}]]'
            sys.exit(f'Reference to an unknown card: [[t:{m.group(1)}]]')
        return re.sub(r'\[\[t:([^\]]+)\]\]', link, text)
    for i in items:
        i['why'], i['suggestion'] = resolve(i['why']), resolve(i['suggestion'])
        i['flags'] = [resolve(f) for f in i['flags']]
        for r in i['remarks']:
            r['text'] = resolve(r['text'])
    notes = [resolve(x) for x in getattr(cards, 'NOTES', [])] + ([args.note] if args.note.strip() else [])
    stem, suffix = Path(R['manuscript']).stem, Path(R['manuscript']).suffix
    files = {'review': f'review_{rid}.json', 'page': f'review_{rid}.html', 'decisions': f'review_decisions_{rid}.json',
             'instructions': f'review_apply_instructions_{rid}.md', 'proposal': f'{stem}_{rid}_proposal{suffix}',
             'proposal_pdf': f'{stem}_{rid}_proposal.pdf', 'diff_pdf': f'{stem}_{rid}_proposal_diff.pdf'}
    out = proposal.replace('\n', '\r\n') if crlf else proposal
    (HERE / files['proposal']).write_bytes(out.encode('utf-8'))
    groups, grades = {}, {}
    for i in items:
        groups[i['group']] = groups.get(i['group'], 0) + 1
        if i['grade']:
            grades[i['grade']] = grades.get(i['grade'], 0) + 1
    meta = {'id': rid, 'port': int(R.get('port', 8765)), 'label': R.get('label', rid), 'title': R.get('title', 'Review'),
            'intro': R.get('intro', ''), 'manuscript': R['manuscript'], 'manuscript_hash': sha,
            'proposal_hash': hashlib.sha256(out.encode('utf-8')).hexdigest(), 'files': files,
            'typeset': bool(R.get('typeset', suffix == '.tex')), 'typeset_note': R.get('typeset_note', ''),
            'bib': R.get('bib', 'the bibliography file'),
            'grade_labels': R.get('grade_labels', {'A': 'a reader is stuck or misled, a referee requires it, or you asked for it',
                                                   'B': 'should be fixed', 'C': 'cosmetic or optional'}),
            'n_edits': len(spans), 'n_renames': sum(1 for i in items if i['kind'] == 'rename'), 'n_places': n_places,
            'groups': groups, 'grades': grades, 'notes': [x for x in notes if x.strip()]}
    review = {'metadata': meta, 'items': items}
    (HERE / files['review']).write_text(json.dumps(review, ensure_ascii=False, indent=1), encoding='utf-8')
    (HERE / 'round.json').write_text(json.dumps({'id': rid, 'port': meta['port'], **files}, indent=1), encoding='utf-8')
    page = (HERE / 'page_template.html').read_text(encoding='utf-8')
    payload = json.dumps(review, ensure_ascii=False).replace('</', '<\\/')
    (HERE / files['page']).write_text(page.replace('/*REVIEW_JSON*/null', payload), encoding='utf-8')
    kinds = {k: sum(1 for i in items if i['kind'] == k) for k in ('edit', 'rename', 'instruction')}
    print(f'{plural(len(items), "card")}: {kinds["edit"]} with text edits ({plural(len(spans), "edit")}), '
          f'{plural(kinds["rename"], "rename card")} ({plural(n_places, "place")}), {kinds["instruction"]} suggestion only. '
          'OLD blocks unique and non-overlapping.')
    for w in warnings:
        print('WARNING', w)
    print('Wrote', ', '.join([files['review'], files['page'], 'round.json', files['proposal']]))


if __name__ == '__main__':
    main()
