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
  self.assertEqual('Parent title',provider.tasks[0]['title']);self.assertEqual('parent-group',provider.tasks[0]['group']);self.assertEqual(2,len(preserved.review_cases))
 def test_lost_comment_response_is_adopted_without_duplicate(self):
  class LostCommentTasks(FixtureTasks):
   def write_comment(self,object_id,effect_id,text):
    result=super().write_comment(object_id,effect_id,text)
    raise ConnectionError('synthetic lost comment response')
  provider=LostCommentTasks();provider.tasks=[{'provider_object_id':'task-1'}]
  with self.assertRaises(ConnectionError):recover_task_comment(provider,'task-1','comment-1','Parent progress')
  adopted=recover_task_comment(provider,'task-1','comment-1','Parent progress')
  self.assertEqual('Parent progress',adopted['text']);self.assertEqual(1,len(provider.comments))
if __name__=='__main__': unittest.main()
