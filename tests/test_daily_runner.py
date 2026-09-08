from __future__ import annotations
import copy,json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from school_os.daily import DailyError,PHASES,run_daily  # noqa:E402
class DailyRunnerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.schema=json.loads((ROOT/'schemas/capability-profile.schema.json').read_text());cls.template=json.loads((ROOT/'templates/state/capability-profile.json').read_text())
 def profile(self,entrypoint):
  p=copy.deepcopy(self.template);p['execution_surface']=entrypoint;p['evidence_class']='observed' if entrypoint=='scheduled' else 'synthetic';p['authentication']['status']='available';p['conformant_operations']=['daily-run']
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
 def test_stale_auth_capacity_and_resumed_non_progress_block(self):
  from school_os.capabilities import CapabilityError,qualify_execution
  stale=self.profile('manual');stale['authentication']['status']='unavailable'
  with self.assertRaisesRegex(CapabilityError,'authentication'):qualify_execution(stale,self.schema,operation='daily-run',entrypoint='manual')
  plan=qualify_execution(self.profile('manual'),self.schema,operation='daily-run',entrypoint='manual',requested_records=99,requested_bytes=999999)
  self.assertEqual(1,plan.max_records_per_unit);self.assertEqual(65536,plan.max_bytes_per_unit)
  stages,_=self.stages();stages['reconcile']=lambda _:{'verified':True,'progressed':False}
  with self.assertRaisesRegex(DailyError,'made no progress'):run_daily(profile=self.profile('manual'),capability_schema=self.schema,entrypoint='manual',operation_id='daily-001',attempt_id='attempt-002',stages=stages,resume_after='catalog',durable_predecessor_output={'verified':True,'phase':'catalog'},require_progress_after_resume=True)
 def test_no_new_message_run_still_regenerates_required_outputs(self):
  stages,seen=self.stages()
  stages['discover']=lambda _:{'verified':True,'new_conversations':0}
  stages['reconcile']=lambda previous: seen.append(('reconcile',previous)) or {'verified':True,'rolling_regenerated':True}
  stages['brief_delivery']=lambda previous: seen.append(('brief_delivery',previous)) or {'verified':True,'brief_regenerated':True}
  result=run_daily(profile=self.profile('manual'),capability_schema=self.schema,entrypoint='manual',operation_id='daily-empty-001',attempt_id='attempt-001',stages=stages)
  self.assertEqual('COMPLETE',result.outcome);self.assertTrue(result.outputs['reconcile']['rolling_regenerated']);self.assertTrue(result.outputs['brief_delivery']['brief_regenerated']);self.assertEqual(['reconcile','brief_delivery'],[phase for phase,_ in seen if phase in {'reconcile','brief_delivery'}])
 def test_measured_budget_stops_before_next_phase_and_resumes(self):
  stages,_=self.stages(); checkpoints=[]
  paused=run_daily(profile=self.profile('manual'),capability_schema=self.schema,entrypoint='manual',operation_id='daily-budget',attempt_id='attempt-1',stages=stages,max_elapsed_ms=4,estimated_phase_ms={'preflight':1,'discover':1,'catalog':4},monotonic_clock=lambda:0.0,checkpoint=lambda phase,result,outcome:checkpoints.append((phase,result,outcome)) or phase)
  self.assertEqual('NEEDS_CONTINUATION',paused.outcome);self.assertEqual('discover',paused.current_phase);self.assertEqual('needs_continuation',checkpoints[-1][2])
  resumed=run_daily(profile=self.profile('manual'),capability_schema=self.schema,entrypoint='manual',operation_id='daily-budget',attempt_id='attempt-2',stages=stages,resume_after='discover',durable_predecessor_output=checkpoints[-1][1])
  self.assertEqual('COMPLETE',resumed.outcome)
 def test_budget_counts_admission_and_checkpoint_elapsed(self):
  stages,seen=self.stages(); admission_times=iter((0.0,0.004))
  with self.assertRaisesRegex(DailyError,'cannot complete the next minimum unit'):
   run_daily(profile=self.profile('manual'),capability_schema=self.schema,entrypoint='manual',operation_id='daily-budget',attempt_id='attempt-1',stages=stages,max_elapsed_ms=5,estimated_phase_ms={'preflight':1},monotonic_clock=lambda:next(admission_times))
  self.assertEqual([],seen)
  stages,seen=self.stages(); clock=[0.0]; checkpoints=[]
  def checkpoint(phase,result,outcome):
   checkpoints.append((phase,result,outcome));clock[0] += 0.003;return f'checkpoint-{len(checkpoints)}'
  paused=run_daily(profile=self.profile('manual'),capability_schema=self.schema,entrypoint='manual',operation_id='daily-budget',attempt_id='attempt-1',stages=stages,max_elapsed_ms=6,estimated_phase_ms={'preflight':1,'discover':2},reserve_ms=1,monotonic_clock=lambda:clock[0],checkpoint=checkpoint)
  self.assertEqual('NEEDS_CONTINUATION',paused.outcome);self.assertEqual(['preflight'],[phase for phase,_ in seen]);self.assertEqual('needs_continuation',checkpoints[-1][2])
 def test_budget_validation_rejects_unknown_negative_and_bad_numeric_types(self):
  stages,_=self.stages()
  base=dict(profile=self.profile('manual'),capability_schema=self.schema,entrypoint='manual',operation_id='daily-budget',attempt_id='attempt-1',stages=stages,monotonic_clock=lambda:0.0)
  for value in (True,0,-1,1.5,'5'):
   with self.subTest(max_elapsed_ms=value),self.assertRaisesRegex(DailyError,'elapsed budget must be a positive integer'):
    run_daily(**base,max_elapsed_ms=value,estimated_phase_ms={'preflight':1})
  for value in (True,-1,1.5,'1'):
   with self.subTest(reserve_ms=value),self.assertRaisesRegex(DailyError,'budget reserve must be a nonnegative integer'):
    run_daily(**base,reserve_ms=value)
  with self.assertRaisesRegex(DailyError,'requires a measured next-phase estimate'):
   run_daily(**base,max_elapsed_ms=5,estimated_phase_ms={})
  for value in (True,-1,1.5,'1'):
   with self.subTest(estimated_phase_ms=value),self.assertRaisesRegex(DailyError,'phase estimate must be a nonnegative integer'):
    run_daily(**base,max_elapsed_ms=5,estimated_phase_ms={'preflight':value})
 def test_budget_and_planned_boundaries_require_durable_checkpoint(self):
  stages,_=self.stages();base=dict(profile=self.profile('manual'),capability_schema=self.schema,entrypoint='manual',operation_id='daily-budget',attempt_id='attempt-1',stages=stages)
  with self.assertRaisesRegex(DailyError,'requires a durable checkpoint'):
   run_daily(**base,max_elapsed_ms=2,estimated_phase_ms={'preflight':0,'discover':2},monotonic_clock=lambda:0.0)
  with self.assertRaisesRegex(DailyError,'requires a durable checkpoint reference'):
   run_daily(**base,stop_after='preflight',checkpoint=lambda _phase,_result,_outcome:None)
 def test_resumed_budget_preserves_history_without_replaying_predecessors(self):
  stages,seen=self.stages();checkpoints=[]
  paused=run_daily(profile=self.profile('manual'),capability_schema=self.schema,entrypoint='manual',operation_id='daily-resume',attempt_id='attempt-2',stages=stages,resume_after='discover',durable_predecessor_output={'verified':True,'phase':'discover'},max_elapsed_ms=3,estimated_phase_ms={'catalog':1,'reconcile':3},monotonic_clock=lambda:0.0,checkpoint=lambda phase,result,outcome:checkpoints.append((phase,result,outcome)) or f'checkpoint-{phase}-{outcome}')
  self.assertEqual(('preflight','discover','catalog'),paused.completed_phases);self.assertEqual(['catalog'],[phase for phase,_ in seen])
  resumed=run_daily(profile=self.profile('manual'),capability_schema=self.schema,entrypoint='manual',operation_id='daily-resume',attempt_id='attempt-3',stages=stages,resume_after='catalog',durable_predecessor_output=checkpoints[-1][1])
  self.assertEqual('COMPLETE',resumed.outcome);self.assertEqual(list(PHASES[2:]),[phase for phase,_ in seen]);self.assertEqual(PHASES,resumed.completed_phases)
  with self.assertRaisesRegex(DailyError,'verified durable predecessor output'):
   run_daily(profile=self.profile('manual'),capability_schema=self.schema,entrypoint='manual',operation_id='daily-resume',attempt_id='attempt-3',stages=stages,resume_after='catalog',durable_predecessor_output={'verified':False})
 def test_measurement_command_executes_paths_and_records_scope(self):
  execution=subprocess.run([sys.executable,str(ROOT/'scripts/measure_synthetic.py')],cwd=ROOT,capture_output=True,text=True,check=False)
  self.assertEqual(0,execution.returncode,execution.stderr)
  baseline=json.loads(execution.stdout)
  operations={item['name']:item for item in baseline['operations']}
  self.assertEqual({'onboarding','bounded_import','daily_update','no_new_message','interrupted','fresh_attempt_resume'},set(operations))
  self.assertIsNone(baseline['unavailable']['model_tokens']);self.assertIsNone(baseline['unavailable']['host_deadline_ns']);self.assertIn('does not establish observed runtime or provider conformance',baseline['evidence_scope'])
  for name in ('daily_update','no_new_message'):
   self.assertEqual('COMPLETE',operations[name]['result']['outcome']);self.assertEqual(list(PHASES),operations[name]['completed_units']);self.assertGreater(operations[name]['provider_fake_calls'],0)
  self.assertEqual(1,operations['daily_update']['helper_calls']['importer.admit_exact_plaintext_representation']);self.assertEqual(1,operations['daily_update']['helper_calls']['catalog.build_catalog_message'])
  self.assertEqual(1,operations['daily_update']['result']['phase_evidence']['task_sync']['canonical_provider_bindings'])
  self.assertEqual(2,operations['daily_update']['helper_calls']['tasks.reconcile_provider_tasks']);self.assertEqual(1,operations['daily_update']['helper_calls']['provider_fake.tasks.create'])
  self.assertNotIn('provider_fake.tasks.create',operations['no_new_message']['helper_calls'])
  self.assertEqual(0,operations['no_new_message']['result']['phase_evidence']['discover']['new_conversations'])
  self.assertEqual('NEEDS_CONTINUATION',operations['interrupted']['result']['outcome']);self.assertEqual('COMPLETE',operations['fresh_attempt_resume']['result']['outcome']);self.assertEqual([],operations['fresh_attempt_resume']['repeated_units']);self.assertIn('same-process continuation under a new attempt ID',operations['fresh_attempt_resume']['evidence_scope'])
if __name__=='__main__':unittest.main()
