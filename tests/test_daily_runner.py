from __future__ import annotations
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from school_os.daily import DailyError,PHASES,run_daily  # noqa:E402
class DailyRunnerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.schema=json.loads((ROOT/'schemas/capability-profile.schema.json').read_text());cls.template=json.loads((ROOT/'templates/state/capability-profile.json').read_text())
 def profile(self,entrypoint):
  p=copy.deepcopy(self.template);p['execution_surface']=entrypoint;p['authentication']['status']='available';p['conformant_operations']=['daily-run']
  for name in p['network_paths']:p['network_paths'][name]['status']='available' if name!='scheduler' or entrypoint=='scheduled' else 'not_required'
  for name in p['observations']:p['observations'][name]['status']='available'
  p['capabilities']=[{'capability_id':x,'status':'available','verification':{},'degradation':'stop_before_side_effects'} for x in ('storage.read_complete','mail.search','tasks.list_complete')]
  if entrypoint=='scheduled':p['capabilities'] += [{'capability_id':x,'status':'available','verification':{},'degradation':'stop_before_side_effects'} for x in ('scheduler.inspect','scheduler.verify')];p['selected_adapters']['scheduler']='synthetic';p['scheduler_behavior']={}
  return p
 def stages(self):
  seen=[]
  return {phase:(lambda previous,phase=phase: (seen.append((phase,previous.get('phase'))),{'verified':True,'phase':phase})[1]) for phase in PHASES},seen
 def test_manual_runs_all_phases_without_scheduler(self):
  stages,seen=self.stages();result=run_daily(profile=self.profile('manual'),capability_schema=self.schema,entrypoint='manual',operation_id='daily-001',attempt_id='attempt-001',stages=stages)
  self.assertEqual('COMPLETE',result.outcome);self.assertEqual(list(PHASES),[x[0] for x in seen]);self.assertNotIn('scheduler',str(result.outputs))
 def test_scheduled_uses_same_runner_and_requires_admission(self):
  stages,_=self.stages()
  with self.assertRaisesRegex(DailyError,'scheduler admission'):run_daily(profile=self.profile('scheduled'),capability_schema=self.schema,entrypoint='scheduled',operation_id='daily-001',attempt_id='attempt-001',stages=stages)
  self.assertEqual('scheduled',run_daily(profile=self.profile('scheduled'),capability_schema=self.schema,entrypoint='scheduled',operation_id='daily-001',attempt_id='attempt-001',stages=stages,scheduler_admission=lambda:True).entrypoint)
 def test_runner_rejects_unverified_or_missing_phase(self):
  stages,_=self.stages();stages['catalog']=lambda _:{'verified':False}
  with self.assertRaisesRegex(DailyError,'not verified: catalog'):run_daily(profile=self.profile('manual'),capability_schema=self.schema,entrypoint='manual',operation_id='daily-001',attempt_id='attempt-001',stages=stages)
  del stages['catalog']
  with self.assertRaisesRegex(DailyError,'missing required daily phase: catalog'):run_daily(profile=self.profile('manual'),capability_schema=self.schema,entrypoint='manual',operation_id='daily-001',attempt_id='attempt-001',stages=stages)
 def test_planned_pause_and_resumption_use_durable_predecessor_output(self):
  stages,seen=self.stages(); checkpoints=[]
  paused=run_daily(profile=self.profile('manual'),capability_schema=self.schema,entrypoint='manual',operation_id='daily-001',attempt_id='attempt-001',stages=stages,stop_after='catalog',checkpoint=lambda phase,result,outcome: checkpoints.append((phase,result)) or f'checkpoint-{phase}')
  self.assertEqual('NEEDS_CONTINUATION',paused.outcome);self.assertEqual('catalog',paused.current_phase);self.assertEqual('checkpoint-catalog',paused.checkpoint_reference)
  resumed=run_daily(profile=self.profile('manual'),capability_schema=self.schema,entrypoint='manual',operation_id='daily-001',attempt_id='attempt-002',stages=stages,resume_after='catalog',durable_predecessor_output=checkpoints[-1][1])
  self.assertEqual('COMPLETE',resumed.outcome);self.assertEqual('reconcile',seen[-4][0])
if __name__=='__main__':unittest.main()
