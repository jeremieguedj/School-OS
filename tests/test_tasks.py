from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from school_os.tasks import TaskError, build_derived_knowledge, canonical_task_id, reconcile_canonical_tasks, serialize_canonical_tasks  # noqa: E402

class TaskTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.fact=json.loads((ROOT/'schemas/fact.schema.json').read_text()); cls.task=json.loads((ROOT/'schemas/task.schema.json').read_text()); cls.register=json.loads((ROOT/'schemas/canonical-tasks.schema.json').read_text())
 def facts(self):
  base=lambda id,text,flags,start: {"fact_id":id,"record_id":"record-1","source_message_id":"message-1","source_byte_start":start,"source_byte_end":start+3,"received_date":"2026-09-07","entity_scope":"household","category":"school","text":text,"flags":flags}
  return [base("fact-action","Return the form",{"is_update":False,"is_durable":False,"is_guideline":False,"is_action":True},0),base("fact-guideline","Bring a coat when it rains",{"is_update":False,"is_durable":True,"is_guideline":True,"is_action":False},4),base("fact-update","Science observation completed",{"is_update":True,"is_durable":False,"is_guideline":False,"is_action":False},8)]
 def test_source_linked_facts_build_separate_outputs(self):
  derived=build_derived_knowledge(self.facts(),fact_schema=self.fact,task_schema=self.task)
  self.assertEqual(["fact-guideline"],[x['fact_id'] for x in derived['guidelines']]); self.assertEqual(["fact-update"],[x['fact_id'] for x in derived['rolling_updates']]); self.assertEqual(canonical_task_id("fact-action"),derived['tasks'][0]['task_id']); self.assertEqual(["fact-action"],derived['tasks'][0]['source_facts'])
 def test_guideline_never_becomes_task_and_invalid_combination_fails(self):
  facts=self.facts(); facts[1]['flags']['is_action']=True
  with self.assertRaisesRegex(TaskError,"guideline cannot be an action"): build_derived_knowledge(facts,fact_schema=self.fact,task_schema=self.task)
 def test_rebuild_is_stable_and_existing_identity_is_preserved_without_title_matching(self):
  first=reconcile_canonical_tasks({"schema_version":1,"tasks":[]},self.facts(),fact_schema=self.fact,task_schema=self.task,register_schema=self.register)
  second=reconcile_canonical_tasks(first,self.facts(),fact_schema=self.fact,task_schema=self.task,register_schema=self.register)
  self.assertEqual(serialize_canonical_tasks(first,self.register),serialize_canonical_tasks(second,self.register))
if __name__=='__main__': unittest.main()
