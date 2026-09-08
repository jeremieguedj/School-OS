from __future__ import annotations
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from school_os.brief import BriefError,confirm_delivery,render_brief  # noqa:E402
from tests.support.fakes import SendSink  # noqa:E402
class BriefTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.input_schema=json.loads((ROOT/'schemas/brief-input.schema.json').read_text());cls.ledger_schema=json.loads((ROOT/'schemas/delivery-ledger.schema.json').read_text())
 def brief(self): return {'schema_version':1,'window':{'end':'2026-09-07'},'entity_order':['child','household'],'news':[{'date':'2026-09-07','entity_scope':'child','text':'<science>'}],'guidelines':[{'date':'2026-09-07','entity_scope':'child','text':'Wear coat'}],'tasks':[{'date':'2026-09-07','entity_scope':'household','text':'Return form','source_link':'https://example.invalid/form'}],'labels':{'news':'News','guidelines':'Guidelines','tasks':'Action Items'},'theme':{},'input_hashes':{}}
 def test_identical_input_is_byte_identical_and_escaped(self):
  first=render_brief(self.brief(),self.input_schema);second=render_brief(self.brief(),self.input_schema)
  self.assertEqual(first,second);self.assertIn(b'&lt;science&gt;',first['html']);self.assertIn(b'Action Items',first['text'])
 def test_send_sink_confirms_one_ledger_entry_and_blocks_duplicate(self):
  sink=SendSink();ledger={'schema_version':1,'entries':[]};content=render_brief(self.brief(),self.input_schema)['html'];result=confirm_delivery(sink,ledger,delivery_key='daily-20260907',variant='normal',content=content,recipients_fingerprint='a'*64,ledger_schema=self.ledger_schema)
  self.assertEqual(1,len(sink.deliveries));self.assertEqual('confirmed',result['entries'][0]['outcome'])
  with self.assertRaisesRegex(BriefError,'already confirmed'):confirm_delivery(sink,result,delivery_key='daily-20260907',variant='normal',content=content,recipients_fingerprint='a'*64,ledger_schema=self.ledger_schema)
if __name__=='__main__':unittest.main()
