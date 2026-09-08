from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from school_os.tasks import TaskError, recover_task_comment, reconcile_provider_tasks  # noqa: E402
from tests.support.fakes import FixtureTasks  # noqa: E402

class ProviderReconciliationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.task_schema=json.loads((ROOT/'schemas/task.schema.json').read_text()); cls.register_schema=json.loads((ROOT/'schemas/canonical-tasks.schema.json').read_text()); cls.state_schema=json.loads((ROOT/'schemas/provider-state.schema.json').read_text())
 def task(self):
  return {"task_id":"task-1","origin":"source","action":"Return form","task_context":"school","entity_scope":"household","workflow_state":"needs_action","owner":None,"source_opened_date":"2026-09-07","last_supporting_source_date":"2026-09-07","source_due":None,"parent_planned_due":None,"source_link":"record-1#fact-1","source_facts":["fact-1"],"latest_progress":None,"provider_bindings":[],"lifecycle_history":[],"projection_state":{},"revision":1,"last_modified_evidence":{}}
 def state(self): return {"provider_id":"synthetic","adapter_id":"synthetic-tasks","provider_revision":None,"bindings":[],"cursor":None,"cursor_evidence":{},"verified_readback":{}}
 def test_pull_first_create_readback_and_binding_preserves_provider_fields(self):
  provider=FixtureTasks(); register={"schema_version":1,"tasks":[self.task()]}
  result=reconcile_provider_tasks(provider,register,self.state(),task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual(["list","create","read"],provider.calls); self.assertEqual("confirmed",result.effects[0]["outcome"]); self.assertEqual("task-1",result.provider_state["bindings"][0]["task_id"])
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
  with self.assertRaises(ConnectionError):reconcile_provider_tasks(provider,register,self.state(),task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual(1,len(provider.tasks))
  recovered=reconcile_provider_tasks(provider,register,self.state(),task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual(1,len(provider.tasks));self.assertEqual('task-1',recovered.provider_state['bindings'][0]['task_id'])
  provider.tasks[0].update({'title':'Parent title','group':'parent-group','parent_planned_due':'2026-09-10','progress':'done'})
  preserved=reconcile_provider_tasks(provider,register,recovered.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual('Parent title',provider.tasks[0]['title']);self.assertEqual('parent-group',provider.tasks[0]['group']);self.assertEqual('Parent title',preserved.tasks['tasks'][0]['action']);self.assertEqual('parent-group',preserved.tasks['tasks'][0]['entity_scope'])
 def test_lost_update_response_is_adopted_without_a_second_patch(self):
  class LostPatchTasks(FixtureTasks):
   def __init__(self): super().__init__();self.lose=True
   def apply_patch(self,object_id,patch):
    result=super().apply_patch(object_id,patch)
    if self.lose: self.lose=False;raise ConnectionError('synthetic lost patch response')
    return result
  provider=LostPatchTasks();old=self.task();register={"schema_version":1,"tasks":[old]}
  initial=reconcile_provider_tasks(provider,register,self.state(),task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
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
  initial=reconcile_provider_tasks(provider,register,self.state(),task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
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
  provider=FixtureTasks();initial=reconcile_provider_tasks(provider,{"schema_version":1,"tasks":[self.task()]},self.state(),task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  source=json.loads(json.dumps(initial.tasks));source["tasks"][0]["action"]="Source correction"
  projected=reconcile_provider_tasks(provider,source,initial.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual("Source correction",provider.tasks[0]["title"]);self.assertEqual("patch",projected.effects[0]["kind"])
  provider.tasks[0]["title"]="Parent only";parent=reconcile_provider_tasks(provider,projected.tasks,projected.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual("Parent only",parent.tasks["tasks"][0]["action"]);self.assertGreater(parent.tasks["tasks"][0]["revision"],projected.tasks["tasks"][0]["revision"]);self.assertEqual("provider_reconciliation",parent.tasks["tasks"][0]["last_modified_evidence"]["kind"])
  source=json.loads(json.dumps(parent.tasks));source["tasks"][0]["action"]="Second source correction";provider.tasks[0]["title"]="Parent correction"
  conflict=reconcile_provider_tasks(provider,source,parent.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual("Second source correction",conflict.tasks["tasks"][0]["action"]);self.assertEqual("Parent correction",provider.tasks[0]["title"]);self.assertEqual("title",conflict.review_cases[0]["field"])
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
  provider=FaultyCompletion();initial=reconcile_provider_tasks(provider,{"schema_version":1,"tasks":[self.task()]},self.state(),task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema);provider.tasks[0].update({"status":"completed","completion_comment":""})
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
    provider=provider_type();initial=reconcile_provider_tasks(provider,{"schema_version":1,"tasks":[self.task()]},self.state(),task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema);provider.tasks[0].update({"status":"completed","completion_comment":""})
    intent=reconcile_provider_tasks(provider,initial.tasks,initial.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
    with self.assertRaises(ConnectionError):
     reconcile_provider_tasks(provider,intent.tasks,intent.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
    self.assertEqual(expected_status,provider.tasks[0]["status"])
    recovered=reconcile_provider_tasks(provider,intent.tasks,intent.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
    self.assertEqual("open",provider.tasks[0]["status"]);self.assertEqual(1,len(provider.comments));self.assertEqual(1,len(recovered.tasks["tasks"][0]["lifecycle_history"]))
    replay_lost_state=reconcile_provider_tasks(provider,intent.tasks,intent.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
    self.assertEqual(1,len(provider.comments));self.assertEqual(recovered.tasks["tasks"][0]["lifecycle_history"][0]["event_id"],replay_lost_state.tasks["tasks"][0]["lifecycle_history"][0]["event_id"])
if __name__=='__main__': unittest.main()
