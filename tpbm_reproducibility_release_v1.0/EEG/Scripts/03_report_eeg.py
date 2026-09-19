"""Generate evidence-linked Methods, Results and completion status from outputs."""
from pathlib import Path
import csv,json,math,statistics,sys,platform
P=Path(__file__).resolve().parents[1];O=P/'Outputs'
def read(n):return list(csv.DictReader((O/n).open(encoding='utf-8-sig')))
def save(n,t):(P/n).write_text(t.strip()+'\n',encoding='utf-8')
a=read('EEG_study_level_estimates.csv');s=read('EEG_Chaudhari_sensitivity_intervals.csv');cl=read('EEG_cluster_inventory.csv');gates=read('EEG_compatibility_gates.csv')
summary=json.loads((O/'EEG_audit_summary.json').read_text())
assert len(a)==207 and len(s)==120 and summary['eligible_pools']==0
protocol='https://docs.google.com/document/d/1_iQvlo_VGK5fbE9UCRpxMX9lsnfCy6kLZPTV5VFAICQ/edit'
master='https://docs.google.com/spreadsheets/d/1nL-UxVKVvhbF2QcCERRsBXHrWlpq9aQEzhIbh5sf8nY/edit'
methods=f'''# EEG Methods update — 16 September 2026

## Manuscript-ready draft

Electrophysiological outcomes were assessed separately from cognitive outcomes using the EEG provisions of Protocol v1.1 (17 July 2026). Quantitative synthesis required at least three independent datasets with compatible outcome construct, frequency band, recording state, treatment timing, anatomical representation and comparator. Scalp power, source-network power, event-related potential amplitude, microstate duration, phase-transfer entropy, coherence, graph measures and entropy were considered distinct outcome families. Absolute and relative power, resting and task recordings, during-treatment and post-treatment assessments, and controlled and uncontrolled effects were not combined. Multiple outcomes and companion publications from the same participants did not increase the number of independent datasets. A dependence-aware model was not used to combine incompatible outcomes or to compensate for insufficient independent datasets.

The master workbook EEG tab was frozen on 16 September 2026, retaining its original values and provenance. Report-level effects were mapped to analysis clusters, screened for compatibility, and audited against available extraction records and source information. The Wang 2021/Wang 2022/Shahdadian 2022/Truong 2023 reports were treated as one overlapping source cohort; the Bastola 2026/Pruitt 2024 reports were also linked. The Zhao 2022 CDA entry was a previously calculated within-paper aggregate of two independent experiments, retained as one reported estimate. That family therefore represented at most two independent experiments, below the three-dataset threshold.

Recorded standardized effects and variances were retained for descriptive presentation where their source route was available, with explicit flags for working assumptions. Small-sample corrections followed the recorded approximation J(df)=1−3/(4df−1). Arithmetic was reconstructed where sufficient inputs were available; agreement was distinguished from validation of the underlying extraction and estimator. Approximate unadjusted 95% study-level intervals were calculated as g ± 1.959964√v. These intervals were not multiplicity-adjusted and were not interpreted as evidence of clinical benefit. The positive direction denoted an increase in the specified EEG metric or the source-defined contrast, rather than a uniform favorable physiological response.

Chaudhari's 120 digitized network-by-band-by-time effects were reconstructed using the existing working sample sizes of eight active and eight sham participants. A sensitivity analysis used seven active and nine sham participants, reconverting the same standard errors to standard deviations under each allocation. All available cells were retained, including those without a source significance flag. Both allocations remained conditional because the matched longitudinal sample size was not resolved. No average across networks or time points was calculated.

Five Zomorrodi 2019 effects were quarantined after a source conflict was identified: the extraction used independent groups of ten participants per arm, whereas the paper described a 20-person crossover. The paper described Wilcoxon analyses while labeling the reported statistics as t. In the absence of author clarification, the existing effects were preserved in the audit record without quantitative interpretation; a paired-t conversion was not substituted.

No EEG family met the prespecified threshold for pooling. Accordingly, random-effects or fixed-effect synthesis, multilevel/robust-variance pooled models, heterogeneity estimates, prediction intervals, subgroup/meta-regression analyses, leave-one-out and influence analyses, pooled exclusion sensitivities, and funnel/asymmetry analyses were not performed. The single available EEG–cognition association record was retained for discussion only. Absence of an eligible pooled analysis was not interpreted as absence of an EEG effect.

The reproducible workflow used Python's standard library for snapshot processing and reporting and base R for study-level intervals, figures and independent numerical checks. The protocol's proposed jamovi workflow was not needed because no eligible EEG pooled model was fitted. Frozen source files were checked by SHA-256 before and after execution; derived outputs and execution logs were retained separately. The protocol postdated preliminary analyses, and earlier exploratory two-study EEG pools were not carried forward as final protocol-compliant estimates.

## Technical record for reproducibility

The recorded effect scales are not interchangeable. Paired dz uses the standard deviation of the within-person difference; d_av uses marginal standard deviations. Applying J does not make these denominators equivalent. The following routes reproduce the existing workbook and are not a newly harmonized common estimand.

| Source | Arithmetic reproduced | Limitation |
|---|---|---|
| Spera, 3 effects | g=J(n−1)t/√n; v=1/n+g²/[2(n−1)] | Fixed-order/high-risk design; recorded leading variance term is uncorrected |
| Wang 2019, 2 effects | g=J(32)d; v=J(32)²(2/17)+g²/64 | Paired design with independent-group working variance; not universally conservative |
| Chaudhari, 120 effects | SD=SEM√n; pooled SD; g=J(14)Δ/SDpooled; v=1/nA+1/nC+g²/28 | Digitization, longitudinal n and independence assumptions; source combines rest/task |
| Wang 2022, 66 effects | dz=mean difference/(SEM√44); g=J(43)dz; v=J(43)²[1/44+dz²/88] | Digitized mean/SEM rounded in the master; paired scale; selected alpha/gamma network inventory |
| Ghaderi, 8 effects | g=J(34)t√(1/19+1/17); v=J(34)²(1/19+1/17)+g²/68 | Conditional on reported permutation t being an ordinary two-sample t statistic; not independently established here |
| He, 1 effect | SDdiff=√(SDa²+SDs²−2rSDaSDs); dz=Δ/SDdiff; g=J(28)dz; v=J(28)²[1/29+dz²/58] | Uses master-transcribed author summary, r=.141277823; original paired arrays not retrieved |
| Bastola, 5 effects | g=J(24)d_av; v=2/25+g²/96 | Author-defined d_av per extraction; original email not retrieved; independent-group working variance; selected significant PTE edges and multimodal source analysis |
| Zhao CDA, 1 effect | Existing within-paper fixed aggregate retained | Experiment-level inputs not independently reconstructed in this EEG run |
| Mehdizadeh, 1 effect | Existing post-treatment adjusted-mean SMD retained | Underlying adjusted means/SDs not independently reconstructed in this run; provisional study-level presentation |

For He, the transcribed active/sham means were .2539416462/.007067451, SDs .4066801889/.1007375143, n=29. For Bastola the five d_av values were .68, .74, .82, .46 and .58, n=25. These values permit arithmetic reproduction but do not replace the original correspondence. Working independent-group variances were not described as automatically conservative, because paired correlations and marginal variances govern that comparison.

The Python audit reconstructed 205 effects. The two unreconstructed available effects were Zhao and Mehdizadeh; the other five were quarantined Zomorrodi rows. The reconstruction tolerance was 1e−7 for unrounded routes, 1e−5 for He's transcribed summary, and 0.0005 for Wang 2022's rounded digitized summaries. A separate R implementation verified four quantities for each of 120 Chaudhari effects: 8/8 g and variance and 7/9 g and variance (480 comparisons, tolerance 1e−7).

The 42 compatibility screening groups are deliberately coarse for within-study source networks: different network numbers remain dependent anatomical outcomes, and equal network numbers across papers are not assumed equivalent. Screening already fails the independent-dataset threshold at this coarser level; stricter anatomy or estimator harmonization could only reduce eligibility. These groups are not 42 completed meta-analyses. The Inputs field `eligible_for_new_pool` means not quarantined at source screening, not that pooling has been authorized; the compatibility gate must also pass.

Alternative imputed within-person correlations (.2/.5/.8) were not substituted for observed paired statistics. For effects with missing paired information, a correlation alone was insufficient to identify an exact paired variance without additional marginal SD/estimand information. These scenarios remain not estimable rather than being assigned fabricated covariances. Restriction inventories report how many rows/clusters survive digitization, fixed-order, working-variance and route exclusions; they are not pooled sensitivity estimates. Final risk-of-bias and certainty judgements require the review team's adjudication.

## Sources and provenance

- [Approved protocol]({protocol}), §§8.3, 11.6–11.9; local text snapshot in Reproducibility/Source_snapshots.
- [Master workbook]({master}), EEG Analysis Input, EEG Extraction Queue, Audit Decisions and Meta-Analysis Inclusion Map; numeric snapshot stored locally.
- [Zomorrodi source paper](https://www.nature.com/articles/s41598-019-42693-x), study design and Statistical Analyses sections; also checked against the local full-text PDF. User confirmed no clarification was available on 16 September 2026.
- Chaudhari digitization CSV and Chaudhari, Wang 2022, He and Bastola extraction documents: frozen text snapshots in Reproducibility/Source_snapshots. Their embedded provenance is preserved.
- The accessible “Run R Data Checks” conversation was inspected for a newer EEG specification; its accessible turns described cognition and handoff work. No newer explicit EEG pooling rule was located. This is a limitation of accessible history, not proof that no other discussion exists.
- Original Bastola/He author replies were not located in the available searches. No author messages were sent. Earlier He extraction text predates the later master-transcribed paired summary; the later master route was used and labeled.
'''
save('Methods_Update_EEG_2026-09-16.md',methods)
table='| Study/cluster | Source effects | Retained descriptive effects | Status |\n|---|---:|---:|---|\n'
for x in cl:table+=f"| {x['study']} | {x['source_effect_rows']} | {x['available_effect_rows']} | {'Quarantined' if int(x['available_effect_rows'])==0 else 'Study-level only'} |\n"
small='| Study | Metric | Recorded g | Approximate 95% interval |\n|---|---|---:|---|\n'
for x in a:
 if x['study_key'] in ['Chaudhari','Wang2022']:continue
 label=x['metric']+(' / '+x['state'] if x['study_key']=='Spera' else '')
 small+=f"| {x['study']} | {label} | {float(x['g']):.3f} | {float(x['ci_low']):.3f} to {float(x['ci_high']):.3f} |\n"
