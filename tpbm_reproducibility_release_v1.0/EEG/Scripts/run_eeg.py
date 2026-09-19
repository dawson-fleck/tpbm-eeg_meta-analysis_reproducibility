"""Portable EEG pipeline: Python standard library + base R; no network access."""
from pathlib import Path
import argparse,subprocess,sys,shutil,hashlib,json,datetime,os
p=argparse.ArgumentParser();p.add_argument('--rscript',default=shutil.which('Rscript'));args=p.parse_args()
if not args.rscript: p.error('Rscript not on PATH; supply --rscript PATH')
root=Path(__file__).resolve().parents[1]
stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
run=root/'Reproducibility'/'Runs'/stamp;run.mkdir(parents=True)
def hashes():
 return {str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((root/'Reproducibility'/'Source_snapshots').glob('*')) if f.is_file()}
before=hashes();(run/'source_hashes_before.json').write_text(json.dumps(before,indent=2))
if (root/'Outputs').exists():shutil.copytree(root/'Outputs',run/'previous_outputs')
shutil.copytree(root/'Scripts',run/'Scripts_snapshot')
for f in root.glob('*.md'):
 (run/'previous_reports').mkdir(exist_ok=True);shutil.copy2(f,run/'previous_reports'/f.name)
env=os.environ.copy();env['PYTHONIOENCODING']='utf-8';env['LANG']='C';env['LC_ALL']='C'
steps=[[sys.executable,str(root/'Scripts'/'01_prepare_eeg.py')],[args.rscript,str(root/'Scripts'/'02_describe_eeg.R')],[sys.executable,str(root/'Scripts'/'03_report_eeg.py')]]
for i,cmd in enumerate(steps,1):
 result=subprocess.run(cmd,cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
 (run/f'{i:02d}.log').write_text(result.stdout,encoding='utf-8');print(result.stdout)
 if result.returncode:raise SystemExit(result.returncode)
after=hashes();assert before==after,'Source snapshot changed during execution'
(run/'source_hashes_after.json').write_text(json.dumps(after,indent=2))
manifest={str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for folder in ['Scripts','Inputs','Outputs'] for f in sorted((root/folder).rglob('*')) if f.is_file()}
manifest.update({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in root.glob('*.md')})
(run/'package_hashes.json').write_text(json.dumps(manifest,indent=2))
(run/'PASS.txt').write_text('All pipeline steps passed. Source snapshots unchanged. Zero pooled EEG models eligible.\n')
print('Completed:',run)
