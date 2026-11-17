#!/usr/bin/env python3
"""Synthetic offline contract exercise. Never connects to a platform."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import campaign

def run(out):
    out = Path(out); out.mkdir(parents=True, exist_ok=False)
    source = Path(__file__).resolve().parents[1]/'examples'/'neutral-product'/'brief.json'
    root = out/'campaign'; campaign.init(source, root)
    evidence = root/'work'/'evidence'/'synthetic-observations.txt'
    evidence.write_text('SYNTHETIC fixture only. No account, media, upload, submission or public page was tested.\n', encoding='utf-8')
    counter = 0
    def add(channel, status, actor='none', checks=None, next_action=None):
        nonlocal counter
        counter += 1
        event = {'id': f'demo-{counter:03}', 'at': datetime.now(timezone.utc).isoformat(),
                 'status': status, 'actor': actor, 'summary': 'Synthetic illustration: '+status,
                 'checks': checks or {}, 'evidence': [{'path': 'work/evidence/synthetic-observations.txt', 'sha256': campaign.sha(evidence.read_bytes())}]}
        if next_action: event['nextAction'] = next_action
        if status in campaign.VERIFY: event['postId'] = 'synthetic-post-'+str(counter)
        campaign.record(root, channel, event)
    ready = {k:True for k in campaign.READY}
    for c in campaign.CHANNELS:
        add(c, 'content_candidate')
    for c in ('Facebook', 'Reddit'):
        add(c, 'editor_ready_unpublished', checks=ready)
        add(c, 'submitted_processing', actor='user')
        add(c, 'account_post_verified', checks={'accountPostVerified':True})
    add('TikTok', 'cancelled_by_user', actor='user', next_action='Keep cancellation; no retry.')
    for c in ('YouTube', 'Instagram'):
        add(c, 'editor_ready_unpublished', checks=ready, next_action='User reviews and submits, then verify real outcome.')
    add('X', 'editor_ready_unpublished', checks=ready)
    add('X', 'submission_unknown', actor='user', next_action='Inspect existing post/manager state before any retry.')
    add('LinkedIn', 'assets_waiting_manual', next_action='User selects approved file; then verify preview and disclosure.')
    result = campaign.report(root, out/'report')
    print(json.dumps(result, ensure_ascii=False))
    return result

if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--out',required=True,type=Path)
    try: run(ap.parse_args().out)
    except (OSError, ValueError) as e: ap.exit(2, 'ERROR: '+str(e)+'\n')
