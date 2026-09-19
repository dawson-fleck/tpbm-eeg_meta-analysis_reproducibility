from pathlib import Path
import csv,math
A=Path(__file__).resolve().parent
def J(n):return 1-3/(4*(n-1)-1)
gs=[J(n)*t/math.sqrt(n) for n,t in [(23,2.313),(18,2.506)]]
vs=[J(n)**2/n+g*g/(2*n) for n,g in zip([23,18],gs)]
z=sum(a/b for a,b in zip(gs,vs))/sum(1/b for b in vs);v=1/sum(1/b for b in vs)
g=(1-3/(4*28-1))*(33.24-65.81)/math.sqrt((20.13**2+24.08**2)/2);mv=2/15+g*g/56
rows=[dict(study='Zhao C 2022 CDA',g=z,v=v,source='ZhaoC_PDF.txt results: paired t(22)=2.313 and t(17)=2.506',limitation='Paired dz; not a marginal-SD cognition effect; rounded statistics'),dict(study='Mehdizadeh 2025 Fp1',g=g,v=mv,source='Mehdizadeh_paper.txt Table 2: 33.24 SD20.13 versus65.81 SD24.08 n15/15',limitation='Table labels adjusted means plus SD; ordinary independent SMD variance ignores uncertainty/covariance from ANCOVA; descriptive provisional')]
assert abs(z-.5082220213365676)<1e-10 and abs(v-.025707870436938063)<1e-10
assert abs(g-(-1.4279120663665306))<1e-10 and abs(mv-.1697428488561036)<1e-10
with (A/'Outputs/EEG_additional_source_reconstruction.csv').open('w',newline='',encoding='utf-8-sig') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
fz=(20*math.atanh(.446)+15*math.atanh(.563))/35
(A/'Outputs/EEG_association_check.txt').write_text(f'Zhao C independent experiments: r=.446 n23 and r=.563 n18. Fixed Fisher-z aggregate={fz:.12f}; variance={1/35:.12f}; r={math.tanh(fz):.6f}. Matches recorded extraction. Same-session association; not prospective validated prediction or adaptive trial.',encoding='utf-8')
print('PASS two additional EEG source reconstructions and within-paper Fisher-z check')
