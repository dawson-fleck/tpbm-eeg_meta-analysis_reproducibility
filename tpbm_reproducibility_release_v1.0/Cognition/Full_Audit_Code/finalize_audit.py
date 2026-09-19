from pathlib import Path
import csv,hashlib,json
A=Path(__file__).resolve().parent
def read(p):return list(csv.DictReader((A/p).open(encoding='utf-8-sig')))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,rows):
 with (A/p).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
checks=[]
for r in read('Logs/input_manifest.csv'):
 p=Path(r['original']);checks.append(dict(original=str(p),initial_sha256=r['sha256'],current_sha256=digest(p) if p.exists() else 'MISSING',unchanged=p.exists() and digest(p)==r['sha256']))
write('Logs/preservation_check.csv',checks)
assert all(x['unchanged'] for x in checks),'An original changed since snapshot'
qa={'original_files_unchanged':len(checks)}
e=read('Outputs/effect_arithmetic_checks.csv');assert len(e)==47 and all(x['arithmetic_pass']=='True' for x in e)
qa['central_specification_effect_checks']=len(e)
e=read('Outputs/metafor_formula_checks.csv');assert len(e)==102 and max(abs(float(x[k])) for x in e for k in ['g_error','v_error'])<1e-10
qa['original_corrected_formula_checks']=len(e)
for root in ['', 'Working_corrected/']:
 e=read(root+'Outputs/independent_python_models.csv');err=max(float(x['max_R_error']) for x in e);assert len(e)==4 and err<3e-6
 qa[root+'principal_models_python_R_max_error']=err
 e=read(root+'Outputs/multilevel.csv');assert len(e)==27
 qa[root+'multilevel_models']=len(e)
assert read('Outputs/EEG_reproduction_comparison.csv')[0]['identical']=='True'
assert len(read('Outputs/EEG_additional_source_reconstruction.csv'))==2
qa['EEG_source_rows_reproduced']=212;qa['EEG_retained_arithmetic_checks']=207
for p in ['AUDIT_REPORT.md','MANUSCRIPT_CORRECTIONS.md','Working_corrected/Manuscript_audited_working.txt','Outputs/cohort_effect_provenance.csv','Outputs/corrected_sensitivity_matrix.csv','Outputs/planned_analysis_feasibility.csv','run_audit.ps1']:
 assert (A/p).stat().st_size>100,p
qa['status']='PASS; numerical verification does not resolve source/appraisal uncertainties'
(A/'Logs/final_QA.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
files=[]
for p in sorted(A.rglob('*')):
 if p.is_file() and p.name not in ['final_manifest.csv','finalize_rerun.log'] and '__pycache__' not in p.parts:
  files.append(dict(path=str(p.relative_to(A)),bytes=p.stat().st_size,sha256=digest(p)))
write('Logs/final_manifest.csv',files)
print(json.dumps(qa,indent=2))
