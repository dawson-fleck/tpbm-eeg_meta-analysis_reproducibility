from pathlib import Path
import csv,json,math,hashlib,zipfile,sys,re,shutil
A=Path(__file__).resolve().parent; B=A.parent; V=B/'AQ4_Recovery_v2_2026-09-16'
for d in ['Inputs','Outputs','Logs','Sources','Source_text','EEG_replication/Scripts','EEG_replication/Reproducibility/Source_snapshots','EEG_replication/Outputs','EEG_replication/Inputs']: (A/d).mkdir(parents=True,exist_ok=True)
def read(p): return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def write(p,rows):
 if not rows:return
 with p.open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
manifest=[]
def snap(p,dest):
 dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 manifest.append(dict(original=str(p),snapshot=str(dest.relative_to(A)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
for p in (V/'Inputs').glob('*.csv'):snap(p,A/'Inputs'/p.name)
for p in (V/'Scripts').glob('*'):snap(p,A/'Sources'/'Inspected_scripts'/p.name)
for p in (B/'EEG/Scripts').glob('*'):snap(p,A/'EEG_replication/Scripts'/p.name)
for p in (B/'EEG/Reproducibility/Source_snapshots').glob('*'):snap(p,A/'EEG_replication/Reproducibility/Source_snapshots'/p.name)
for name,p in [('historical_coding.csv',B/'Cognition/Approved_plan_outputs/analysis_coding.csv'),('locked.csv',B/'Cognition/Cognition_Primary_Input_locked_2026-08-28.csv'),('historical_mmse.csv',B/'Cognition/Approved_plan_outputs/mmse_raw_input.csv')]:snap(p,A/'Inputs'/name)
for p in (V/'Outputs').glob('*.csv'):snap(p,A/'Sources'/'Prior_outputs'/p.name)
for p in (B/'AQ4_Correction_2026-09-16/Source_snapshots').glob('*'):
 if p.suffix.lower() in ['.txt','.json','.md','.csv']:snap(p,A/'Sources'/'Prior_source_records'/p.name)
bundle=json.loads((A/'Sources/Prior_source_records/extraction_fulltext_bundle.json').read_text(encoding='utf-8-sig'))
for x in bundle:
 text=x.get('result',{}).get('structuredContent',{}).get('content','')
 if text:(A/'Source_text'/(re.sub(r'[^\w.-]','_',x['title'])+'.txt')).write_text(text,encoding='utf-8')
write(A/'Logs/input_manifest.csv',manifest)
archives=[]
for name in ['Cognition','EEG']:
 with zipfile.ZipFile(B/(name+'.zip')) as z:
  for info in z.infolist():
   if info.is_dir():continue
   rel=info.filename.replace('\\','/');p=B/rel
   if not p.exists():p=B/name/rel
   # CRC tests archive integrity without extracting or running bundled code.
   content=z.read(info);h=hashlib.sha256(content).hexdigest()
   archives.append(dict(archive=name,entry=rel,size=len(content),sha256=h,local_match=p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==h))
write(A/'Logs/archive_inventory.csv',archives)
def J(df):return math.exp(math.lgamma(df/2)-.5*math.log(df/2)-math.lgamma((df-1)/2))
def calc(z,r=.5):
 def n(k):return float(z[k]) if z.get(k) else float('nan')
 a,b=n('n1'),n('n0');route=z['route'];df=a+b-2;extra={}
 if route in ['SMD','SMD_t','SMD_d']:
  den=math.sqrt(((a-1)*n('sd1')**2+(b-1)*n('sd0')**2)/df) if route=='SMD' else float('nan')
  d=(n('m1')-n('m0'))/den if route=='SMD' else n('t')*math.sqrt(1/a+1/b) if route=='SMD_t' else n('reported_d')
  g=J(df)*d;v=1/a+1/b+g*g/(2*(a+b));extra=dict(df=str(df),J=str(J(df)),standardizer=den)
 elif route=='SMCRPH':
  s1,s0=n('sd1'),n('sd0');sp2=(s1*s1+s0*s0)/2;df=2*(a-1)/(1+r*r)
  g=J(df)*(n('m1')-n('m0'))/math.sqrt(sp2)
  v=(s1*s1+s0*s0-2*r*s1*s0)/(a*sp2)+g*g*(s1**4+s0**4+2*r*r*s1*s1*s0*s0)/(8*sp2*sp2*a)
  extra=dict(df=str(df),J=str(J(df)),standardizer=math.sqrt(sp2))
 else:
  ga=J(a-1)*n('change1')/n('preSD1');gb=J(b-1)*n('change0')/n('preSD0');g=ga-gb
  if n('imputed_r')==1:
   s1sq=n('preSD1')**2+n('sd1')**2-2*r*n('preSD1')*n('sd1');s0sq=n('preSD0')**2+n('sd0')**2-2*r*n('preSD0')*n('sd0')
  else:s1sq=n('changeSD1')**2;s0sq=n('changeSD0')**2
  v=s1sq/(a*n('preSD1')**2)+ga*ga/(2*a)+s0sq/(b*n('preSD0')**2)+gb*gb/(2*b)
  extra=dict(df=f'{a-1};{b-1}',J=f'{J(a-1)};{J(b-1)}',standardizer=f'{n("preSD1")};{n("preSD0")}')
 return dict(g=g*n('sign'),v=v,**extra)
if __name__=='__main__':
 checks=[]
 for kind in ['harmonization','all_outcomes','external']:
  rows=read(A/'Inputs'/f'{kind}_specification_v2.csv')
  for r in [.2,.5,.8]:
   out=[]
   prior=read(A/'Sources/Prior_outputs'/('study_level_harmonization_audit.csv' if kind=='harmonization' else f'{"all_outcomes" if kind=="all_outcomes" else "external_harmonization"}_audit.csv'))
   for z in rows:
    if z['include']!='1':continue
    e=calc(z,r);out.append(dict(z,hedges_g=e['g'],sampling_variance=e['v'],audit_df=e['df'],audit_J=e['J'],audit_standardizer=e['standardizer'],paired_r=r))
    if r==.5:
     p=next(x for x in prior if x['cohort_id']==z['cohort_id'] and x['outcome_id']==z['outcome_id'])
     checks.append(dict(kind=kind,cohort_id=z['cohort_id'],outcome_id=z['outcome_id'],g=e['g'],v=e['v'],g_error=e['g']-float(p['hedges_g']),v_error=e['v']-float(p['sampling_variance']),arithmetic_pass=abs(e['g']-float(p['hedges_g']))<1e-10 and abs(e['v']-float(p['sampling_variance']))<1e-10,source_verification='Separate source audit required'))
   write(A/'Outputs'/f'{kind}_r{r}.csv',out)
 write(A/'Outputs/effect_arithmetic_checks.csv',checks)
 tang=[(.43,.12),(.48,.12),(.48,.11),(.36,.05),(.43,.11),(.34,.04)]
 def combine(arms):
  n=8*len(arms);m=sum(x[0] for x in arms)/len(arms);s=math.sqrt(sum(7*x[1]**2+8*(x[0]-m)**2 for x in arms)/(n-1));return n,m,s
 tg=[]
 for name,aa,bb in [('all_active',tang,[(.39,.11)]),('all_PW',[tang[i] for i in [1,2,4,5]],[(.39,.11)]),('CW',[tang[i] for i in [0,3]],[(.39,.11)]),('PW_vs_CW',[tang[i] for i in [1,2,4,5]],[tang[i] for i in [0,3]]),('historical_selected_3_PW',[tang[i] for i in [1,2,4]],[(.39,.11)])]:
  a,m,s=combine(aa);b,m0,s0=combine(bb);df=a+b-2;g=J(df)*(m-m0)/math.sqrt(((a-1)*s*s+(b-1)*s0*s0)/df);v=1/a+1/b+g*g/(2*(a+b))
  tg.append(dict(contrast=name,n1=a,n0=b,mean1=m,sd1=s,g=g,v=v,lo=g-1.95996398454*math.sqrt(v),hi=g+1.95996398454*math.sqrt(v),variance='SMD LS: 1/n1+1/n0+g^2/(2*(n1+n0))'))
 write(A/'Outputs/Tang_corrected_contrasts.csv',tg)
 print('Independent effect checks:',len(checks),'passed:',sum(x['arithmetic_pass'] for x in checks),'source texts',len(list((A/'Source_text').glob('*'))),'archive entries',len(archives))
 (A/'Logs/python_version.txt').write_text(sys.version,encoding='utf-8')
