import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import campaign
import demo

class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)
        self.brief=campaign.read_json(Path(__file__).resolve().parents[1]/'examples/neutral-product/brief.json')
        self.bp=self.base/'brief.json'; self.bp.write_text(json.dumps(self.brief),encoding='utf-8')
        self.root=self.base/'campaign'; campaign.init(self.bp,self.root)
        self.ep=self.root/'work/evidence/observation.txt'; self.ep.write_text('Observed fixture',encoding='utf-8')
        self.counter=0

    def event(self,status,**kw):
        self.counter+=1
        e={'id':f'e-{self.counter}', 'at':'2026-01-01T00:00:00+00:00','status':status,'actor':'none',
           'summary':'Observed fixture, not a live account test','checks':{},
           'evidence':[{'path':'work/evidence/observation.txt','sha256':campaign.sha(self.ep.read_bytes())}]}
        e.update(kw); return e

    def add(self,status,**kw):
        campaign.record(self.root,'X',self.event(status,**kw))

    def ready(self):
        self.add('editor_ready_unpublished',checks={k:True for k in campaign.READY})

    def test_fresh_campaign_and_existing_destination(self):
        self.assertEqual(campaign.load(self.root)[1]['channels']['X']['status'],'queued')
        with self.assertRaises(FileExistsError):campaign.init(self.bp,self.root)

    def test_wrong_submitter_rejected_without_mutation(self):
        self.ready(); before=(self.root/'state.json').read_bytes()
        with self.assertRaises(campaign.Invalid):self.add('submitted_processing',actor='assistant')
        self.assertEqual(before,(self.root/'state.json').read_bytes())
        self.assertFalse((self.root/'.writer.lock').exists())

    def test_incomplete_preview_checks(self):
        with self.assertRaises(campaign.Invalid):self.add('editor_ready_unpublished',checks={'mediaVerified':True})

    def test_local_only_permission(self):
        b=copy.deepcopy(self.brief);b['permissions']['X']={'prepareEditor':False,'submitActor':'none'}
        self.bp.write_text(json.dumps(b),encoding='utf-8');r=self.base/'local';campaign.init(self.bp,r)
        ep=r/'work/evidence/observation.txt';ep.write_text('Observed fixture',encoding='utf-8')
        with self.assertRaises(campaign.Invalid):campaign.record(r,'X',self.event('editor_ready_unpublished',checks={k:True for k in campaign.READY}))

    def test_cannot_verify_before_submission(self):
        with self.assertRaises(campaign.Invalid):self.add('public_verified',checks={'publicPageVerified':True},postId='a',url='https://example.invalid/post')

    def test_success_layers_and_public_requirements(self):
        self.ready();self.add('submitted_processing',actor='user')
        self.add('account_post_verified',checks={'accountPostVerified':True},postId='fixture-post')
        with self.assertRaises(campaign.Invalid):self.add('public_verified',checks={'publicPageVerified':True},postId='fixture-post')
        self.add('public_verified',checks={'publicPageVerified':True},postId='fixture-post',url='https://example.invalid/post')
        self.assertEqual(campaign.load(self.root)[1]['channels']['X']['status'],'public_verified')

    def test_unknown_requires_reconciliation(self):
        self.ready();self.add('submission_unknown',actor='user')
        with self.assertRaises(campaign.Invalid):self.add('account_post_verified',checks={'accountPostVerified':True},postId='p')
        self.add('account_post_verified',checks={'accountPostVerified':True,'reconciledPriorAttempt':True},postId='p')

    def test_no_restart_after_submission(self):
        self.ready();self.add('submitted_processing',actor='user');self.add('blocked',nextAction='Inspect prior submission')
        with self.assertRaises(campaign.Invalid):self.add('content_candidate')
        with self.assertRaises(campaign.Invalid):self.ready()
        self.add('editor_ready_unpublished',checks=dict.fromkeys(campaign.READY,True)|{'reconciledPriorAttempt':True,'priorAttemptNotPublished':True})

    def test_unknown_retry_requires_not_published(self):
        self.ready();self.add('submission_unknown',actor='user')
        with self.assertRaises(campaign.Invalid):
            self.add('editor_ready_unpublished',checks=dict.fromkeys(campaign.READY,True)|{'reconciledPriorAttempt':True})
        self.add('editor_ready_unpublished',checks=dict.fromkeys(campaign.READY,True)|{'reconciledPriorAttempt':True,'priorAttemptNotPublished':True})

    def test_blocked_submission_can_reconcile_existing_post(self):
        self.ready();self.add('submitted_processing',actor='user');self.add('blocked',nextAction='Inspect manager record')
        self.add('account_post_verified',postId='p',checks={'accountPostVerified':True,'reconciledPriorAttempt':True})
        self.assertEqual(campaign.load(self.root)[1]['channels']['X']['status'],'account_post_verified')

    def test_cancellation_requires_user_and_stays_cancelled(self):
        with self.assertRaises(campaign.Invalid):self.add('cancelled_by_user',nextAction='No retry')
        self.add('cancelled_by_user',actor='user',nextAction='Keep cancelled')
        with self.assertRaises(campaign.Invalid):self.add('content_candidate')

    def test_evidence_modified_or_missing(self):
        self.add('content_candidate');self.ep.write_text('changed',encoding='utf-8')
        with self.assertRaises(campaign.Invalid):campaign.load(self.root)
        self.ep.unlink()
        with self.assertRaises(campaign.Invalid):campaign.load(self.root)

    def test_path_escape_and_absolute_rejected(self):
        for p in ('../outside.txt','/outside.txt','C:/private.txt','work\\secret.txt'):
            e=self.event('content_candidate');e['evidence'][0]['path']=p
            with self.assertRaises(campaign.Invalid):campaign.record(self.root,'X',e)

    def test_brief_drift_rejected(self):
        p=self.root/'brief.json';b=campaign.read_json(p);b['goal']='changed';p.write_text(json.dumps(b),encoding='utf-8')
        with self.assertRaises(campaign.Invalid):campaign.load(self.root)

    def test_event_chain_tamper_rejected(self):
        self.add('content_candidate');p=self.root/'state.json';s=campaign.read_json(p);s['channels']['X']['events'][0]['summary']='changed';p.write_text(json.dumps(s),encoding='utf-8')
        with self.assertRaises(campaign.Invalid):campaign.load(self.root)

    def test_duplicate_id_rejected(self):
        e=self.event('content_candidate');campaign.record(self.root,'X',e)
        with self.assertRaises(campaign.Invalid):campaign.record(self.root,'Facebook',e)

    def test_active_writer_lock_rejected(self):
        (self.root/'.writer.lock').write_text('test fixture',encoding='utf-8')
        with self.assertRaises(campaign.Invalid):self.add('content_candidate')
        self.assertTrue((self.root/'.writer.lock').exists())

    def test_html_escaping_and_synthetic_disclaimer(self):
        self.add('content_candidate',summary='<script>alert(1)</script>')
        campaign.report(self.root,self.base/'report');p=(self.base/'report/report.html').read_text(encoding='utf-8')
        self.assertNotIn('<script>alert(1)</script>',p)
        self.assertIn('&lt;script&gt;',p);self.assertIn('SYNTHETIC OFFLINE DEMO',p)

    def test_timestamp_needs_timezone(self):
        with self.assertRaises(campaign.Invalid):self.add('content_candidate',at='2026-01-01T00:00:00')

    def test_portable_demo_and_existing_output(self):
        out=self.base/'demo';result=demo.run(out)
        self.assertEqual(result['evidenceMode'],'synthetic');campaign.load(out/'campaign')
        with self.assertRaises(FileExistsError):demo.run(out)

if __name__=='__main__':unittest.main()
