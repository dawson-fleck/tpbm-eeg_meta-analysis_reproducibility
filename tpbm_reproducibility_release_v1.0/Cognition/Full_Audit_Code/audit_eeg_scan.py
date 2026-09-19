from pathlib import Path
import csv,collections,re,zipfile,xml.etree.ElementTree as ET,json
A=Path(__file__).resolve().parent;B=A.parent
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def write(name,rows):
 if not rows:return
 with (A/'Outputs'/name).open('w',newline='',encoding='utf-8-sig') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
d=read(A/'EEG_replication/Inputs/EEG_effects_audited.csv');groups=collections.defaultdict(list)
for x in d:
 if x['eligible_for_new_pool']=='1':groups[(x['construct'],x['band'])].append(x)
rows=[]
for (construct,band),rr in groups.items():
 clusters={x['cluster_id'] for x in rr};units=sum(max(int(x['independent_experiments_in_cluster']) for x in rr if x['cluster_id']==c) for c in clusters)
 rows.append(dict(construct=construct,band=band,clusters=len(clusters),independent_upper_bound=units,cohorts=';'.join(sorted(clusters)),decision='No compatible k>=3 even before state/timing/anatomy stratification' if units<3 else 'Needs compatibility review'))
write('EEG_independent_family_gate.csv',rows)
assert max(x['independent_upper_bound'] for x in rows)<3
legacy=read(B/'EEG/Inputs/EEG_effects_audited.csv');assert len(d)==len(legacy)
for x,y in zip(d,legacy):assert x==y
write('EEG_reproduction_comparison.csv',[dict(rows=len(d),identical=True,arithmetic_checks=len(read(A/'EEG_replication/Outputs/EEG_effect_reconstruction_checks.csv')),unreconstructed='ZhaoC CDA and Mehdizadeh delta',quarantined='Zomorrodi 2019 five rows',maximum_broad_family_datasets=max(x['independent_upper_bound'] for x in rows))])
# Scan active publication material and historical reporting; hits are candidates, not automatic errors.
patterns={'historical_overall':r'0[.]667|[.]446.{0,8}[.]887','historical_RoB17':r'0[.]626|[.]386.{0,8}[.]866','old_current_overall':r'0[.]390|0[.]3899','wrong_CI_discussion':r'crossing zero in all three','EEG_association_conflation':r'feature associated with improved cognition','old_current_memory':r'0[.]281','unresolved_placeholder':r'\[AQ\d|\[Assembly note'}
files=[A/'Sources/Manuscript_live.txt']+list((B/'Cognition').glob('*.md'))+list((B/'Publication_Package_2026-09-16').glob('*.md'))+list((B/'Publication_Package_2026-09-16/tpbm-meta-analysis/docs').rglob('*.md'))
hits=[]
for p in files:
 for i,line in enumerate(p.read_text(encoding='utf-8-sig').splitlines(),1):
  for key,pat in patterns.items():
   if re.search(pat,line,re.I):hits.append(dict(file=str(p.relative_to(B)),line=i,category=key,text=line[:1200],interpretation='Review in context: preserved history is allowed; current claims need correction'))
for p in (B/'Publication_Package_2026-09-16').glob('*.docx'):
 with zipfile.ZipFile(p) as z:
  root=ET.fromstring(z.read('word/document.xml'));ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
  pars=[''.join(x.itertext()) for x in root.findall('.//w:t',ns)]
  text='\n'.join(pars);(A/'Sources'/(p.stem+'_text.txt')).write_text(text,encoding='utf-8')
  for i,line in enumerate(pars,1):
   for key,pat in patterns.items():
    if re.search(pat,line,re.I):hits.append(dict(file=str(p.relative_to(B)),line=i,category=key,text=line[:1200],interpretation='DOCX text-run index; compare against live manuscript before amendment'))
write('manuscript_package_scan.csv',hits)
print('EEG independently gated by construct/band: max independent k',max(x['independent_upper_bound'] for x in rows),'; 212 reproduced records match; manuscript scan hits',len(hits))