changes=[abs(float(x['change_in_g'])) for x in s]
ranges=[]
for key in ['Chaudhari','Wang2022']:
 v=[float(x['g']) for x in a if x['study_key']==key];ranges.append(f"{key}: {min(v):.3f} to {max(v):.3f}")
z=read('EEG_cognition_association_source.csv')[0];fz=float(z['Hedges g / Fisher z']);v=float(z['Sampling variance']);r=math.tanh(fz);lo=math.tanh(fz-1.95996398454*math.sqrt(v));hi=math.tanh(fz+1.95996398454*math.sqrt(v))
save('Results_Draft_EEG_2026-09-16.md',f'''# EEG Results draft — 16 September 2026

## Manuscript-ready draft

The frozen EEG analysis input contained 223 records: 212 numeric EEG-dynamics effects assigned to 10 analysis clusters, one EEG–cognition association record, and 10 records without an extractable quantitative effect. The numeric rows were dominated by dependent source-network outcomes from Chaudhari (120 effects) and Wang 2022 (66 effects). The number of effect rows therefore substantially exceeded the number of independent datasets. The Zhao CDA aggregate represented two experiments; analysis-cluster counts should not be substituted for a count of all underlying experiments or review-wide studies.

Source auditing identified a design/statistic conflict affecting all five Zomorrodi 2019 effects. These effects were withheld from quantitative interpretation, leaving 207 provisional study-level estimates across nine analysis clusters. Arithmetic was successfully reconstructed for 205 estimates, but this did not resolve uncertainties in the underlying extraction or working variance assumptions. No compatible outcome family contained at least three independent datasets. Consequently, no protocol-compliant pooled EEG effect, heterogeneity estimate, prediction interval, moderator result, or small-study-effect test was produced.

Available outcomes described several distinct aspects of electrophysiology, including CDA amplitude, scalp spectral power, source-network power, microstate duration, graph topology/entropy and directional PTE. Their effect scales, anatomical definitions, recording states and assessment times differed. These results do not support a single numerical summary of an overall EEG response, and increases in a given EEG metric should not be equated with cognitive or clinical improvement.

The Chaudhari sample-size sensitivity was completed for all 120 cells. Changing the working allocation from 8/8 to 7/9 changed g by a median absolute {statistics.median(changes):.4f} and a maximum absolute {max(changes):.4f}. This sensitivity tests the allocation assumption while retaining the digitized mean/SEM values; it does not resolve the matched longitudinal sample size. No pooled inference was made under either allocation.

One within-paper EEG–cognition association record was available, from Zhao's CDA and working-memory changes. Its recorded Fisher z back-transformed to r={r:.3f} (approximate 95% interval {lo:.3f} to {hi:.3f}). This record was retained for discussion only and did not constitute an independent-study association meta-analysis or evidence of mediation.

## Study-level inventory

{table}

This table describes the numeric input only. Ten additional nonnumeric rows, including overlapping companion publications, are listed with their source reasons in Outputs/EEG_source_rows_without_effect.csv. They must not be counted as ten additional independent eligible datasets.

## Descriptive estimates

{small}

All intervals above are unadjusted approximations from the recorded variances. Zhao and Mehdizadeh remain source-summary estimates without independent reconstruction here. Ghaderi's conversion is conditional on the statistic definition; He and Bastola rely on transcribed author information. The selected Bastola pathways do not represent an unbiased inventory of all tested pathways. These qualifications apply to any manuscript reuse.

The full 186 Chaudhari/Wang 2022 network rows appear in Outputs/EEG_study_level_estimates.csv and separate figure panels. Their g ranges ({'; '.join(ranges)}) describe heterogeneous dependent cells, not pooled treatment magnitudes. No sign-count or significance-count analysis was used.

## Reporting limits

This is a complete computational report of analyses currently supported by the frozen inputs and protocol gates, not a completed pooled EEG meta-analysis. Physiological narrative interpretation still requires study-specific context and final risk-of-bias/certainty adjudication. The Zomorrodi conflict needs valid source clarification or recoverable participant-level/paired summary data before conversion. Additional compatible independent data would be needed for pooling; running the same data in smaller batches would not address this limitation.
''')
planned=[
('Snapshot and overlap audit','COMPLETE','223 records; cohort links retained'),
('Source-effect reconstruction','COMPLETE WITH LIMITS','205 arithmetic checks pass; 2 unreconstructed; 5 quarantined'),
('Study-level intervals and figures','COMPLETE','207 provisional estimates, no pooled diamonds'),
('Chaudhari 8/8 versus 7/9 sensitivity','COMPLETE','120 effects; 480 independent R comparisons'),
('Family/band/state/timing/anatomy pooling','NOT ELIGIBLE','No compatible family reaches 3 independent datasets'),
('Multilevel or robust-variance synthesis','NOT ELIGIBLE','Dependent rows are not independent studies; incompatible constructs remain separate'),
('Fixed versus random effects; heterogeneity','NOT RUN','No eligible pooled model'),
('Prediction intervals','NOT RUN','No eligible pool; protocol additionally requires at least 5 datasets'),
('Moderator/subgroup analyses','NOT RUN','Insufficient compatible independent datasets'),
('Leave-one-out and influence diagnostics','NOT RUN','No pooled model to diagnose'),
('Exclusion sensitivities','INVENTORY COMPLETE; MODELS NOT RUN','Restrictions cannot create an eligible pool'),
('Assumed paired r=.2/.5/.8','NOT ESTIMABLE WHERE MISSING','Observed paired statistics retained; missing marginal SD/estimand information not invented'),
('Funnel/asymmetry analyses','NOT RUN','No homogeneous pool; protocol requires at least 10 independent studies'),
('EEG–cognition association synthesis','DISCUSSION ONLY','One within-paper record; no independent-study meta-analysis'),
('Risk of bias and certainty','REVIEWER ADJUDICATION REMAINS','No automated final GRADE/JBI judgement'),
('Zomorrodi source repair','UNRESOLVED','No author clarification available; preserve and quarantine 5 rows'),
('Original He/Bastola correspondence','PROVENANCE LIMIT','Transcribed extraction/master values used; original replies not retrieved')]
with (O/'EEG_planned_analysis_status.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['planned_analysis','status','reason']);w.writerows(planned)
status='\n'.join(f'| {x} | {y} | {z} |' for x,y,z in planned)
save('Analysis_Status_EEG_2026-09-16.md',f'''# EEG analysis status — 16 September 2026

The supported EEG audit, study-level calculations, sample-size sensitivity, figures and drafts are complete. **No pooled EEG meta-analysis is currently eligible under the approved protocol.** This is a scientific/data limitation, not a need to run computations piecemeal.

| Planned component | Status | Reason |
|---|---|---|
{status}

Read Results_Draft_EEG_2026-09-16.md and Methods_Update_EEG_2026-09-16.md together. Figure panels are descriptive, and the five Zomorrodi values are excluded from them. Source files remain untouched. Run logs and source/output hashes are in Reproducibility/Runs.

Before final manuscript submission: resolve or explicitly retain the source limitations; adjudicate risk of bias/certainty; finalize study-specific narrative interpretation; verify the complete review-wide study flow against the broader inclusion map. The 223 EEG input records are not a PRISMA study count. No newly requested scientific pooling amendment has been assumed.
''')
save('README.md','''# Reproducible EEG analysis package

Start with Analysis_Status_EEG_2026-09-16.md, then the Methods and Results drafts. All paths used by the scripts are relative to this folder; moving the whole EEG folder is supported.

Requirements: Python 3.10+ (standard library only), R 4.x (base R only). No Python/R add-on package or network access is required. Tested runtime versions are recorded in Outputs and run logs.

Run from any directory:

```text
python path/to/EEG/Scripts/run_eeg.py --rscript path/to/Rscript
```

If Rscript is on PATH, omit --rscript. The runner freezes source hashes, archives previous outputs, runs preparation, independent R verification/plots, and report generation, and writes PASS.txt only after all steps succeed and source hashes match. A successful run means the stated audit passed; it does not validate unresolved scientific assumptions.

- Reproducibility/Source_snapshots: frozen source records, never edited by the pipeline.
- Inputs: machine-readable original and audited effect tables.
- Outputs: study-level tables, compatibility gates, checks, sensitivity, figure panels and session information.
- Scripts: the complete workflow; both R and Python are intentional and reproducible together.
- Reproducibility/Runs: timestamped logs, prior-output archives and checksums.

No pooled model is fitted because no compatible family meets the protocol threshold. The numeric field eligible_for_new_pool is only a nonquarantine flag; always apply EEG_compatibility_gates.csv as well.

For a public GitHub repository, upload the scripts, README, environment/session record and suitable derived tables/figures. Review source snapshots for redistribution rights and private correspondence before publication; do not upload copyrighted full-text PDFs or private email records by default. If any input cannot be shared, provide a documented access/reconstruction route and clearly state that a public code-only repository cannot reproduce results without those inputs. Choose a license for your own code and cite the original studies/data separately. No GitHub upload has been performed.
''')
(O/'Python_environment.json').write_text(json.dumps({'python':sys.version,'platform':platform.platform(),'dependencies':'standard library only'},indent=2))
print('PASS: Methods, Results, status, planned-analysis matrix and reproducibility README generated from current outputs.')
