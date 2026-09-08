from __future__ import annotations
import json,sys,unittest
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from school_os.brief import BriefError,begin_delivery,build_brief_input,confirm_delivery,delivery_key,recover_delivery,render_brief  # noqa:E402
from school_os.tasks import parent_task_from_provider  # noqa:E402
from tests.support.fakes import SendSink  # noqa:E402
class BriefTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.input_schema=json.loads((ROOT/'schemas/brief-input.schema.json').read_text());cls.ledger_schema=json.loads((ROOT/'schemas/delivery-ledger.schema.json').read_text())
 def brief(self): return {'schema_version':1,'window':{'end':'2026-09-07'},'entity_order':['child','household'],'news':[{'date':'2026-09-07','entity_scope':'child','text':'<science>','source_link':'https://example.invalid/news'}],'guidelines':[{'date':'2026-09-07','entity_scope':'child','text':'Wear coat','source_link':'https://example.invalid/guideline'}],'tasks':[{'date':'2026-09-07','entity_scope':'household','text':'Return form','source_link':'https://example.invalid/form'}],'labels':{'news':'News','guidelines':'Guidelines','tasks':'Action Items'},'theme':{},'input_hashes':{}}
 def test_identical_input_is_byte_identical_and_escaped(self):
  first=render_brief(self.brief(),self.input_schema);second=render_brief(self.brief(),self.input_schema)
  self.assertEqual(first,second);self.assertIn(b'&lt;science&gt;',first['html']);self.assertIn(b'Action Items',first['text'])
 def source(self, fact, *, day, ordinal=0, link='https://example.invalid/thread?source=brief&item=1'):
  moment=int(datetime.fromisoformat(day+'T19:00:00+00:00').timestamp()*1000)
  return {'record_id':fact['record_id'],'source_message_id':fact['source_message_id'],'gmail_internal_date_ms':moment,'source_message_ordinal':ordinal,'source_content_ordinal':ordinal,'verified_link':link}
 def input_v2(self, *, selection=True, template=None, tasks=None, guideline_scope='child_1', scope_to_entity=None):
  facts=[
   {'fact_id':'news-new','record_id':'record-a','source_message_id':'message-a','received_date':'2026-09-07','entity_scope':'child_1','text':'Canonical <news> & details','flags':{'is_update':True,'is_action':False,'is_guideline':False}},
   {'fact_id':'news-old','record_id':'record-b','source_message_id':'message-b','received_date':'2026-08-31','entity_scope':'child_1','text':'Outside window','flags':{'is_update':True,'is_action':False,'is_guideline':False}},
   {'fact_id':'action-fact','record_id':'record-c','source_message_id':'message-c','received_date':'2026-09-07','entity_scope':'child_1','text':'Action fact never appears as news','flags':{'is_update':True,'is_action':True,'is_guideline':False}},
   {'fact_id':'guideline-fact','record_id':'record-d','source_message_id':'message-d','received_date':'2026-09-06','entity_scope':guideline_scope,'text':'Wear a coat','flags':{'is_update':False,'is_action':False,'is_guideline':True}},
  ]
  sources={fact['fact_id']:self.source(fact,day=fact['received_date'],ordinal=index) for index,fact in enumerate(facts)}
  selected=[] if selection else None
  if selection: selected=[{'fact_id':'guideline-fact','is_current':True,'latest_source_received_date':'2026-09-06','verified_link':'https://example.invalid/guideline'}]
  task_rows=[{'task_id':'source-task','origin':'source','resolution':'unresolved','action':'Return the form','entity_scope':'child_1','last_supporting_source_date':'2026-09-05','source_link':'https://example.invalid/action'},{'task_id':'parent-task','origin':'parent','resolution':'unresolved','action':'Choose a club','entity_scope':'household','last_supporting_source_date':None,'source_link':None}] if tasks is None else tasks
  projection={'child_1':'child_1','child_2':'child_2','household':'household'} if scope_to_entity is None else scope_to_entity
  return build_brief_input(run_local_date='2026-09-07',timezone='America/Los_Angeles',entities=[{'entity_id':'child_1','display_name':'Child One','kind':'child'},{'entity_id':'child_2','display_name':'Child Two','kind':'child'},{'entity_id':'household','display_name':'Family','kind':'household'}],scope_to_entity=projection,facts=facts,source_record_map=sources,current_guideline_selection=selected,unresolved_task_view={'selection':'all_unresolved_finite','tasks':task_rows},template=template,input_hashes={'facts':'f'*64})
 def test_builder_filters_by_inclusive_received_window_and_preserves_canonical_text(self):
  value=self.input_v2();self.assertEqual(['Canonical <news> & details'],[item['text'] for item in value['news']]);self.assertEqual('2026-09-07',value['news'][0]['received_date']);self.assertEqual('Wear a coat',value['guidelines'][0]['text']);self.assertEqual(['Return the form','Choose a club'],[item['text'] for item in value['tasks']])
 def test_v2_groups_received_days_keeps_parent_added_tasks_and_escapes_without_rewriting_link(self):
  rendered=render_brief(self.input_v2(),self.input_schema);html=rendered['html'].decode();plain=rendered['text'].decode()
  self.assertIn('Received September 7, 2026',html);self.assertIn('Received September 5, 2026',html);self.assertIn('Parent-added tasks',html);self.assertNotIn('Undated parent-origin',html);self.assertIn('Canonical &lt;news&gt; &amp; details',html);self.assertIn('https://example.invalid/thread?source=brief&amp;item=1',html);self.assertIn('Received 2026-09-07',plain);self.assertIn('Parent-added tasks',plain);self.assertNotIn('Action fact never appears as news',html)
 def test_parent_added_tasks_are_provider_independent_and_stay_in_their_normal_sections(self):
  source={'task_id':'source-task','origin':'source','resolution':'unresolved','action':'Return the form','entity_scope':'child_1','last_supporting_source_date':'2026-09-05','source_link':'https://example.invalid/action'}
  child={**parent_task_from_provider('sheets',{'row_id':'sheet-row','title':'Choose a club','group':'child_2'}),'resolution':'unresolved'}
  household={**parent_task_from_provider('other-provider',{'provider_object_id':'provider-row','title':'Choose a dinner','group':'household'}),'resolution':'unresolved'}
  rendered=render_brief(self.input_v2(tasks=[source,child,household]),self.input_schema);html=rendered['html'].decode();plain=rendered['text'].decode()
  self.assertEqual(2,html.count('Parent-added tasks'));self.assertIn('<li>Choose a club</li>',html);self.assertIn('<li>Choose a dinner</li>',html);self.assertNotIn('Choose a club &mdash;',html);self.assertLess(html.index('Child Two'),html.index('Choose a club'));self.assertLess(html.index('Family'),html.index('Choose a dinner'));self.assertIn('Parent-added tasks',plain)
 def test_completed_and_malformed_source_tasks_are_excluded_or_blocked(self):
  completed={**parent_task_from_provider('sheets',{'row_id':'sheet-row','title':'Already done','group':'child_2'}),'resolution':'completed'}
  with self.assertRaisesRegex(BriefError,'explicit unresolved'): self.input_v2(tasks=[completed])
  source={'task_id':'source-task','origin':'source','resolution':'unresolved','action':'Return the form','entity_scope':'child_1','last_supporting_source_date':None,'source_link':'https://example.invalid/action'}
  with self.assertRaisesRegex(BriefError,'source-origin unresolved task requires verified source date and link'): self.input_v2(tasks=[source])
  source['last_supporting_source_date']='not-a-date'
  with self.assertRaisesRegex(BriefError,'task last supporting source date must be an ISO local date'): self.input_v2(tasks=[source])
 def test_entries_use_visible_separators_and_bold_guideline_scope(self):
  html=render_brief(self.input_v2(),self.input_schema)['html'].decode();plain=render_brief(self.input_v2(),self.input_schema)['text'].decode()
  self.assertIn('Canonical &lt;news&gt; &amp; details &mdash; <a href=',html);self.assertIn('Return the form &mdash; <a href=',html);self.assertIn('<strong>Child One:</strong> Wear a coat &mdash; <a href=',html);self.assertIn('Canonical <news> & details — Source:',plain)
 def test_multi_child_guideline_scope_is_preserved_separately_from_household_route(self):
  value=self.input_v2(guideline_scope='Child One, Child Two',scope_to_entity={'child_1':'child_1','child_2':'child_2','household':'household','Child One, Child Two':'household'})
  self.assertEqual('household',value['guidelines'][0]['entity_scope']);self.assertEqual('Child One, Child Two',value['guidelines'][0]['scope_display'])
  self.assertIn('<strong>Child One, Child Two:</strong> Wear a coat',render_brief(value,self.input_schema)['html'].decode())
 def test_theme_is_applied_and_source_task_without_verified_link_blocks(self):
  value=self.input_v2();value['theme']={**value['theme'],'news_banner':'#123456'};self.assertIn('background-color:#123456',render_brief(value,self.input_schema)['html'].decode())
  value=self.input_v2();value['tasks'][0]['source_link']=None
  with self.assertRaisesRegex(BriefError,'source-origin brief task requires'): render_brief(value,self.input_schema)
 def test_template_mapping_rejects_unknown_and_renders_declared_empty_fallback(self):
  template={'version':'synthetic-v1','html':'<main>{{DATE}}{{CHILD_NEWS}}{{CHILD1_TASKS}}{{CHILD_TASKS}}{{FAMILY_TASKS}}{{GUIDELINES}}</main>','text':'{{DATE}}\n{{CHILD_NEWS}}\n{{CHILD1_TASKS}}\n{{CHILD_TASKS}}\n{{FAMILY_TASKS}}\n{{GUIDELINES}}','placeholders':{'DATE':{'kind':'date'},'CHILD_NEWS':{'kind':'entries','section':'news','entity_scope':'child_1'},'CHILD1_TASKS':{'kind':'entries','section':'tasks','entity_scope':'child_1'},'CHILD_TASKS':{'kind':'entries','section':'tasks','entity_scope':'child_2','empty_text':'No child tasks.'},'FAMILY_TASKS':{'kind':'entries','section':'tasks','entity_scope':'household'},'GUIDELINES':{'kind':'entries','section':'guidelines','entity_scope':'*'}}}
  rendered=render_brief(self.input_v2(template=template),self.input_schema)['html'].decode();self.assertIn('September 7, 2026',rendered);self.assertIn('No child tasks.',rendered);self.assertNotIn('{{',rendered)
  unrouted={'version':'synthetic-v1','html':'<main>{{DATE}}{{CHILD_NEWS}}{{CHILD1_TASKS}}{{CHILD_TASKS}}{{GUIDELINES}}</main>','text':'{{DATE}}\n{{CHILD_NEWS}}\n{{CHILD1_TASKS}}\n{{CHILD_TASKS}}\n{{GUIDELINES}}','placeholders':{key:value for key,value in template['placeholders'].items() if key!='FAMILY_TASKS'}}
  with self.assertRaisesRegex(BriefError,'does not route exactly one'): self.input_v2(template=unrouted)
  household_news=self.input_v2();household_news['news'][0].update({'entity_scope':'household','scope_display':'household','text':'Shared news must survive'})
  self.assertIn('Shared news must survive',render_brief(household_news,self.input_schema)['html'].decode())
  selected=self.input_v2(template=template);selected['news'][0].update({'entity_scope':'household','scope_display':'household','text':'Shared news must block'})
  with self.assertRaisesRegex(BriefError,'does not route exactly one'): render_brief(selected,self.input_schema)
  duplicate=self.input_v2();duplicate['template']['html']+=duplicate['template']['html']
  with self.assertRaisesRegex(BriefError,'exactly once'): render_brief(duplicate,self.input_schema)
  duplicate=self.input_v2();duplicate['template']['text']+=duplicate['template']['text']
  with self.assertRaisesRegex(BriefError,'exactly once'): render_brief(duplicate,self.input_schema)
  template['html']='<main>{{DATE}}{{UNKNOWN}}</main>'
  with self.assertRaisesRegex(BriefError,'exactly once'): self.input_v2(template=template)
 def test_builder_requires_explicit_current_guideline_selection_and_does_not_infer_task_resolution(self):
  with self.assertRaisesRegex(BriefError,'current guideline selection is required'): self.input_v2(selection=False)
  value=self.input_v2();value['tasks'][0]['origin']='source';value['tasks'][0]['source_link']='javascript:alert(1)'
  with self.assertRaisesRegex(BriefError,'unsafe URL scheme'): render_brief(value,self.input_schema)
 def test_send_sink_confirms_one_ledger_entry_and_blocks_duplicate(self):
  sink=SendSink();ledger={'schema_version':1,'entries':[]};content=render_brief(self.brief(),self.input_schema)['html'];result=confirm_delivery(sink,ledger,delivery_key='daily-20260907',variant='normal',content=content,recipients_fingerprint='a'*64,ledger_schema=self.ledger_schema)
  self.assertEqual(1,len(sink.deliveries));self.assertEqual('confirmed',result['entries'][0]['outcome'])
  with self.assertRaisesRegex(BriefError,'already exists'):confirm_delivery(sink,result,delivery_key='daily-20260907',variant='normal',content=content,recipients_fingerprint='a'*64,ledger_schema=self.ledger_schema)
 def test_lost_send_is_reconciled_once_and_correction_uses_distinct_key(self):
  class LostSink(SendSink):
   def send(self,content): super().send(content);raise ConnectionError('lost response')
  content=render_brief(self.brief(),self.input_schema)['html'];key=delivery_key('instance','daily-run','2026-09-07','normal');sink=LostSink();pending=begin_delivery({'schema_version':1,'entries':[]},delivery_key=key,variant='normal',content=content,recipients_fingerprint='a'*64,ledger_schema=self.ledger_schema)
  with self.assertRaisesRegex(BriefError,'already exists'):begin_delivery(pending,delivery_key=key,variant='normal',content=content,recipients_fingerprint='a'*64,ledger_schema=self.ledger_schema)
  with self.assertRaises(ConnectionError):sink.send(content)
  recovered=recover_delivery(sink,pending,delivery_key=key,content=content,ledger_schema=self.ledger_schema)
  self.assertEqual('confirmed',recovered['entries'][0]['outcome']);self.assertEqual(1,len(sink.deliveries))
  self.assertEqual(recovered,recover_delivery(sink,recovered,delivery_key=key,content=content,ledger_schema=self.ledger_schema))
  self.assertNotEqual(key,delivery_key('instance','daily-run','2026-09-07','correction-1'))
  with self.assertRaisesRegex(BriefError,'inconclusive'):recover_delivery(SendSink(),pending,delivery_key=key,content=content,ledger_schema=self.ledger_schema)
 def test_manual_and_scheduled_entrypoints_share_one_delivery_key(self):
  content=render_brief(self.brief(),self.input_schema)['html'];key=delivery_key('instance','daily-run','2026-09-07','normal')
  manual=begin_delivery({'schema_version':1,'entries':[]},delivery_key=key,variant='normal',content=content,recipients_fingerprint='a'*64,ledger_schema=self.ledger_schema)
  with self.assertRaisesRegex(BriefError,'already exists'):begin_delivery(manual,delivery_key=key,variant='normal',content=content,recipients_fingerprint='a'*64,ledger_schema=self.ledger_schema)
if __name__=='__main__':unittest.main()
