"""Independent REML and unmodified HK implementation using only Python stdlib.
Student t probabilities use incomplete beta continued fractions; no R calls.
"""
from pathlib import Path
import math,csv,sys
A=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def beta_cf(a,b,x):
 qab=a+b;qap=a+1;qam=a-1;c=1.;d=1-qab*x/qap;d=1/max(d,1e-300);h=d
 for m in range(1,401):
  aa=m*(b-m)*x/((qam+2*m)*(a+2*m));d=1+aa*d;c=1+aa/c
  if abs(d)<1e-300:d=1e-300
  if abs(c)<1e-300:c=1e-300
  d=1/d;h*=d*c;aa=-(a+m)*(qab+m)*x/((a+2*m)*(qap+2*m));d=1+aa*d;c=1+aa/c
  if abs(d)<1e-300:d=1e-300
  if abs(c)<1e-300:c=1e-300
  d=1/d;delta=d*c;h*=delta
  if abs(delta-1)<3e-14:break
 return h
def ibeta(a,b,x):
 if x<=0:return 0.
 if x>=1:return 1.
 bt=math.exp(math.lgamma(a+b)-math.lgamma(a)-math.lgamma(b)+a*math.log(x)+b*math.log1p(-x))
 return bt*beta_cf(a,b,x)/a if x<(a+1)/(a+b+2) else 1-bt*beta_cf(b,a,1-x)/b
def p_t(t,df):return ibeta(df/2,.5,df/(df+t*t))
def qt(df):
 lo,hi=0.,1000.
 for _ in range(100):
  m=(lo+hi)/2
  if p_t(m,df)>.05:lo=m
  else:hi=m
 return (lo+hi)/2
def golden(fn):
 lo,hi=0.,10.;gr=(math.sqrt(5)-1)/2;c=hi-gr*(hi-lo);d=lo+gr*(hi-lo)
 for _ in range(160):
  if fn(c)<fn(d):hi=d;d=c;c=hi-gr*(hi-lo)
  else:lo=c;c=d;d=lo+gr*(hi-lo)
 m=(lo+hi)/2
 return m if fn(m)<fn(0) else 0.
def model(rows):
 y=[float(x['hedges_g']) for x in rows];v=[float(x['sampling_variance']) for x in rows];k=len(y)
 def f(tau):
  w=[1/(a+tau) for a in v];mu=sum(a*b for a,b in zip(w,y))/sum(w)
  return .5*(sum(math.log(a+tau) for a in v)+math.log(sum(w))+sum(a*(b-mu)**2 for a,b in zip(w,y)))
 tau=golden(f);w=[1/(a+tau) for a in v];mu=sum(a*b for a,b in zip(w,y))/sum(w);scale=sum(a*(b-mu)**2 for a,b in zip(w,y))/(k-1);se=math.sqrt(scale/sum(w));q=qt(k-1)
 u=[1/a for a in v];fixed=sum(a*b for a,b in zip(u,y))/sum(u);Q=sum(a*(b-fixed)**2 for a,b in zip(u,y));typ=(k-1)*sum(u)/(sum(u)**2-sum(a*a for a in u))
 return dict(k=k,g=mu,tau2=tau,se=se,p=p_t(mu/se,k-1),lo=mu-q*se,hi=mu+q*se,Q=Q,I2=100*tau/(tau+typ),pi_lo=mu-q*math.sqrt(tau+se*se) if k>=5 else '',pi_hi=mu+q*math.sqrt(tau+se*se) if k>=5 else '')
rows=read(A/'Outputs/harmonization_r0.5.csv');prior={x['model']:x for x in read(A/'Outputs/model_results.csv')};out=[]
for dom in ['Overall cognition','Memory','Global cognition','Executive / sustained attention']:
 rr=rows if dom=='Overall cognition' else [x for x in rows if x['domain']==dom];m=model(rr);p=prior['primary__'+dom];err=max(abs(val-float(p[key])) for key,val in m.items() if val!='');assert err<1e-5,(dom,err)
 out.append(dict(model=dom,**m,max_R_error=err))
with (A/'Outputs/independent_python_models.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
print('PASS: four independent Python REML/HK fits including t inference, heterogeneity and prediction intervals; max error',max(x['max_R_error'] for x in out))
