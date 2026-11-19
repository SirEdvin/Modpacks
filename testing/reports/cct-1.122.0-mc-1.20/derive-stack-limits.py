"""Record max stack limits measured by detailed native turtle.getItemDetail."""
import json,pathlib
OUT=pathlib.Path(__file__).resolve().parent
source=OUT/'fabric-1.20/invalid-stack-trial/upgrade-before/all-stacks/results.json'
rows=json.loads(source.read_text());limits={e['item']:e['lua']['input']['maxCount'] for e in rows if e['kind']=='turtle'}
(OUT/'item-stack-limits.json').write_text(json.dumps(dict(source=str(source.relative_to(OUT)),limits=limits),indent=2)+'\n')
print('Measured item stack limits:',len(limits),'stackable',sum(v>1 for v in limits.values()),'nonstackable',sum(v==1 for v in limits.values()))
