from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from school_os.tasks import TaskError, canonical_task_id, reconcile_canonical_tasks, recover_task_comment, reconcile_provider_tasks  # noqa: E402
from tests.support.fakes import FixtureTasks  # noqa: E402

class ProviderReconciliationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.task_schema=json.loads((ROOT/'schemas/task.schema.json').read_text()); cls.register_schema=json.loads((ROOT/'schemas/canonical-tasks.schema.json').read_text()); cls.state_schema=json.loads((ROOT/'schemas/provider-state.schema.json').read_text());cls.fact_schema=json.loads((ROOT/'schemas/fact.schema.json').read_text())
 def task(self):
  return {"task_id":"task-1","origin":"source","action":"Return form","task_context":"school","entity_scope":"household","workflow_state":"needs_action","owner":None,"source_opened_date":"2026-09-07","last_supporting_source_date":"2026-09-07","source_due":None,"parent_planned_due":None,"source_link":"record-1#fact-1","source_facts":["fact-1"],"latest_progress":None,"provider_bindings":[],"lifecycle_history":[],"projection_state":{},"revision":1,"last_modified_evidence":{}}
 def state(self): return {"provider_id":"synthetic","adapter_id":"synthetic-tasks","provider_revision":None,"bindings":[],"cursor":None,"cursor_evidence":{},"verified_readback":{}}
 def sync(self,provider,register,state):
  return reconcile_provider_tasks(provider,register,state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
 def create_and_sync(self,provider,register,state=None):
  intent=self.sync(provider,register,state or self.state())
  self.assertEqual("create_intent",intent.effects[0]["kind"]);self.assertEqual([],provider.tasks)
  return self.sync(provider,intent.tasks,intent.provider_state)
 def test_pull_first_create_readback_and_binding_preserves_provider_fields(self):
  provider=FixtureTasks(); register={"schema_version":1,"tasks":[self.task()]}
  result=self.create_and_sync(provider,register)
  self.assertEqual(["list","list","create","read"],provider.calls); self.assertEqual("confirmed",result.effects[0]["outcome"]); self.assertEqual("task-1",result.provider_state["bindings"][0]["task_id"])
  provider.tasks[0]["parent_note"]="keep"; result=reconcile_provider_tasks(provider,register,result.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual("keep",provider.tasks[0]["parent_note"]); self.assertEqual(1,len(provider.tasks))
 def test_lost_create_replay_binds_existing_task_and_preserves_parent_title_group(self):
  class LostResponseTasks(FixtureTasks):
   def __init__(self): super().__init__();self.lose=True
   def create_task(self,candidate):
    result=super().create_task(candidate)
    if self.lose: self.lose=False;raise ConnectionError('synthetic lost response')
    return result
  provider=LostResponseTasks();register={"schema_version":1,"tasks":[self.task()]}
  intent=self.sync(provider,register,self.state());unknown=self.sync(provider,intent.tasks,intent.provider_state)
  self.assertEqual(1,len(provider.tasks))
  self.assertEqual("unknown",unknown.provider_state["effect_intents"][0]["outcome"])
  recovered=self.sync(provider,unknown.tasks,unknown.provider_state)
  self.assertEqual(1,len(provider.tasks));self.assertEqual('task-1',recovered.provider_state['bindings'][0]['task_id'])
  provider.tasks[0].update({'title':'Parent title','group':'parent-group','parent_planned_due':'2026-09-10','progress':'done'})
  preserved=reconcile_provider_tasks(provider,register,recovered.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual('Parent title',provider.tasks[0]['title']);self.assertEqual('parent-group',provider.tasks[0]['group']);self.assertEqual('Parent title',preserved.tasks['tasks'][0]['action']);self.assertEqual('parent-group',preserved.tasks['tasks'][0]['entity_scope'])
 def test_unknown_create_does_not_retry_after_one_empty_complete_snapshot(self):
  class InvisibleAfterLostCreate(FixtureTasks):
   def __init__(self): super().__init__();self.first=True;self.hide_next=False
   def list_tasks(self):
    self.calls.append("list")
    if self.hide_next:self.hide_next=False;return []
    return [dict(task) for task in self.tasks]
   def create_task(self,candidate):
    value=super().create_task(candidate)
    if self.first:self.first=False;self.hide_next=True;raise ConnectionError("lost accepted create")
    return value
  provider=InvisibleAfterLostCreate();register={"schema_version":1,"tasks":[self.task()]}
  journaled=self.sync(provider,register,self.state());unknown=self.sync(provider,journaled.tasks,journaled.provider_state)
  self.assertEqual(1,len(provider.tasks));self.assertEqual("unknown",unknown.provider_state["effect_intents"][0]["outcome"])
  with self.assertRaisesRegex(TaskError,"remains unknown"):
   self.sync(provider,unknown.tasks,unknown.provider_state)
  self.assertEqual(1,len(provider.tasks));self.assertEqual(1,provider.calls.count("create"))
  adopted=self.sync(provider,unknown.tasks,unknown.provider_state)
  self.assertEqual(1,len(provider.tasks));self.assertEqual([],adopted.provider_state["effect_intents"]);self.assertEqual("task-1",adopted.provider_state["bindings"][0]["task_id"])
 def test_zero_match_create_retry_requires_explicit_definitely_not_applied(self):
  class DefinitelyAbsentCreate(FixtureTasks):
   def __init__(self): super().__init__();self.first=True
   def create_task(self,candidate):
    if self.first:self.first=False;self.calls.append("create");raise ConnectionError("failed before apply")
    return super().create_task(candidate)
   def reconcile_create_intent(self,intent):
    self.calls.append("reconcile_create")
    return {"outcome":"definitely_not_applied","verification":{"complete_lookup":True,"consistency_window_elapsed":True}}
  provider=DefinitelyAbsentCreate();register={"schema_version":1,"tasks":[self.task()]}
  journaled=self.sync(provider,register,self.state());unknown=self.sync(provider,journaled.tasks,journaled.provider_state)
  retried=self.sync(provider,unknown.tasks,unknown.provider_state)
  self.assertEqual(1,len(provider.tasks));self.assertEqual(2,provider.calls.count("create"));self.assertIn("reconcile_create",provider.calls);self.assertEqual([],retried.provider_state["effect_intents"])
 def test_managed_row_without_binding_or_create_intent_blocks(self):
  provider=FixtureTasks();provider.tasks=[{**{"canonical_task_id":"task-1","origin":"source","title":"Return form","group":"household","description":"school","workflow_state":"needs_action","source_link":"record-1#fact-1","source_due":""},"provider_object_id":"synthetic-task-1"}]
  with self.assertRaisesRegex(TaskError,"durable create intent"):
   self.sync(provider,{"schema_version":1,"tasks":[self.task()]},self.state())
 def test_create_recovery_blocks_conflicting_or_ambiguous_canonical_id_matches(self):
  for variant in ("conflicting","ambiguous"):
   with self.subTest(variant=variant):
    provider=FixtureTasks();register={"schema_version":1,"tasks":[self.task()]};journaled=self.sync(provider,register,self.state());projection=journaled.provider_state["effect_intents"][0]["projection"]
    first={**projection,"provider_object_id":"synthetic-task-1"}
    provider.tasks=[{**first,"title":"Wrong action"}] if variant=="conflicting" else [first,{**projection,"provider_object_id":"synthetic-task-2"}]
    with self.assertRaisesRegex(TaskError,"conflicting provider match|multiple provider tasks"):
     self.sync(provider,journaled.tasks,journaled.provider_state)
    self.assertEqual(0,provider.calls.count("create"))
 def test_lost_update_response_is_adopted_without_a_second_patch(self):
  class LostPatchTasks(FixtureTasks):
   def __init__(self): super().__init__();self.lose=True
   def apply_patch(self,object_id,patch):
    result=super().apply_patch(object_id,patch)
    if self.lose: self.lose=False;raise ConnectionError('synthetic lost patch response')
    return result
  provider=LostPatchTasks();old=self.task();register={"schema_version":1,"tasks":[old]}
  initial=self.create_and_sync(provider,register)
  updated=self.task();updated['task_context']='Revised school context';register={"schema_version":1,"tasks":[updated]}
  with self.assertRaises(ConnectionError):reconcile_provider_tasks(provider,register,initial.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual('Revised school context',provider.tasks[0]['description']);self.assertEqual(1,provider.calls.count('patch'))
  recovered=reconcile_provider_tasks(provider,register,initial.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual(1,provider.calls.count('patch'));self.assertEqual('adopt',recovered.effects[0]['kind']);self.assertEqual((),recovered.review_cases)
 def test_lost_comment_response_is_adopted_without_duplicate(self):
  class LostCommentTasks(FixtureTasks):
   def write_comment(self,object_id,effect_id,text):
    result=super().write_comment(object_id,effect_id,text)
    raise ConnectionError('synthetic lost comment response')
  provider=LostCommentTasks();provider.tasks=[{'provider_object_id':'task-1'}]
  with self.assertRaises(ConnectionError):recover_task_comment(provider,'task-1','comment-1','Parent progress')
  adopted=recover_task_comment(provider,'task-1','comment-1','Parent progress')
  self.assertEqual('Parent progress',adopted['text']);self.assertEqual(1,len(provider.comments))
 def test_completion_requires_comment_and_replay_is_idempotent(self):
  class CompletionTasks(FixtureTasks):
   def apply_parent_state(self,object_id,*,status=None,**_):
    return self.apply_patch(object_id,{"status":status})
  provider=CompletionTasks();register={"schema_version":1,"tasks":[self.task()]}
  initial=self.create_and_sync(provider,register)
  provider.tasks[0].update({"status":"completed","completion_comment":""})
  intent=reconcile_provider_tasks(provider,initial.tasks,initial.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual("completed",provider.tasks[0]["status"]);self.assertEqual(1,len(intent.provider_state["effect_intents"]));self.assertEqual(0,len(provider.comments))
  reopened=reconcile_provider_tasks(provider,intent.tasks,intent.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual("open",provider.tasks[0]["status"]);self.assertEqual(1,len(provider.comments));self.assertEqual("reopened_missing_completion_comment",reopened.tasks["tasks"][0]["lifecycle_history"][0]["kind"])
  replay=reconcile_provider_tasks(provider,reopened.tasks,reopened.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual(1,len(provider.comments));self.assertEqual(1,len(replay.tasks["tasks"][0]["lifecycle_history"]))
  provider.tasks[0].update({"status":"completed","completion_comment":"Called the office"})
  complete=reconcile_provider_tasks(provider,replay.tasks,replay.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual(2,len(complete.tasks["tasks"][0]["lifecycle_history"]))
  repeated=reconcile_provider_tasks(provider,complete.tasks,complete.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual(2,len(repeated.tasks["tasks"][0]["lifecycle_history"]))
  provider.tasks[0]["status"]="open";parent_reopen=reconcile_provider_tasks(provider,repeated.tasks,repeated.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual("unresolved",parent_reopen.tasks["tasks"][0]["resolution"]);self.assertEqual("parent_reopen",parent_reopen.tasks["tasks"][0]["lifecycle_history"][-1]["kind"])
  provider.tasks[0]["status"]="completed";again=reconcile_provider_tasks(provider,parent_reopen.tasks,parent_reopen.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual("completed",again.tasks["tasks"][0]["resolution"]);self.assertEqual("parent_completion",again.tasks["tasks"][0]["lifecycle_history"][-1]["kind"])
 def test_three_way_source_only_projects_and_divergence_reviews_without_overwrite(self):
  provider=FixtureTasks();initial=self.create_and_sync(provider,{"schema_version":1,"tasks":[self.task()]})
  source=json.loads(json.dumps(initial.tasks));source["tasks"][0]["action"]="Source correction"
  projected=reconcile_provider_tasks(provider,source,initial.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual("Source correction",provider.tasks[0]["title"]);self.assertEqual("patch",projected.effects[0]["kind"])
  provider.tasks[0]["title"]="Parent only";parent=reconcile_provider_tasks(provider,projected.tasks,projected.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual("Parent only",parent.tasks["tasks"][0]["action"]);self.assertGreater(parent.tasks["tasks"][0]["revision"],projected.tasks["tasks"][0]["revision"]);self.assertEqual("provider_reconciliation",parent.tasks["tasks"][0]["last_modified_evidence"]["kind"])
  source=json.loads(json.dumps(parent.tasks));source["tasks"][0]["action"]="Second source correction";provider.tasks[0]["title"]="Parent correction"
  conflict=reconcile_provider_tasks(provider,source,parent.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual("Second source correction",conflict.tasks["tasks"][0]["action"]);self.assertEqual("Parent correction",provider.tasks[0]["title"]);self.assertEqual("title",conflict.review_cases[0]["field"])
 def test_source_correction_after_accepted_parent_edit_blocks_before_projection(self):
  flags={"is_update":False,"is_durable":False,"is_guideline":False,"is_action":True};opening={"fact_id":"fact-open","record_id":"record-1","source_message_id":"message-1","source_byte_start":0,"source_byte_end":4,"received_date":"2026-09-01","entity_scope":"household","category":"school","text":"Original action","flags":flags};task_id=canonical_task_id(opening["fact_id"])
  register=reconcile_canonical_tasks({"schema_version":1,"tasks":[]},[opening],fact_schema=self.fact_schema,task_schema=self.task_schema,register_schema=self.register_schema);provider=FixtureTasks();initial=self.create_and_sync(provider,register)
  provider.tasks[0]["title"]="Parent wording";accepted=self.sync(provider,initial.tasks,initial.provider_state)
  correction={"fact_id":"fact-correction","record_id":"record-1","source_message_id":"message-2","source_byte_start":0,"source_byte_end":4,"received_date":"2026-09-02","entity_scope":"household","category":"school","text":"Source wording","flags":{**flags,"is_action":False},"task_relation":{"target_task_id":task_id,"relation":"correction","changed_source_fields":{"action":"Source wording"}}}
  calls=list(provider.calls)
  with self.assertRaisesRegex(TaskError,"divergent source and parent.*action"):
   reconcile_canonical_tasks(accepted.tasks,[correction],fact_schema=self.fact_schema,task_schema=self.task_schema,register_schema=self.register_schema)
  self.assertEqual("Parent wording",provider.tasks[0]["title"]);self.assertEqual(calls,provider.calls)
 def test_comment_recovery_rejects_same_effect_with_wrong_text(self):
  provider=FixtureTasks();provider.tasks=[{"provider_object_id":"object-1"}];provider.comments=[{"provider_object_id":"object-1","effect_id":"effect-1","text":"wrong"}]
  with self.assertRaisesRegex(TaskError,"unexpected text"):
   recover_task_comment(provider,"object-1","effect-1","required")
 def test_interrupted_reminder_recovers_before_reopen_and_new_completion_gets_new_effect(self):
  class FaultyCompletion(FixtureTasks):
   def __init__(self): super().__init__();self.fail_comment=True
   def write_comment(self,object_id,effect_id,text):
    if self.fail_comment:self.fail_comment=False;raise ConnectionError("synthetic comment failure")
    return super().write_comment(object_id,effect_id,text)
   def apply_parent_state(self,object_id,*,status=None,**_): return self.apply_patch(object_id,{"status":status})
  provider=FaultyCompletion();initial=self.create_and_sync(provider,{"schema_version":1,"tasks":[self.task()]});provider.tasks[0].update({"status":"completed","completion_comment":""})
  intent=reconcile_provider_tasks(provider,initial.tasks,initial.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  with self.assertRaises(ConnectionError):
   reconcile_provider_tasks(provider,intent.tasks,intent.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual("completed",provider.tasks[0]["status"])
  recovered=reconcile_provider_tasks(provider,intent.tasks,intent.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual("open",provider.tasks[0]["status"]);self.assertEqual(1,len(provider.comments));first_id=recovered.tasks["tasks"][0]["lifecycle_history"][-1]["event_id"]
  provider.tasks[0].update({"status":"completed","completion_comment":""})
  second_intent=reconcile_provider_tasks(provider,recovered.tasks,recovered.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  second=reconcile_provider_tasks(provider,second_intent.tasks,second_intent.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual(2,len(provider.comments));self.assertNotEqual(first_id,second.tasks["tasks"][0]["lifecycle_history"][-1]["event_id"])
 def test_completed_source_task_is_not_created_and_duplicate_provider_binding_blocks(self):
  completed=self.task();completed["lifecycle_history"]=[{"event_id":"source-complete","kind":"source_completion"}]
  provider=FixtureTasks();result=reconcile_provider_tasks(provider,{"schema_version":1,"tasks":[completed]},self.state(),task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual([],provider.tasks);self.assertEqual([],result.provider_state["bindings"])
  duplicate=self.task();duplicate["provider_bindings"]=[{"provider_id":"synthetic","provider_object_id":"a"},{"provider_id":"synthetic","provider_object_id":"b"}]
  with self.assertRaisesRegex(TaskError,"multiple bindings"):
   reconcile_provider_tasks(FixtureTasks(),{"schema_version":1,"tasks":[duplicate]},self.state(),task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
 def test_reminder_recovery_survives_lost_comment_reopen_and_state_responses(self):
  class Base(FixtureTasks):
   def apply_parent_state(self,object_id,*,status=None,**_): return self.apply_patch(object_id,{"status":status})
  class LostComment(Base):
   fail=True
   def write_comment(self,object_id,effect_id,text):
    value=super().write_comment(object_id,effect_id,text)
    if self.fail:self.fail=False;raise ConnectionError("lost comment response")
    return value
  class LostReopenBefore(Base):
   fail=True
   def apply_parent_state(self,object_id,*,status=None,**kwargs):
    if self.fail:self.fail=False;raise ConnectionError("reopen failed before effect")
    return super().apply_parent_state(object_id,status=status,**kwargs)
  class LostReopenAfter(Base):
   fail=True
   def apply_parent_state(self,object_id,*,status=None,**kwargs):
    value=super().apply_parent_state(object_id,status=status,**kwargs)
    if self.fail:self.fail=False;raise ConnectionError("lost reopen response")
    return value
  for provider_type,expected_status in ((LostComment,"completed"),(LostReopenBefore,"completed"),(LostReopenAfter,"open")):
   with self.subTest(provider=provider_type.__name__):
    provider=provider_type();initial=self.create_and_sync(provider,{"schema_version":1,"tasks":[self.task()]});provider.tasks[0].update({"status":"completed","completion_comment":""})
    intent=reconcile_provider_tasks(provider,initial.tasks,initial.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
    with self.assertRaises(ConnectionError):
     reconcile_provider_tasks(provider,intent.tasks,intent.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
    self.assertEqual(expected_status,provider.tasks[0]["status"])
    recovered=reconcile_provider_tasks(provider,intent.tasks,intent.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
    self.assertEqual("open",provider.tasks[0]["status"]);self.assertEqual(1,len(provider.comments));self.assertEqual(1,len(recovered.tasks["tasks"][0]["lifecycle_history"]))
    replay_lost_state=reconcile_provider_tasks(provider,intent.tasks,intent.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
    self.assertEqual(1,len(provider.comments));self.assertEqual(recovered.tasks["tasks"][0]["lifecycle_history"][0]["event_id"],replay_lost_state.tasks["tasks"][0]["lifecycle_history"][0]["event_id"])
if __name__=='__main__': unittest.main()
