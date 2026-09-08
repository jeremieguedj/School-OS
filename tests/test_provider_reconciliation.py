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
  reopened=reconcile_provider_tasks(provider,initial.tasks,initial.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual("open",provider.tasks[0]["status"]);self.assertEqual(1,len(provider.comments));self.assertEqual("reopened_missing_completion_comment",reopened.tasks["tasks"][0]["lifecycle_history"][0]["kind"])
  replay=reconcile_provider_tasks(provider,reopened.tasks,reopened.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual(1,len(provider.comments));self.assertEqual(1,len(replay.tasks["tasks"][0]["lifecycle_history"]))
  provider.tasks[0].update({"status":"completed","completion_comment":"Called the office"})
  complete=reconcile_provider_tasks(provider,replay.tasks,replay.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual(2,len(complete.tasks["tasks"][0]["lifecycle_history"]))
  repeated=reconcile_provider_tasks(provider,complete.tasks,complete.provider_state,task_schema=self.task_schema,register_schema=self.register_schema,provider_state_schema=self.state_schema)
  self.assertEqual(2,len(repeated.tasks["tasks"][0]["lifecycle_history"]))
if __name__=='__main__': unittest.main()
