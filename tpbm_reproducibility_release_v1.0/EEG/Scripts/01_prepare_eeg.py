"""EEG audit and derived study-level inputs. Never changes source snapshots."""
from pathlib import Path
import csv,json,math,re,hashlib,collections,statistics
P=Path(__file__).resolve().parents[1];S=P/'Reproducibility'/'Source_snapshots';O=P/'Outputs';I=P/'Inputs'
O.mkdir(exist_ok=True);I.mkdir(exist_ok=True)
def write(name,rows,fields=None,root=O):
 with (root/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
snapshot=json.loads((S/'EEG_master_numeric_snapshot.json').read_text(encoding='utf-8-sig'))
rows=snapshot['tabs']['EEG Analysis Input']['values'];headers=rows[0]
records=[dict(source_row=i+2,**dict(zip(headers,r+[None]*(len(headers)-len(r))))) for i,r in enumerate(rows[1:]) if r and r[0]]
write('EEG_source_snapshot_2026-09-16.csv',records,root=I)
def number(v):
 try:return float(v)
 except (TypeError,ValueError):return None
def code(r):
 s=r['Study'];year=int(r['Year']);m=r['Band / metric'];t=r['Timing / condition'];family=r['EEG family']
 key=('Wang'+str(year)) if s=='Wang et al.' else ('Zhao' if s.startswith('Zhao C') else s.split()[0])
 base={'Zhao':('ZHAO-C-2022','CDA amplitude set-size contrast','task visual working memory','task endpoint','posterior CDA','ERP voltage',2),
 'Spera':('SPERA-2021','scalp spectral power','eyes closed' if 'closed' in t else 'eyes open','immediate post','scalp/frontal-central','scalp PSD; normalization not harmonized',1),
 'Zomorrodi':('ZOMORRODI-2019','scalp spectral power','eyes closed','immediate post','19-electrode global','absolute-power post/pre ratio',1),
 'Mehdizadeh':('MEHDIZADEH-2025','scalp spectral power','not verified in this snapshot','1-week post','Fp1','absolute delta power',1),
 'He':('HE-2026','microstate C mean duration','eyes closed','immediate post','whole-scalp microstate','relative change; paired dz',1),
 'Wang2019':('WANG-2019','scalp spectral power','eyes open','during T8','nominal Fp2','baseline-normalized scalp PSD',1),
 'Chaudhari':('CHAUDHARI-2023','source network power','rest/task combined by source analysis','repeated treatment '+('TP1' if 'TP1' in t else 'TP2'),'study-defined source network','S8-S1 normalized network power',1),
 'Ghaderi':('GHADERI-2021','graph '+m.split(' / ')[-1],'rest; eye state not verified','immediate post','global graph','post/pre relative change',1),
 'Wang2022':('UTA-1064-EEG-49','source network power','eyes closed','recovery' if 'recovery' in t.lower() else 'during '+t,'study-defined source network','paired sham-subtracted normalized power',1),
 'Bastola':('UTSW-1064-MEGEEG-25','directional PTE','eyes open','immediate post','source edge '+m.split('PTE ')[-1],'author-defined marginal-SD d_av',1)}
 if key not in base:return None
 cid,construct,state,timing,scope,normalization,units=base[key]
 band=m.split(' / ')[0].split()[0].lower() if family not in ['ERP','Microstate/network'] else 'not applicable'
 if key in ['Zhao','He']:band='not applicable'
 if key=='Mehdizadeh':band='delta'
 status='QUARANTINED: source design/statistic conflict' if key=='Zomorrodi' else 'Available study-level estimate; source/working assumptions retained'
 return dict(cluster_id=cid,study_key=key,construct=construct,band=band,state=state,timing_group=timing,anatomical_scope=scope,normalization=normalization,independent_experiments_in_cluster=units,quantitative_status=status,eligible_for_new_pool=int(key!='Zomorrodi'),digitized=int(key in ['Chaudhari','Wang2019','Wang2022']),fixed_order=int(key in ['Spera','Wang2019']),mixed_route=int(key=='Zomorrodi'),variance_approximation=int(key in ['Chaudhari','Wang2019','Bastola']),source_conflict=int(key=='Zomorrodi'))
effects=[];notnum=[];links=[]
for r in records:
 g=number(r['Hedges g / Fisher z']);v=number(r['Sampling variance'])
 if 'relationship' in r['EEG family'].lower():links.append(r);continue
 if g is None or v is None:notnum.append(r);continue
 assert math.isfinite(g) and math.isfinite(v) and v>0
 c=code(r);assert c is not None,(r['Study'],r['Year'])
 effects.append(dict(effect_id=f"EEG-R{r['source_row']:03d}",source_row=r['source_row'],study=f"{r['Study']} {r['Year']}",metric=r['Band / metric'],g=g,vi=v,**c,n_active_or_paired=r['n active / paired'],n_control=r['n control'],source_effect_route=r['Effect route'],source_tier=r['Analysis tier'],source_design=r['Design'],source_direction=r['Direction'],source_overlap=r['Independence / overlap note'],source_audit=r['Audit status']))
assert len(effects)==212 and len({x['cluster_id'] for x in effects})==10
assert len({x['effect_id'] for x in effects})==len(effects)
write('EEG_effects_audited.csv',effects,root=I)
write('EEG_source_rows_without_effect.csv',notnum)
write('EEG_cognition_association_source.csv',links)
groups=collections.defaultdict(list)
for r in effects:
 key=tuple(r[x] for x in ['construct','band','state','timing_group','anatomical_scope','normalization'])
 groups[key].append(r)
gates=[]
for idx,(key,rs) in enumerate(sorted(groups.items()),1):
 viable=[x for x in rs if x['eligible_for_new_pool']]
 clusters={x['cluster_id'] for x in viable};units=sum(max(y['independent_experiments_in_cluster'] for y in viable if y['cluster_id']==c) for c in clusters)
 gates.append(dict(stratum_id=f'EEG-S{idx:03d}',**dict(zip(['construct','band','state','timing','scope','normalization'],key)),source_effect_rows=len(rs),available_effect_rows=len(viable),analysis_clusters=len(clusters),independent_datasets_upper_bound=units,studies='; '.join(sorted({x['study'] for x in rs})),decision='NOT POOLED',reason='Source effect quarantined' if not viable else 'Fewer than 3 compatible independent datasets; dependent rows do not increase k'))
 assert units<3, 'A potentially eligible family requires explicit reviewed model specification'
write('EEG_compatibility_gates.csv',gates)
clusters=[]
for c in sorted({x['cluster_id'] for x in effects}):
 rs=[x for x in effects if x['cluster_id']==c];a=rs[0]
 clusters.append(dict(cluster_id=c,study=a['study'],source_effect_rows=len(rs),available_effect_rows=sum(x['eligible_for_new_pool'] for x in rs),independent_experiments=a['independent_experiments_in_cluster'],families='; '.join(sorted({x['construct'] for x in rs})),state='; '.join(sorted({x['state'] for x in rs})),timing='; '.join(sorted({x['timing_group'] for x in rs})),status=a['quantitative_status'],note='Multiple effects are dependent; no overall EEG mean is defined'))
write('EEG_cluster_inventory.csv',clusters)

# Reconstruct recorded calculations without silently changing stored source effects.
raw=list(csv.DictReader((S/'Chaudhari_digitized.csv').open(encoding='utf-8-sig')))
audit=[];sens=[]
def J(df):return 1-3/(4*df-1)
def check(effect,g,v,route,tol=1e-7):
 audit.append(dict(effect_id=effect['effect_id'],source_row=effect['source_row'],study=effect['study'],route=route,source_g=effect['g'],recomputed_g=g,abs_g_difference=abs(effect['g']-g),source_variance=effect['vi'],recomputed_variance=v,abs_variance_difference=abs(effect['vi']-v),tolerance=tol,passed=abs(effect['g']-g)<tol and abs(effect['vi']-v)<tol,note='Agreement verifies arithmetic of supplied values, not original extraction or scientific validity'))
for e in effects:
 key=e['study_key'];g=e['g'];v=e['vi']
 if key=='Chaudhari':
  net=int(re.search(r'(?:network | N)(\d+)',e['metric']).group(1));tp=e['timing_group'][-3:]
  a=next(x for x in raw if int(x['network'])==net and x['TP']==tp and x['band']==e['band'])
  mu=float(a['tpbm_mean'])-float(a['sham_mean']);se1=float(a['tpbm_sem']);se0=float(a['sham_sem'])
  calc=J(14)*mu/math.sqrt((7*se1**2*8+7*se0**2*8)/14)
  check(e,calc,1/8+1/8+calc*calc/28,'Digitized group means and SEM; working 8/8')
  g79=J(14)*mu/math.sqrt((6*se1**2*7+8*se0**2*9)/14);v79=1/7+1/9+g79*g79/28
  sens.append(dict(effect_id=e['effect_id'],study=e['study'],band=e['band'],metric=e['metric'],timing=e['timing_group'],scenario='7 active / 9 sham instead of 8/8',reference_g=g,reference_vi=v,sensitivity_g=g79,sensitivity_vi=v79,change_in_g=g79-g,raw_mean_difference=mu,raw_mean_difference_variance=se1**2+se0**2,note='Reconvert digitized SEM to SD using 7/9; no pooled inference; matched longitudinal n remains uncertain'))
 elif key=='Wang2022':
  m=re.search(r'dNP=([\-\d.]+)%; SEM=([\d.]+)%',e['source_effect_route']);assert m
  dz=float(m[1])/(float(m[2])*math.sqrt(44));calc=J(43)*dz
  check(e,calc,J(43)**2*(1/44+dz*dz/88),'Rounded digitized sham-subtracted mean/SEM; paired dz',tol=.0005)
 elif key=='Spera':
  n=7 if 'eyes closed'==e['state'] else 8;t=3.61 if n==7 else (3.02 if e['band']=='gamma' else 2.91)
  calc=J(n-1)*t/math.sqrt(n);check(e,calc,1/n+calc*calc/(2*(n-1)),'Reported paired t; recorded unscaled-leading variance')
 elif key=='Bastola':
  ds=[.68,.74,.82,.46,.58];which=[x for x in effects if x['study_key']=='Bastola'].index(e);calc=J(24)*ds[which]
  check(e,calc,2/25+calc*calc/96,'Author-defined d_av per extraction; original email not retrieved')
 elif key=='Wang2019':
  d=1.45 if e['band']=='alpha' else 1.48;calc=J(32)*d
  check(e,calc,J(32)**2*(2/17)+calc*calc/64,'Digitized reported d; recorded independent working variance')
 elif key=='He':
  sd=math.sqrt(.4066801889**2+.1007375143**2-2*.141277823*.4066801889*.1007375143)
  dz=(.2539416462-.007067451)/sd;calc=J(28)*dz
  check(e,calc,J(28)**2*(1/29+dz*dz/58),'Master-transcribed author paired summary; raw arrays not retrieved',tol=1e-5)
 elif key=='Ghaderi':
  ts={('beta2','clustering coefficient'):-2.37,('beta2','local efficiency'):-2.32,('beta2','graph energy'):-1.65,('beta2','Shannon entropy'):1.8,('beta4','global efficiency'):-2.09,('beta4','local efficiency'):-1.96,('beta4','graph energy'):-1.97,('beta4','Shannon entropy'):2.16}
  t=ts[(e['band'],e['metric'].split(' / ')[1])];calc=J(34)*t*math.sqrt(1/19+1/17)
  check(e,calc,J(34)**2*(1/19+1/17)+calc*calc/68,'Recorded permutation t treated as ordinary between-group t; conditional route')
write('EEG_effect_reconstruction_checks.csv',audit)
assert all(a['passed'] for a in audit),[a for a in audit if not a['passed']]
write('EEG_Chaudhari_sample_size_sensitivity.csv',sens)
excluded=[e for e in effects if not e['eligible_for_new_pool']]
write('EEG_quarantined_source_effects.csv',excluded)
scenario=[]
for name,criterion in [('All nonquarantined',lambda x:True),('Exclude digitized',lambda x:not x['digitized']),('Exclude fixed-order/high-RoB',lambda x:not x['fixed_order']),('Exclude working variance approximations',lambda x:not x['variance_approximation']),('Exclude multimodal Bastola PTE',lambda x:x['study_key']!='Bastola'),('Transcranial-only',lambda x:not x['mixed_route'])]:
 rr=[e for e in effects if e['eligible_for_new_pool'] and criterion(e)]
 scenario.append(dict(scenario=name,available_effect_rows=len(rr),clusters=len({e['cluster_id'] for e in rr}),pooled_model='NOT FIT',reason='Compatibility threshold fails before and after restriction; clusters across different constructs cannot be pooled'))
write('EEG_exclusion_sensitivity_inventory.csv',scenario)
summary=dict(source_rows=len(records),numeric_dynamics_rows=len(effects),source_clusters=len(clusters),quarantined_rows=len(excluded),available_rows=len(effects)-len(excluded),available_clusters=9,compatibility_strata=len(gates),eligible_pools=0,reconstruction_checks=len(audit),sample_size_sensitivity_effects=len(sens),association_records=len(links))
(O/'EEG_audit_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
