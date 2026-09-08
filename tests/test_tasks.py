from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from school_os.tasks import TaskError, build_derived_knowledge, canonical_task_id, parent_task_from_provider, reconcile_canonical_tasks, serialize_canonical_tasks, unresolved_tasks  # noqa: E402

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
 def test_attachment_fact_keeps_origin_hashes_and_a_verifiable_locator(self):
  facts=self.facts(); facts[0]['attachment']={
   "attachment_id":"resource-001", "origin":"html_embedded", "mime_type":"image/png",
   "original_content_sha256":"a"*64, "extracted_text_sha256":"b"*64,
   "locator":{"kind":"extracted_text_span","byte_start":0,"byte_end":3},
  }
  build_derived_knowledge(facts,fact_schema=self.fact,task_schema=self.task)
  del facts[0]['attachment']['origin']
  with self.assertRaisesRegex(TaskError,"invalid Fact"):
   build_derived_knowledge(facts,fact_schema=self.fact,task_schema=self.task)
 def test_explicit_parent_row_gets_issued_non_source_identity(self):
  row={"provider_object_id":"row-1","managed_by":"parent","title":"Call school","group":"household","progress":"left voicemail"}
  first=parent_task_from_provider("sheets",row);second=parent_task_from_provider("sheets",row)
  recovered=parent_task_from_provider("sheets",row,task_id=first["task_id"])
  self.assertNotEqual(first['task_id'],second['task_id']);self.assertEqual(first['task_id'],recovered['task_id']);self.assertEqual('parent',first['origin']);self.assertEqual([],first['source_facts']);self.assertIsNone(first['source_link'])
  with self.assertRaisesRegex(TaskError,"explicit parent"):
   parent_task_from_provider("sheets",{**row,"managed_by":None})
 def test_explicit_source_relation_updates_only_its_target_and_keeps_opening_id(self):
  register=reconcile_canonical_tasks({"schema_version":1,"tasks":[]},self.facts(),fact_schema=self.fact,task_schema=self.task,register_schema=self.register)
  task_id=register["tasks"][0]["task_id"]
  support={"fact_id":"fact-correction","record_id":"record-2","source_message_id":"message-2","source_byte_start":0,"source_byte_end":4,"received_date":"2026-09-08","entity_scope":"household","category":"school","text":"The deadline is Friday","flags":{"is_update":True,"is_durable":False,"is_guideline":False,"is_action":False},"task_relation":{"target_task_id":task_id,"relation":"correction","changed_source_fields":{"source_due":"2026-09-12"}}}
  repaired=reconcile_canonical_tasks(register,[*self.facts(),support],fact_schema=self.fact,task_schema=self.task,register_schema=self.register)
  task=repaired["tasks"][0]
  self.assertEqual(task_id,task["task_id"]);self.assertEqual("2026-09-12",task["source_due"]);self.assertIn("fact-correction",task["source_facts"]);self.assertGreater(task["revision"],register["tasks"][0]["revision"]);self.assertEqual("source_reconciliation",task["last_modified_evidence"]["kind"])
  support["task_relation"]["target_task_id"]="task-unknown"
  with self.assertRaisesRegex(TaskError,"unknown target"):
   reconcile_canonical_tasks(register,[*self.facts(),support],fact_schema=self.fact,task_schema=self.task,register_schema=self.register)
 def test_source_relations_use_source_chronology_and_resolution(self):
  opening=self.facts()[0];task_id=canonical_task_id(opening["fact_id"]);flags={"is_update":False,"is_durable":False,"is_guideline":False,"is_action":False}
  def relation(fact_id,date,relation,due):
   return {"fact_id":fact_id,"record_id":"record-2","source_message_id":"message-2","source_byte_start":0,"source_byte_end":3,"received_date":date,"entity_scope":"household","category":"school","text":relation,"flags":flags,"task_relation":{"target_task_id":task_id,"relation":relation,"changed_source_fields":({"source_due":due} if due else {})}}
  newer=relation("a-newer","2026-09-10","completion","2026-09-12");older=relation("z-older","2026-09-02","correction","2026-09-09")
  completed=reconcile_canonical_tasks({"schema_version":1,"tasks":[]},[opening,newer,older],fact_schema=self.fact,task_schema=self.task,register_schema=self.register)
  self.assertEqual("2026-09-12",completed["tasks"][0]["source_due"]);self.assertEqual("2026-09-10",completed["tasks"][0]["last_supporting_source_date"]);self.assertEqual("completed",completed["tasks"][0]["resolution"])
  reopened=relation("zz-reopen","2026-09-11","reopen",None)
  result=reconcile_canonical_tasks(completed,[opening,newer,older,reopened],fact_schema=self.fact,task_schema=self.task,register_schema=self.register)
  self.assertEqual([],unresolved_tasks(completed));self.assertEqual("unresolved",result["tasks"][0]["resolution"]);self.assertEqual(1,len(unresolved_tasks(result)));self.assertEqual(["source_completion","source_reopen"],[event["kind"] for event in result["tasks"][0]["lifecycle_history"]])
 def test_conflicting_relations_at_same_source_coordinate_block(self):
  opening=self.facts()[0];task_id=canonical_task_id(opening["fact_id"]);flags={"is_update":False,"is_durable":False,"is_guideline":False,"is_action":False}
  base={"record_id":"record-2","source_message_id":"message-2","source_byte_start":0,"source_byte_end":3,"received_date":"2026-09-08","entity_scope":"household","category":"school","flags":flags}
  a={**base,"fact_id":"fact-a","text":"Friday","task_relation":{"target_task_id":task_id,"relation":"correction","changed_source_fields":{"source_due":"2026-09-11"}}};b={**base,"fact_id":"fact-b","text":"Monday","task_relation":{"target_task_id":task_id,"relation":"correction","changed_source_fields":{"source_due":"2026-09-14"}}}
  with self.assertRaisesRegex(TaskError,"source coordinate"):
   reconcile_canonical_tasks({"schema_version":1,"tasks":[]},[opening,a,b],fact_schema=self.fact,task_schema=self.task,register_schema=self.register)
if __name__=='__main__': unittest.main()
