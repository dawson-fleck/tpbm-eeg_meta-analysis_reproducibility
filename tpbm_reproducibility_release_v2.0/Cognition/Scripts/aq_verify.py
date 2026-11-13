"""Independent Python effect and REML/HK checks; does not call R."""
from pathlib import Path
import csv,math,sys,json,hashlib
import numpy as np
P=Path(__file__).resolve().parents[1]

from scipy.optimize import minimize_scalar
from scipy.stats import t
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def J(df):return math.exp(math.lgamma(df/2)-.5*math.log(df/2)-math.lgamma((df-1)/2))
checks=[]
for r in [.2,.5,.8]:
 for z in read(P/'Inputs'/f'harmonized_cognition_v3_r{r}.csv'):
  def n(k):return float(z[k]) if z[k] else math.nan
  a,b=n('n1'),n('n0');route=z['route'];df=a+b-2
  if route in ['SMD','SMD_t','SMD_d']:
   d=(n('m1')-n('m0'))/math.sqrt(((a-1)*n('sd1')**2+(b-1)*n('sd0')**2)/df) if route=='SMD' else n('t')*math.sqrt(1/a+1/b) if route=='SMD_t' else n('reported_d')
   g=J(df)*d;v=1/a+1/b+g*g/(2*(a+b))
  elif route=='SMCRPH':
   s1,s0=n('sd1'),n('sd0');sp2=(s1*s1+s0*s0)/2
   g=J(2*(a-1)/(1+r*r))*(n('m1')-n('m0'))/math.sqrt(sp2)
   v=(s1*s1+s0*s0-2*r*s1*s0)/(a*sp2)+g*g*(s1**4+s0**4+2*r*r*s1*s1*s0*s0)/(8*sp2*sp2*a)
  else:
   ga=J(a-1)*n('change1')/n('preSD1');gb=J(b-1)*n('change0')/n('preSD0');g=ga-gb
   if n('imputed_r')==1:
    s1sq=n('preSD1')**2+n('sd1')**2-2*r*n('preSD1')*n('sd1');s0sq=n('preSD0')**2+n('sd0')**2-2*r*n('preSD0')*n('sd0')
   else:s1sq=n('changeSD1')**2;s0sq=n('changeSD0')**2
   v=s1sq/(a*n('preSD1')**2)+ga*ga/(2*a)+s0sq/(b*n('preSD0')**2)+gb*gb/(2*b)
  g*=n('sign');dg=abs(g-n('hedges_g'));dv=abs(v-n('sampling_variance'))
  assert dg<1e-10 and dv<1e-10,(z['cohort_id'],r,g,v,dg,dv)
  checks.append(dict(cohort_id=z['cohort_id'],r=r,g_abs_error=dg,vi_abs_error=dv))
models={x['id']:x for x in read(P/'Outputs/all_model_results.csv')}
membership=read(P/'Outputs/model_membership.csv');pooled=[]
for key in ['new__Overall cognition','new__Memory','new__Global cognition','new__Executive / sustained attention','old__Overall cognition']:
 rows=[x for x in membership if x['id']==key];y=np.array([float(x['yi']) for x in rows]);v=np.array([float(x['vi']) for x in rows]);k=len(y)
 def obj(tau):
  w=1/(v+tau);mu=np.sum(w*y)/sum(w)
  return .5*(np.log(v+tau).sum()+math.log(sum(w))+np.sum(w*(y-mu)**2))
 fit=minimize_scalar(obj,bounds=(0,5),method='bounded',options={'xatol':1e-13});tau=fit.x if fit.fun<obj(0) else 0
 w=1/(v+tau);mu=sum(w*y)/sum(w);se=math.sqrt(sum(w*(y-mu)**2)/(k-1)/sum(w));q=t.ppf(.975,k-1)
 vals={'g':mu,'tau2':tau,'se':se,'ci_low':mu-q*se,'ci_high':mu+q*se}
 errs={n:abs(x-float(models[key][n])) for n,x in vals.items()}
 assert max(errs.values())<1e-5,(key,errs)
 pooled.append({'id':key,**vals,'max_R_difference':max(errs.values())})
locked=P/'Original_snapshot/Cognition_Primary_Input_locked_2026-08-28.csv'
locked_verified=False
if locked.exists():
 assert hashlib.sha256(locked.read_bytes()).hexdigest()=='857b679893fa3545a348a229285f8ec7de0762edd8ba311dabf9fba61ea40156'
 locked_verified=True
report={'status':'PASS','effect_checks':checks,'independent_REML_HK':pooled,'internal_source_snapshot_verified':locked_verified,'public_source_snapshot_note':'Internal source snapshot is outside the scope of the public GitHub release.','python':sys.version,'numpy':np.__version__}
(P/'Logs/independent_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
scope='private source snapshot verified' if locked_verified else 'private source snapshot intentionally omitted'
print(f'PASS: {len(checks)} independent v3 effect/variance checks, {len(pooled)} independent REML/HK models, {scope}.')
