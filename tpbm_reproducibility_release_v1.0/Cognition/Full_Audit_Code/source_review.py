from pathlib import Path
import csv,json,re,sys
sys.stdout.reconfigure(encoding='utf-8')
A=Path(__file__).resolve().parent
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def write(p,rows):
 with p.open('w',newline='',encoding='utf-8-sig') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
names={'TANG-2023':'Tang_2023_completed.docx','HWANG-2016':'Hwang_et_al_2016_completed.docx','CHAN-2019-OLDER':'Chan_et_al_2019_completed.docx','DOUGAL-2021':'Dougal_et_al.2021','CHAN-2021-DIFFICULT':'Chan_et_al.2021','YANG-2024-LANGUAGE':'Yang_et_al.','CHAN-2021-MCI':'Chan_et_al_2021_MCI_completed.docx','HASSAN-2026-STROKE':'Hassan_et_al_2026_completed','PENA-2026':'Pena_et_al_2026_completed','CHUN-2025-PILOT':'Chun_et_al.2025','LEE-2025-TBI':'Lee_2025_TBI.docx','DEOLIVEIRA-2024':'de_Oliveira_et_al_2024_completed.docx','BERMAN-2017-DEMENTIA':'Berman_2017_completed.docx','YANG-2025-OLDER-WM':'Yang_et_al_2025_completed','SABOURI-MOGHADAM-2017':None,'SALEHPOUR-2026-STAGE1-ADHD':'Salehpour_et_al_2026_completed','ZHAO-X-2022-SCD':'Zhao_et_al_2022_SCD_completed'}
patterns={'age':r'Mean age or age range|^Age:','wavelength':r'^Wavelength','device':r'^Device name|^Device:','pulse':r'^Pulsed or continuous|^Mode:','target':r'^Stimulation site|^Target:|^Target area','sessions':r'^Number of sessions|^Sessions:','sham':r'^Sham.*description|^Sham/control|^Sham:'}
rows=[]
for x in read(A/'Outputs/harmonization_r0.5.csv'):
 n=names[x['cohort_id'][4:]];p=A/'Source_text'/('DataExtraction_'+n+'.txt') if n else None;lines=[l.strip() for l in p.read_text(encoding='utf-8-sig').splitlines() if l.strip()] if p and p.exists() else []
 row=dict(cohort_id=x['cohort_id'],study=x['study'],source_file=str(p.relative_to(A)) if p else 'Sources/Prior_source_records/Sabouri_source_verified.txt')
 for key,pat in patterns.items():
  values=[]
  for i,l in enumerate(lines):
   if re.search(pat,re.sub(r'^\d+[.]?\s*','',l),re.I):values.append(' | '.join(lines[i:i+3]))
  row[key]=' || '.join(dict.fromkeys(values)) or 'Not resolved by automated field extraction; inspect source'
 rows.append(row)
write(A/'Outputs/treatment_parameter_source_inventory.csv',rows)
for r in rows:print(r['cohort_id'], '\n', '\n'.join(k+': '+r[k][:400] for k in ['age','wavelength','device','pulse','sessions']))
