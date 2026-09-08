"""Deterministic brief rendering and verified synthetic delivery ledger helpers."""
from __future__ import annotations
from collections.abc import Mapping
from html import escape
from typing import Any, Protocol
from .contracts import canonical_json_bytes, sha256_bytes, validate

class BriefError(ValueError): pass
class DeliveryPort(Protocol):
 def send(self, content: bytes) -> str: ...
 def find_delivery(self, content: bytes) -> list[str]: ...
def _valid(value: Any,schema: Mapping[str,Any],label:str)->None:
 errors=validate(value,dict(schema))
 if errors: raise BriefError(f"invalid {label}: "+"; ".join(errors))
def _ordered(items:list[dict[str,Any]], entity_order:list[str])->list[dict[str,Any]]:
 rank={entity:index for index,entity in enumerate(entity_order)}
 return sorted(items,key=lambda item:(str(item.get('date','')),rank.get(item.get('entity_scope'),len(rank)),str(item.get('text',''))),reverse=True)
def _line(item:Mapping[str,Any],html:bool)->str:
 text=str(item.get('text',''))
 link=item.get('source_link')
 if html:
  safe=escape(text)
  return f'<li>{safe}' + (f' <a href="{escape(str(link),quote=True)}">Source</a>' if link else '') + '</li>'
 return f'- {text}' + (f' (Source: {link})' if link else '')
def render_brief(value:Mapping[str,Any],schema:Mapping[str,Any])->dict[str,bytes]:
 _valid(value,schema,'brief input'); labels=value['labels']; order=value['entity_order']
 sections=[(labels.get('news','News'),value['news']),(labels.get('guidelines','Guidelines'),value['guidelines']),(labels.get('tasks','Action Items'),value['tasks'])]
 html_parts=[]; text_parts=[]
 for title,items in sections:
  ordered=_ordered(items,order); html_parts.append(f'<section><h2>{escape(str(title))}</h2><ul>'+''.join(_line(item,True) for item in ordered)+'</ul></section>')
  text_parts.append(str(title)+'\n'+('\n'.join(_line(item,False) for item in ordered) or '- None'))
 return {'html':('<!doctype html><html><body><main>'+''.join(html_parts)+'</main></body></html>\n').encode(),'text':('\n\n'.join(text_parts)+'\n').encode()}
def delivery_key(instance_id:str,operation:str,window:str,variant:str)->str:
 if not all((instance_id,operation,window,variant)): raise BriefError('delivery key inputs are required')
 return 'delivery-'+sha256_bytes('\0'.join((instance_id,operation,window,variant)).encode())
def begin_delivery(ledger:Mapping[str,Any],*,delivery_key:str,variant:str,content:bytes,recipients_fingerprint:str,ledger_schema:Mapping[str,Any])->dict[str,Any]:
 _valid(ledger,ledger_schema,'delivery ledger')
 if any(entry['delivery_key']==delivery_key for entry in ledger['entries']): raise BriefError('delivery key already exists')
 entry={'delivery_key':delivery_key,'variant':variant,'content_sha256':sha256_bytes(content),'recipients_fingerprint':recipients_fingerprint,'outcome':'pending','provider_message_id':None,'verification':{}}
 result={'schema_version':1,'entries':[*(ledger['entries']),entry]}; _valid(result,ledger_schema,'delivery ledger'); return result
def recover_delivery(port:DeliveryPort,ledger:Mapping[str,Any],*,delivery_key:str,content:bytes,ledger_schema:Mapping[str,Any])->dict[str,Any]:
 _valid(ledger,ledger_schema,'delivery ledger'); entries=[dict(entry) for entry in ledger['entries']]; matches=[entry for entry in entries if entry['delivery_key']==delivery_key]
 if len(matches)!=1: raise BriefError('delivery recovery requires one durable intent')
 entry=matches[0]
 if entry['outcome']=='confirmed': return {'schema_version':1,'entries':entries}
 found=port.find_delivery(content)
 if len(found)!=1: raise BriefError('delivery lookup is ambiguous or inconclusive')
 entry.update({'outcome':'confirmed','provider_message_id':found[0],'verification':{'provider_message_id':found[0]}})
 result={'schema_version':1,'entries':entries};_valid(result,ledger_schema,'delivery ledger');return result
def confirm_delivery(port:DeliveryPort,ledger:Mapping[str,Any],*,delivery_key:str,variant:str,content:bytes,recipients_fingerprint:str,ledger_schema:Mapping[str,Any])->dict[str,Any]:
 pending=begin_delivery(ledger,delivery_key=delivery_key,variant=variant,content=content,recipients_fingerprint=recipients_fingerprint,ledger_schema=ledger_schema)
 message_id=port.send(content)
 entries=[dict(entry) for entry in pending['entries']];entries[-1].update({'outcome':'confirmed','provider_message_id':message_id,'verification':{'provider_message_id':message_id}})
 result={'schema_version':1,'entries':entries};_valid(result,ledger_schema,'delivery ledger');return result
