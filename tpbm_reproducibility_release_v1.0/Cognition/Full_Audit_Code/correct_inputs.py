from pathlib import Path
import csv,math,shutil
A=Path(__file__).resolve().parent;W=A/'Working_corrected'
for d in ['Inputs','Outputs','Logs']:(W/d).mkdir(parents=True,exist_ok=True)
for p in (A/'Inputs').glob('*.csv'):shutil.copy2(p,W/'Inputs'/p.name)
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def write(p,rows):
 with p.open('w',newline='',encoding='utf-8-sig') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
changes=[]
effect_paths=[A/'Outputs'/f'{kind}_r{r}.csv' for kind in ['harmonization','all_outcomes','external'] for r in ['0.2','0.5','0.8']]
for p in effect_paths+list((A/'Inputs').glob('*specification_v2.csv')):
 rows=read(p)
 if not rows or 'cohort_id' not in rows[0]:continue
 for z in rows:
  if z['cohort_id']=='COG-HWANG-2016':
   for key,val in [('n1','15'),('n0','15'),('comparator_intensity','Low/nonzero-output sham')]:
    changes.append(dict(file=p.name,cohort_id=z['cohort_id'],outcome_id=z['outcome_id'],field=key,old=z[key],new=val,evidence='Hwang paper Participants and Tables 1-2: n=15 each; sham 5 seconds per minute'))
    z[key]=val
   if 'hedges_g' in z:
    df=28;J=math.exp(math.lgamma(df/2)-.5*math.log(df/2)-math.lgamma((df-1)/2));sp=math.sqrt((float(z['sd1'])**2+float(z['sd0'])**2)/2);g=J*float(z['sign'])*(float(z['m1'])-float(z['m0']))/sp;v=2/15+g*g/60
    z.update(hedges_g=g,sampling_variance=v,audit_df=df,audit_J=J,audit_standardizer=sp)
  if z['cohort_id'] in ['COG-DOUGAL-2021','COG-CHAN-2021-DIFFICULT','COG-DEOLIVEIRA-2024']:
   evidence={'COG-DOUGAL-2021':'Maculume funding and majority shareholding, Disclosure/Funding','COG-CHAN-2021-DIFFICULT':'Hamblin advisory boards including Vielight and JOOVV, Competing interests','COG-DEOLIVEIRA-2024':'Cassano PBM industry funding, consultation, shareholding, patents, Declaration of competing interest'}[z['cohort_id']]
   changes.append(dict(file=p.name,cohort_id=z['cohort_id'],outcome_id=z['outcome_id'],field='industry_status',old=z['industry_status'],new='Documented industry association',evidence=evidence));z['industry_status']='Documented industry association'
 write(W/('Outputs' if p.parent.name=='Outputs' else 'Inputs')/p.name,rows)
write(A/'Outputs/correction_log.csv',changes)
print('Corrected Hwang sample sizes/sham; three documented industry associations. Original inputs unchanged.')
