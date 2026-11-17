#!/usr/bin/env python3
"""Offline campaign ledger. No networking, credentials, browser control or media generation."""
import argparse
import hashlib
import html
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

CHANNELS = ('Facebook', 'Reddit', 'TikTok', 'YouTube', 'X', 'Instagram', 'LinkedIn')
STATUSES = {'content_candidate', 'assets_waiting_manual', 'editor_ready_unpublished',
            'submitted_processing', 'submission_unknown', 'manager_verified',
            'account_post_verified', 'public_verified', 'blocked', 'cancelled_by_user'}
VERIFY = {'manager_verified', 'account_post_verified', 'public_verified'}
READY = ('accountVerified', 'destinationVerified', 'rulesRead', 'duplicatesChecked',
         'mediaVerified', 'copyVerified', 'previewVerified', 'disclosuresResolved', 'reviewPassed')

class Invalid(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise Invalid(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def write_new(path, obj):
    with Path(path).open('x', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

def nonempty(value):
    return isinstance(value, str) and bool(value.strip())

def safe_file(root, rel):
    require(nonempty(rel) and '\\' not in rel, 'Use a nonempty relative POSIX path')
    p = Path(rel)
    require(not p.is_absolute() and '..' not in p.parts and ':' not in rel,
            'Path must stay inside campaign')
    candidate = root / p
    require(candidate.resolve().is_relative_to(root.resolve()), 'Path escapes campaign')
    require(candidate.is_file() and not candidate.is_symlink(), 'Evidence file missing or symlinked')
    return candidate

def validate_brief(b):
    require(isinstance(b, dict) and b.get('schemaVersion') == 1, 'Unsupported brief schema')
    require(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', b.get('campaignId', '')) is not None,
            'campaignId must be lowercase kebab-case')
    for k in ('goal', 'audience', 'language', 'cta'):
        require(nonempty(b.get(k)), 'Missing brief field: ' + k)
    require(b.get('evidenceMode') in ('real', 'synthetic'), 'evidenceMode must be real or synthetic')
    channels = b.get('channels')
    require(isinstance(channels, list) and channels and len(channels) == len(set(channels)),
            'Channels must be a nonempty unique list')
    require(all(c in CHANNELS for c in channels), 'Unknown channel')
    permissions = b.get('permissions', {})
    require(isinstance(permissions, dict) and set(permissions) == set(channels), 'Permissions must cover selected channels exactly')
    for c in channels:
        p = permissions[c]
        require(isinstance(p, dict) and type(p.get('prepareEditor')) is bool, 'prepareEditor must be boolean')
        require(p.get('submitActor') in ('none', 'user', 'assistant'), 'Invalid submitActor')
        if p['prepareEditor'] or p['submitActor'] != 'none':
            require(nonempty(p.get('authorizationSource')), 'External permission needs authorizationSource')
    require(isinstance(b.get('facts'), list) and b['facts'], 'At least one sourced fact is required')
    for f in b['facts']:
        require(isinstance(f, dict) and nonempty(f.get('claim')) and nonempty(f.get('source')), 'Invalid fact')
    require(isinstance(b.get('unknowns'), list), 'unknowns must be a list')

def evidence(root, event):
    entries = event.get('evidence')
    require(isinstance(entries, list) and entries, 'Every event needs actual local evidence')
    for item in entries:
        require(isinstance(item, dict), 'Evidence item must be an object')
        p = safe_file(root, item.get('path'))
        require(item.get('sha256') == sha(p.read_bytes()), 'Evidence hash mismatch: ' + str(item.get('path')))

def validate_event(root, brief, channel, history, event):
    require(isinstance(event, dict), 'Event must be an object')
    require(nonempty(event.get('id')) and event['id'] not in {e['id'] for e in history}, 'Event ID missing or duplicated')
    require(event.get('status') in STATUSES, 'Unknown status')
    require(nonempty(event.get('summary')), 'Summary required')
    try:
        stamp = datetime.fromisoformat(event.get('at', '').replace('Z', '+00:00'))
        require(stamp.tzinfo is not None, 'Event timestamp needs timezone')
    except (ValueError, TypeError):
        raise Invalid('Invalid event timestamp') from None
    require(event.get('actor') in ('none', 'user', 'assistant'), 'Invalid event actor')
    evidence(root, event)
    checks = event.get('checks', {})
    require(isinstance(checks, dict), 'checks must be an object')
    status = event['status']
    prev = history[-1]['status'] if history else 'queued'
    require(prev != 'cancelled_by_user', 'Cancelled channel cannot be silently resumed; use a new reviewed campaign')
    perm = brief['permissions'][channel]
    if prev == 'submission_unknown' and status not in ('blocked', 'submission_unknown', 'cancelled_by_user'):
        require(checks.get('reconciledPriorAttempt') is True, 'Reconcile unknown submission before proceeding')
    if status == 'editor_ready_unpublished':
        require(perm['prepareEditor'], 'Editor preparation is not authorized')
        require(all(checks.get(k) is True for k in READY), 'Editor-ready checks are incomplete')
        require(prev not in VERIFY | {'submitted_processing'}, 'Re-editing a submitted post needs a new scoped campaign')
    if status in ('submitted_processing', 'submission_unknown'):
        require(perm['submitActor'] == event['actor'] and event['actor'] != 'none', 'Submit actor is not authorized')
        require(prev == 'editor_ready_unpublished' or
                (prev == 'submission_unknown' and checks.get('reconciledPriorAttempt') is True),
                'Submission requires a ready editor or reconciled prior attempt')
    past_submission = any(e['status'] in VERIFY | {'submitted_processing', 'submission_unknown'} for e in history)
    if past_submission and status in ('content_candidate', 'assets_waiting_manual'):
        raise Invalid('Prior submission exists; reconcile it instead of restarting local stages')
    if status in VERIFY:
        require(prev in VERIFY | {'submitted_processing', 'submission_unknown'} or
                (prev == 'blocked' and past_submission and checks.get('reconciledPriorAttempt') is True),
                'Verification needs an observed submission stage or reconciled blocked attempt')
        key = {'manager_verified': 'managerRecordVerified', 'account_post_verified': 'accountPostVerified',
               'public_verified': 'publicPageVerified'}[status]
        require(checks.get(key) is True, 'Missing layer-specific verification')
        require(nonempty(event.get('postId')), 'Verified post needs its actual postId')
        if status == 'public_verified':
            require(nonempty(event.get('url')) and event['url'].startswith('https://'), 'Public verification needs an HTTPS URL')
    if status in ('blocked', 'cancelled_by_user', 'assets_waiting_manual'):
        require(nonempty(event.get('nextAction')), 'Blocked/cancelled/manual status needs an explicit nextAction')
    if status == 'cancelled_by_user':
        require(event['actor'] == 'user', 'Cancellation must cite a user decision')
    if prev in VERIFY and status not in VERIFY | {'blocked', 'cancelled_by_user'}:
        raise Invalid('Cannot silently downgrade a verified post')
    # A known submission must not be relabeled local candidate and submitted twice.
    if prev == 'submitted_processing' and status not in VERIFY | {'submission_unknown', 'blocked', 'cancelled_by_user'}:
        raise Invalid('Submitted post must be reconciled, not recreated')
    if prev == 'blocked' and any(e['status'] in VERIFY | {'submitted_processing', 'submission_unknown'} for e in history):
        if status == 'editor_ready_unpublished':
            require(checks.get('reconciledPriorAttempt') is True, 'Blocked prior submission needs reconciliation')
            require(checks.get('priorAttemptNotPublished') is True, 'Confirm prior attempt was not published before preparing a retry')
    if prev == 'submission_unknown' and status == 'editor_ready_unpublished':
        require(checks.get('priorAttemptNotPublished') is True, 'Unknown attempt must be confirmed not published before retry')

def init(brief_path, root):
    brief = read_json(brief_path)
    validate_brief(brief)
    root = Path(root)
    root.mkdir(parents=True, exist_ok=False)
    (root/'input').mkdir()
    (root/'work'/'evidence').mkdir(parents=True)
    (root/'output').mkdir()
    (root/'brief.json').write_bytes(canonical(brief) + b'\n')
    state = {'schemaVersion': 1, 'campaignId': brief['campaignId'],
             'briefSha256': sha((root/'brief.json').read_bytes()),
             'channels': {c: {'status': 'queued', 'events': []} for c in brief['channels']}}
    write_new(root/'state.json', state)
    return state

def load(root):
    root = Path(root)
    # The state/brief themselves must also stay in the selected directory.
    bp = safe_file(root, 'brief.json'); sp = safe_file(root, 'state.json')
    brief = read_json(bp); state = read_json(sp)
    validate_brief(brief)
    require(state.get('schemaVersion') == 1 and state.get('campaignId') == brief['campaignId'], 'State/brief mismatch')
    require(state.get('briefSha256') == sha(bp.read_bytes()), 'Brief changed; do not rebase existing events silently')
    require(set(state.get('channels', {})) == set(brief['channels']), 'Channel set changed')
    ids = set()
    for channel in brief['channels']:
        record = state['channels'][channel]
        require(isinstance(record.get('events'), list), 'events must be a list')
        history = []; previous = None
        for stored in record['events']:
            event = {k:v for k,v in stored.items() if k not in ('eventSha256', 'previousEventSha256')}
            require(stored.get('previousEventSha256') == previous, 'Event chain mismatch')
            expected = sha(canonical({'previousEventSha256': previous, 'event': event}))
            require(stored.get('eventSha256') == expected, 'Event bytes changed')
            validate_event(root, brief, channel, history, event)
            require(event['id'] not in ids, 'Event ID duplicated across campaign')
            ids.add(event['id']); history.append(event); previous = expected
        require(record.get('status') == (history[-1]['status'] if history else 'queued'), 'Latest status mismatch')
    return brief, state

def record(root, channel, event):
    root = Path(root)
    lock = root/'.writer.lock'
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise Invalid('Another writer or unresolved writer lock exists') from None
    try:
        os.close(fd)
        brief, state = load(root)
        require(channel in state['channels'], 'Channel not selected')
        require(not ({'eventSha256', 'previousEventSha256'} & set(event)), 'Hash-chain fields are reserved')
        require(not any(e['id'] == event.get('id') for c in state['channels'].values() for e in c['events']), 'Duplicate event ID')
        events = state['channels'][channel]['events']
        validate_event(root, brief, channel, events, event)
        previous = events[-1]['eventSha256'] if events else None
        stored = dict(event, previousEventSha256=previous,
                      eventSha256=sha(canonical({'previousEventSha256': previous, 'event': event})))
        events.append(stored)
        state['channels'][channel]['status'] = event['status']
        temp = root/'.state-next.json'
        require(not temp.exists(), 'Unresolved state temp file; inspect it before retry')
        write_new(temp, state)
        os.replace(temp, root/'state.json')
        return state
    finally:
        lock.unlink()

def report(root, out):
    brief, state = load(root)
    rows = []
    for channel in brief['channels']:
        c = state['channels'][channel]
        e = c['events'][-1] if c['events'] else {}
        rows.append((channel, c['status'], e.get('summary', 'Not started'), e.get('nextAction', 'Review next required stage')))
    mode = brief['evidenceMode']
    title = 'Campaign: ' + brief['campaignId']
    notice = ('SYNTHETIC OFFLINE DEMO: no real media, account, upload or publication was verified.' if mode == 'synthetic'
              else 'Local records require human evidence review; helper validation does not prove live publication.')
    md = '# '+title+'\n\n'+notice+'\n\nGoal: '+brief['goal']+'\n\n'
    md += '| Channel | Status | Evidence-based summary | Next action |\n|---|---|---|---|\n'
    def cell(s): return str(s).replace('|', '\\|').replace('\n', ' ')
    md += ''.join('| '+' | '.join(cell(v) for v in row)+' |\n' for row in rows)
    esc = lambda x: html.escape(str(x), quote=True)
    cards = ''.join('<article><h2>'+esc(r[0])+'</h2><p class="status">'+esc(r[1])+'</p><p>'+esc(r[2])+'</p><p><b>Next:</b> '+esc(r[3])+'</p></article>' for r in rows)
    detail = html.escape(json.dumps(state, ensure_ascii=False, indent=2))
    page = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    page += '<title>'+esc(title)+'</title><style>body{font:16px/1.6 system-ui,sans-serif;margin:0;background:#f2f5f8;color:#182639}main{max-width:1100px;margin:auto;padding:28px}h1{line-height:1.25}aside,article{background:white;padding:20px;border-radius:12px;border:1px solid #d9e1eb}aside{border-left:5px solid #b87915}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;margin:24px 0}.status{font-family:monospace;overflow-wrap:anywhere;color:#204d78}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}details{background:white;padding:20px;border-radius:12px}h2{margin:0}*{box-sizing:border-box}</style>'
    page += '<main><h1>'+esc(title)+'</h1><aside>'+esc(notice)+'</aside><p>'+esc(brief['goal'])+'</p><section class="grid">'+cards+'</section><details><summary>Evidence ledger (local paths and hashes)</summary><pre>'+detail+'</pre></details></main></html>\n'
    out = Path(out); out.mkdir(parents=True, exist_ok=False)
    (out/'report.md').write_text(md, encoding='utf-8')
    (out/'report.html').write_text(page, encoding='utf-8')
    return {'campaignId': brief['campaignId'], 'evidenceMode': mode, 'channels': len(rows),
            'realPublicationVerifiedByScript': False, 'output': str(out)}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='action', required=True)
    p = sub.add_parser('init'); p.add_argument('--brief', required=True, type=Path); p.add_argument('--out', required=True, type=Path)
    p = sub.add_parser('validate'); p.add_argument('--campaign', required=True, type=Path)
    p = sub.add_parser('record'); p.add_argument('--campaign', required=True, type=Path); p.add_argument('--channel', required=True); p.add_argument('--event', required=True, type=Path)
    p = sub.add_parser('report'); p.add_argument('--campaign', required=True, type=Path); p.add_argument('--out', required=True, type=Path)
    a = ap.parse_args()
    try:
        if a.action == 'init':
            init(a.brief, a.out); result = {'initialized': str(a.out), 'externalActions': False}
        elif a.action == 'validate':
            b, s = load(a.campaign); result = {'valid': True, 'campaignId': b['campaignId'], 'evidenceMode': b['evidenceMode'], 'events': sum(len(c['events']) for c in s['channels'].values()), 'liveSemanticsVerified': False}
        elif a.action == 'record':
            record(a.campaign, a.channel, read_json(a.event)); result = {'recorded': True, 'externalActions': False}
        else:
            result = report(a.campaign, a.out)
        print(json.dumps(result, ensure_ascii=False))
    except (Invalid, OSError, ValueError, TypeError, KeyError, AttributeError) as e:
        print('ERROR: '+str(e), file=sys.stderr)
        return 2
    return 0

if __name__ == '__main__':
    sys.exit(main())
