"""Read exact top-level SNBT fields without mistaking inventory items for upgrades."""
import json

def fields(text):
 text=text[text.index('{')+1:text.rindex('}')]
 chunks=[];start=0;depth=0;quote=False;escape=False
 for i,c in enumerate(text):
  if quote:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quote=False
  elif c=='"':quote=True
  elif c in '{[':depth+=1
  elif c in '}]':depth-=1
  elif c==',' and depth==0:chunks.append(text[start:i].strip());start=i+1
 chunks.append(text[start:].strip())
 result={}
 for chunk in chunks:
  if not chunk:continue
  if chunk.startswith('"'):
   key,end=json.JSONDecoder().raw_decode(chunk);value=chunk[end:].lstrip().removeprefix(':').strip()
  else:key,_,value=chunk.partition(':');key=key.strip();value=value.strip()
  result[key]=value
 return result

def equipped_upgrade(text,kind):
 try:
  root=fields(text)
  if kind=='turtle':
   if 'RightUpgrade' in root:return None
   value=root.get('LeftUpgrade','')
  else:value=fields(root['components'])['computercraft:pocket_upgrade']
  if value.startswith('"'):return json.loads(value)
  return json.loads(fields(value)['id'])
 except (ValueError,KeyError,json.JSONDecodeError):return None

if __name__=='__main__':
 assert equipped_upgrade('{Items:[{id:"wrong"}],LeftUpgrade:{item:{id:"u",count:1},id:"u"}}','turtle')=='u'
 assert equipped_upgrade('{Items:[{id:"u"}],LeftUpgrade:{id:"wrong"}}','turtle')=='wrong'
 assert equipped_upgrade('{LeftUpgrade:"u"}','turtle')=='u'
 assert equipped_upgrade('{components:{"computercraft:pocket_upgrade":{item:{id:"u"},id:"u"}}}','pocket')=='u'
 print('SNBT upgrade-field regressions PASS')
