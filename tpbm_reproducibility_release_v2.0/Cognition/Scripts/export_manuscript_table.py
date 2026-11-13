"""Export the current primary-domain and secondary-overall model table."""
from pathlib import Path
import csv
out=Path(__file__).resolve().parents[1]/'Outputs'
with (out/'all_model_results.csv').open(encoding='utf-8-sig') as source:
 rows=[row for row in csv.DictReader(source) if row['id'].startswith('new__')]
assert len(rows)==4
with (out/'Manuscript_Table_1.csv').open('w',newline='',encoding='utf-8') as target:
 writer=csv.DictWriter(target,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
print('PASS: manuscript table exported from the four current pooled models.')
