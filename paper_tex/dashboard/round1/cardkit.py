"""Helpers for writing the cards of a review round. cards.py imports them:

    from cardkit import C, card, remark, YOURS
"""

C = []                    # the cards, in page order
YOURS = 'Your wording'    # flag for cards that touch text the author wrote or edited


def remark(rid, who, text, anchor='', status='Open'):
    """One remark that a card answers, quoted word for word.

    rid: identifier shown on the card (R12, S3, I-40, 'You', 'Code'). who: its source ('Referee 1', a co-author's
    name, 'Your remark', 'Notation audit', 'Code check'). anchor: where it was made. status: a short tag."""
    return {'rid': rid, 'who': who, 'anchor': anchor, 'text': text, 'status': status}


def card(group, title, **k):
    """Add a card. Its kind follows from its content:

    edits=[(find, new), ...]   text edits; 'find' must occur exactly once in the manuscript (whitespace-flexible)
    rename={'frm', 'to', 'subs': [(regex, replacement), ...], 'regex_repl': False}   one symbol or word everywhere
    neither                    a suggestion card: a question or options, decided by the author's note
    Other fields: why (proposal text), suggestion, remarks, flags, grade ('A'/'B'/'C' or ''), sources
    ([{'label', 'text'}], reference text shown on the card), extra (a bibliography entry to append)."""
    k.update(group=group, title=title)
    for key, default in (('edits', []), ('flags', []), ('remarks', []), ('sources', []), ('why', ''),
                         ('suggestion', ''), ('grade', ''), ('rename', None), ('extra', '')):
        k.setdefault(key, default if not isinstance(default, list) else list(default))
    k['kind'] = 'rename' if k['rename'] else ('edit' if k['edits'] else 'instruction')
    C.append(k)
