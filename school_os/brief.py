"""Deterministic brief rendering and verified synthetic delivery ledger helpers."""
from __future__ import annotations
from collections.abc import Mapping
from html import escape
from typing import Any, Protocol
from .contracts import canonical_json_bytes, sha256_bytes, validate

class BriefError(ValueError): pass
class DeliveryPort(Protocol):
 def send(self, content: bytes) -> str: ...
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
def confirm_delivery(port:DeliveryPort,ledger:Mapping[str,Any],*,delivery_key:str,variant:str,content:bytes,recipients_fingerprint:str,ledger_schema:Mapping[str,Any])->dict[str,Any]:
 _valid(ledger,ledger_schema,'delivery ledger')
 if any(entry['delivery_key']==delivery_key and entry['outcome']=='confirmed' for entry in ledger['entries']): raise BriefError('delivery key already confirmed')
 message_id=port.send(content)
 entry={'delivery_key':delivery_key,'variant':variant,'content_sha256':sha256_bytes(content),'recipients_fingerprint':recipients_fingerprint,'outcome':'confirmed','provider_message_id':message_id,'verification':{'provider_message_id':message_id}}
 result={'schema_version':1,'entries':[*(ledger['entries']),entry]}; _valid(result,ledger_schema,'delivery ledger'); return result
