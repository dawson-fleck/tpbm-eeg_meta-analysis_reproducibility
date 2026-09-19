from pathlib import Path
import csv,math,json,hashlib,collections,re,sys
A=Path(__file__).resolve().parent;B=A.parent;W=A/'Working_corrected';sys.stdout.reconfigure(encoding='utf-8')
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def write(name,rows):
 if not rows:return
 with (A/'Outputs'/name).open('w',newline='',encoding='utf-8-sig') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def md(rows,keys=None):
 keys=keys or list(rows[0]);return '| '+' | '.join(keys)+' |\n| '+' | '.join('---' for _ in keys)+' |\n'+'\n'.join('| '+' | '.join(str(x.get(k,'')).replace('|','/').replace('\n',' ') for k in keys)+' |' for x in rows)
def f(x):return f'{float(x):.3f}'
def pformat(x):return '<0.001' if float(x)<.001 else f(x)
def ci(x):return f'{f(x["g"])} [{f(x["lo"])}, {f(x["hi"])}]'
core=read(A/'Outputs/harmonization_r0.5.csv');corrected=read(W/'Outputs/harmonization_r0.5.csv');spec=read(A/'Inputs/harmonization_specification_v2.csv');lock={x['cohort_id']:x for x in read(A/'Inputs/locked.csv')}
mods={x['model']:x for x in read(A/'Outputs/model_results.csv')};newmods={x['model']:x for x in read(W/'Outputs/model_results.csv')}
source={
'TANG-2023':('Sources/Tang_fulltext_live.txt, Table 3','Seven n=8 arms, post means/SDs checked directly; all six active aggregation independently recomputed.','No main-effect error; historical pulse sensitivity is wrong.'),
'HWANG-2016':('Sources/Hwang_paper.txt, Participants, Tables 1-3 and sham protocol','Post means/SDs agree; n=15 not20 per arm. All three included Hwang outcomes corrected.','Confirmed source-input and zero-output comparator errors.'),
'CHAN-2019-OLDER':('Sources/Prior_source_records/Chan2019_PDF.txt; AQ4 Recovery Source_snapshots/Chan19_embedded_0.jpg','n15/15; one-SE caption; visually checked bars/direction and paired t2.14/.79. Pixel coordinate arithmetic retained.','Digitization and rounded-t uncertainty; no pixel-independent duplicate digitization.'),
'DOUGAL-2021':('Sources/Prior_source_records/Dougal_PDF.txt, Tables 3-4 and disclosures','n14/13; baseline SE .22/.26; change SE .11/.15 converted using sqrt(n); means match.','Industry flag corrected. SD-from-SE not covered by original reconstruction flag.'),
'CHAN-2021-DIFFICULT':('Sources/Chan_difficult_paper.txt, Results and Participants','n18/15 and independent post t(31)=-.279 confirmed.','Industry flag corrected; reconstruction remains flagged.'),
'YANG-2024-LANGUAGE':('Sources/Yang2024_paper.txt, Results and Methods','Analyzed n56; active2343.36 SD674.59 vs sham2556.09 SD733.21; RT sign reversed.','Pooled language groups; paired correlation imputed; period/carryover not modeled.'),
'CHAN-2021-MCI':('Sources/Prior_source_records/ChanMCI_PDF.txt; AQ4 Recovery Source_snapshots/Chan2021_Figure3.png','n9/9, stated means and one-SE bars visually checked; t2.3/.3 reconstruct change SD.','Digitization and coarse t rounding; publisher disclosure page unavailable.'),
'HASSAN-2026-STROKE':('Sources/Hassan_paper.txt, Table 2 and Methods','n20/20, endpoint24.6 SD3.8 vs25.1 SD4.2; null endpoint retained.','First post-course assessment one week later; do not describe as literally immediate.'),
'PENA-2026':('Sources/Pena2026_paper.txt, Methods and Table 2','Means and baseline/post SDs verified; Methods n28/28 retained.','Table1 demographics/df imply a different denominator; n and exact ANCOVA estimand require author reconciliation. Change SD depends on imputed r.'),
'CHUN-2025-PILOT':('Sources/Chun_pilot_paper.txt, Table 3','n13/13; week13 MoCA25.92 SD2.84 vs20.92 SD5.12; industry sponsorship confirmed.','Extraction form contains unrelated older 904nm study text: use paper, not merged form, for parameters.'),
'LEE-2025-TBI':('Sources/Lee_TBI.pdf and Lee_TBI.txt, Table 2','n17 completers; real span5.71 SD1.21 vs sham5.65 SD1.27 confirmed in institutional author manuscript.','23 randomized, six dropouts; imputed paired correlation; additional usable endpoints omitted from all-outcomes set.'),
'DEOLIVEIRA-2024':('Sources/Oliveira_paper.txt, Methods, Table2, Fig4 and disclosures','Baseline19.3 SD3.3 vs18.5 SD3.8; n40/36 and change means checked against text.','Figure-derived change SD1.26756/1.50571 retained; not freshly re-digitized. CONSORT denominator discrepancy remains. Industry flag corrected.'),
'BERMAN-2017-DEMENTIA':('Sources/Berman_paper.txt; Source_text/DataExtraction_Berman_2017_completed.docx.txt','n6/3 completers; supplied individual pre/post pairs reproduce baseline and change summaries.','Figure3 pairs not independently re-digitized in this audit; n3 control and incomplete reporting make variance especially approximate.'),
'YANG-2025-OLDER-WM':('Sources/Yang2025_paper.txt; Source_text/DataExtraction_Yang_et_al_2025_completed.txt','n55 crossover design confirmed; .63 SD.17 vs.56 SD.18 matches archived supplement transcription.','Original Supplementary Table A1 not independently retrieved; active/sham r imputed; possible SILCODE overlap unresolved.'),
'SABOURI-MOGHADAM-2017':('Correct paper DOI10.5812/ircmj.44513; Sources/Prior_source_records/Sabouri_source_verified.txt','n17/17; Table2 baseline SD5/5; abstract changes4.6 SD3 vs.8 SD3 verified against correct full text.','Rounded endpoint means differ from reported changes; use reported changes. Sabouri_PDF.txt is an unrelated paper; do not use it.'),
'SALEHPOUR-2026-STAGE1-ADHD':('Sources/Prior_source_records/Salehpour_PDF.txt, Stage1/Figure4','Selected Stage1 ADHD cells n15/12 and reported d=.93 retained; exact gamma J25 applied.','d not identical to rounded F6.71 reconstruction; post-only subgroup and self-reported ADHD; Stage2 is separate recruitment and not co-counted.'),
'ZHAO-X-2022-SCD':('Sources/ZhaoX_paper.txt; Source_text/DataExtraction_Zhao_et_al_2022_SCD_completed.txt','n32/26 completers versus34/34 randomized; archived supplement RT/paired-t inputs reproduce change SD117.21298/142.72933.','Original supplement not independently retrieved; main-paper trial-count pseudoreplication/RT inconsistencies remain major-risk concerns.')}
roster=[]
for x,y in zip(core,corrected):
 s,verified,limits=source[x['cohort_id'][4:]];l=lock[x['cohort_id']]
 roster.append(dict(cohort_id=x['cohort_id'],study=x['study'],outcome=x['outcome_id'],domain=x['domain'],time=x['timing'],n1=y['n1'],n0=y['n0'],unique_n=y['n1'] if y['route']=='SMCRPH' else float(y['n1'])+float(y['n0']),route=x['route'],direction=x['sign'],original_g=x['hedges_g'],original_v=x['sampling_variance'],audited_g=y['hedges_g'],audited_v=y['sampling_variance'],df=y['audit_df'],J=y['audit_J'],standardizer=y['audit_standardizer'],source=s,source_verified=verified,limits=limits,locked_rob=l['risk_of_bias_flag'],major_flag=x['major_rob'],overlap=l['independence_overlap_audit'],industry_original=x['industry_status'],industry_corrected=y['industry_status']))
write('cohort_effect_provenance.csv',roster)
write('23_to_17_reconciliation.csv',[dict(cohort_id=x['cohort_id'],outcome=x['outcome_id'],historical_included=1,current_included=x['include'],route=x['route'],reason=x['reason']) for x in spec])
write('current_RoB_provenance.csv',[dict(cohort_id=x['cohort_id'],domain=x['domain'],historical_major_flag=x['major_flag'],locked_judgment=x['locked_rob'],final_item_level_verified=False,reason='Live master gives totals/overall labels; final checklist items and adjudication record not supplied',absence_of_major_flag_means='No explicit historical major flag; not low risk') for x in roster])
discrep=[]
for key,v in mods.items():
 if key in newmods:
  z=newmods[key];discrep.append(dict(model=key,original_k=v['k'],corrected_k=z['k'],original_g=v['g'],corrected_g=z['g'],delta_g=float(z['g'])-float(v['g']),original_CI=ci(v),corrected_CI=ci(z),original_p=v['p'],corrected_p=z['p']))
write('model_discrepancies.csv',discrep)
members=read(W/'Outputs/sensitivity_membership.csv');skips=read(W/'Outputs/models_not_run.csv');matrix=[]
for key in dict.fromkeys(x['model'] for x in members):
 rr=[x for x in members if x['model']==key];v=newmods.get(key)
 matrix.append(dict(model=key,k=v['k'] if v else sum(x['included']=='TRUE' for x in rr),estimate_CI=ci(v) if v else 'Not fitted: k<3',p=v['p'] if v else '',retained=';'.join(x['cohort_id'] for x in rr if x['included']=='TRUE'),excluded=';'.join(x['cohort_id'] for x in rr if x['included']!='TRUE'),status='Fitted' if v else 'Omitted with explicit small-k reason'))
write('corrected_sensitivity_matrix.csv',matrix)
feas=[
('Mean age','Omitted; source metadata incomplete for this estimand','Several means available, but enrolled vs analyzed/ADHD subgroup means differ; Oliveira reports median; no invented midpoints.','Complete cohort-specific mean-age ledger, then inspect confounding with population/schedule.'),
('Wavelength','Omitted; cannot assign one numeric wavelength to all effects','Tang660+850, Chan2019 633+870, Oliveira660+850; Berman1060–1080 band. Scalar slope would mix devices and mechanisms.','Use source-specific categories or a restricted continuous analysis only under a documented new coding rule.'),
('Pulse structure','Completed as post-results exploratory audit','11 CW,3 PW,1 mixed,2 unclear. Tang excluded from binary mode model; Dougal and Sabouri remain unclear. F(1,12)=1.460,p=.250.','PW occurs only in global cognition and convergent thinking; no causal pulse inference. Tang direct contrast separately verified.'),
('Device / light source','Completed for laser vs LED only','6 laser,11 LED; F(1,15)=.734,p=.405. Individual device models mostly singleton.','No model-brand meta-regression or optimal device inference.'),
('Target distribution','Omitted; no frozen defensible grouping','17 source descriptions recorded; focal left/right, bilateral frontal, frontal+posterior and whole-head are not interchangeable.','A transparent anatomical taxonomy is needed; likely sparse and confounded with clinical indication.'),
('Session number','Omitted exact-dose regression; binary schedule completed','16 point session counts, Dougal at least56; crossover active sessions distinguished from sham visits. Strong range/schedule/population dependence.','Do not replace lower bound with exact count or choose a transformation after inspecting p-values.'),
('Sham dose','Completed corrected exclusion and exploratory omnibus','Hwang reclassified as1/12 energy. 4 low/nonzero and13 zero/control; F(1,15)=.614,p=.446.','No inferential claim from separate subgroup p-values.'),
('Industry association','Completed corrected exclusion and exploratory omnibus','5 documented vs12 without documented association; F(1,15)=.038,p=.849. ChanMCI disclosure page unavailable.','Absence of documented link is not proof of independence; association definition is broader than trial sponsorship.'),
('Fluence/irradiance/duty cycle','Omitted with justified comparability limits','Peak vs average irradiance, device aperture vs cortical exposure, wavelength and schedule jointly vary.','No multivariable optimization at k17.'),
('Follow-up durability','Missing finalized compatible input; not fitted','First end-of-course assessment must not be confused with later follow-up; no locked compatible follow-up family k>=3.','Retain missing-analysis status rather than treating treatment duration as durability.'),
('Final domain certainty / JBI figure','Unresolved reviewer evidence','Declared final human review is not substantiated by item-level files in the package.','Supply final items, tool edition, evidence, agreement denominator and adjudication. No automated GRADE grade assigned.')]
write('planned_analysis_feasibility.csv',[dict(analysis=a,status=b,evidence=c,next_requirement=d) for a,b,c,d in feas])
main=[]
for dom in ['Memory','Global cognition','Executive / sustained attention','Overall cognition']:
 v=mods['primary__'+dom];z=newmods['primary__'+dom];main.append(dict(Analysis=dom,k=z['k'],Reproduced=ci(v),Corrected=ci(z),p=pformat(z['p']),I2=f'{float(z["I2"]):.1f}%',PI=(f(z['pi_lo'])+' to '+f(z['pi_hi'])) if z['pi_lo'] else 'Not reported; k<5'))
no_rob=[dict(Analysis=x['model'].split('__')[0],k=x['k'],Estimate=ci(x),p=pformat(x['p'])) for x in newmods.values() if x['model'].endswith('__no_major_rob')]
ml=next(x for x in read(W/'Outputs/multilevel.csv') if x['variant']=='components' and x['paired_r']=='0.5' and x['rho']=='0.5')
rob_old=mods['Overall cognition__no_major_rob'];old=mods['historical__Overall cognition'];ret=mods['historical_retained__Overall cognition']
h0=next(x for x in core if 'HWANG' in x['cohort_id']);h1=next(x for x in corrected if 'HWANG' in x['cohort_id'])
report=f'''# Scientific integrity audit — 17 September 2026

**Verdict: the current model implementation reproduces, but the current inputs and manuscript are not fully correct or submission-ready.** A source-confirmed Hwang sample-size error changes the cognition estimates. Incorrect sham and industry coding change sensitivity membership. The favorable executive/attention result is sensitive to the small-k HK convention. The available records do not certify final item-level JBI appraisal, complete outcome ascertainment, or every digitized/supplemental input.

This audit preserves the historical lock, both AQ4 versions, publication package and EEG originals. Corrections are in `Working_corrected/`; nothing was written to the live Google documents. This is a post-results audit, not a retrospective claim of prespecification.

## A. Verified correct, conditional on source limitations

- The 17-cohort v2 analysis and the three primary moderator tests reproduce. A separately written Python implementation agrees with R for all four principal REML/HK fits, including t inference, Q, tau², I² and prediction intervals (maximum original difference <0.000001; corrected <0.000002).
- All 47 included specification rows (17 representative,24 candidate all-outcome including the redundant composite,6 external) reproduce at central r. The actual component model drops the Dougal composite, giving23 effects. Across three paired-r values,102 original/corrected representative effect checks also agree with metafor's design-specific formulas within1e-10.
- The current all-six-active Tang effect is correct. The faulty all-PW row is not an input to the current main model.
- The EEG no-pooling conclusion is supported. An independent coarser construct/band count still reaches at most two independent datasets, before additional state/timing/anatomical restrictions.

## B. Wrong or outdated

1. **Hwang2016 uses n20/20 in every current outcome, but the paper explicitly says n15/15** (Participants and Tables1–2). Table3 means/SDs were correct. Its selected effect changes from g={float(h0['hedges_g']):.6f},v={float(h0['sampling_variance']):.6f} to g={float(h1['hedges_g']):.6f},v={float(h1['sampling_variance']):.6f}. The old variance overstated precision. Correction applies to all three Hwang outcomes and every dependent model.
2. Hwang's sham delivers5seconds of light each minute,1/12 active energy. It is not zero-output. Corrected zero-output overall k=13, not14.
3. **Industry flags miss Dougal2021, Chan2021 difficult-task, and deOliveira2024.** Dougal discloses Maculume funding and majority shareholding; Chan difficult-task discloses Hamblin's commercial advisory/consulting roles; deOliveira discloses Cassano's PBM company funding, consulting, shareholding and patents. The corrected broad documented-industry exclusion removes these plus Chun pilot and Berman. Global cognition then has only Hassan left (k1), so that restricted domain cannot be pooled. No documented association is not a verified absence of one.
4. The live master still labels Tang's selected three favorable PW arms as all four: n24,mean.463333,g≈.645. The missing850nm/PW100 arm has mean.34,SD.04. Correct all-PW n32 vs8 gives g=.374269,v=.158001; CW g=.047990,v=.187548; direct PW–CW g=.345622,v=.094994,normal CI≈[-.2585,.9497]. Tiny differences from the supplied historical normal limits reflect1.96 versus the exact normal quantile. Higher PW peak irradiance confounds a pulse-timing interpretation; this is exploratory, not superiority evidence.
5. Both previously identified prose errors remain live: Discussion says all domain and overall CIs cross zero; EEG Methods says increased EEG features are associated with improved cognition. Neither statement is justified as written. The Discussion also contains an unfinished parameter sentence.
6. The live SAP/master remain historical23-cohort records. Historical Cognition reports, publication snapshots and the current manuscript's old numerical results must not be relabeled as source-corrected results. A dated amendment and explicit version pointers are required.

## C. Results and unresolved validity issues

### Primary domains and secondary overall

{md(main)}

The primary method remains REML with **unmodified HK**, t(k−1). Executive/attention HK scale=.654205. Modified-HK caps that scale at1, giving g=.617,95%CI[-.075,1.310],p=.0617; the stated primary result remains p=.0417. No PI is reported for k3. Default metafor HK PI uses t(k−1)×sqrt(tau²+SE_HK²), not Riley's t(k−2), and does not integrate tau² uncertainty. I² uses metafor's tau²/typical-sampling-variance convention; it need not equal max(0,(Q−df)/Q).

The corrected overall Q(16)={float(newmods['primary__Overall cognition']['Q']):.3f},tau²={float(newmods['primary__Overall cognition']['tau2']):.3f}. Memory remains inconclusive; global cognition remains borderline and inconclusive; the secondary overall CI remains positive while its PI includes zero. Retain domain models as primary and the cross-domain model as secondary. Do not equate a positive cross-domain mean with demonstrated benefit in every domain.

### Version and cohort reconciliation

Historical core23: {ci(old)}. The original values restricted to the17 retained cohorts give {ci(ret)}. Harmonization then gives.390[.205,.575]; this audit's source correction gives.380[.200,.561]. Thus the large historical-to-current change is not just an exclusion count or exact-J rounding issue.

The17 current cohorts are Tang2023; Hwang2016; Chan2019 older; Dougal2021; Chan2021 difficult-task; Yang2024 language; Chan2021 MCI; Hassan2026 stroke; Peña2026; Chun2025 pilot; Lee2025 TBI; deOliveira2024; Berman2017; Yang2025 older-WM; Sabouri Moghadam2017; Salehpour2026 Stage1 ADHD; Zhao-X2022 SCD. Full IDs, effects, Ns, timepoints, formulas and source limits are in `Outputs/cohort_effect_provenance.csv`.

Six historical representatives remain outside the harmonized pool: Zhao-C2022 aggregate, Barrett2013, Papi2022, Kheradmand2022 dementia, Han2025 and Chun2026 confirmatory. Their denominator/sample-mapping problems are itemized in `23_to_17_reconciliation.csv`; no paper is deleted from the review. AQ4 v1 had15 before two Chan recoveries. The23-effect all-outcomes model has17 clusters; the23-cohort external expansion is17+6 external cohorts; the historical all-explicit-RoB-concern exclusion happened to have17 but has a different roster and estimand. Matching k never establishes equivalence.

The external expansion adds Blanco2017,Holmes2019,Chen2023,Joshi2024,Nizamutdinov2021,Paolillo2023. It gives {ci(newmods['external_expansion'])}; it mixes eligibility boundaries and must remain secondary. Separate raw MMSE k3 reproduces1.045[-2.428,4.519] but includes Kheradmand outside the harmonized SMD core; it is not simply a subset of the17 and combines stroke/dementia and endpoint/change contrasts.

### Effect conventions and source confidence

Independent endpoints use pooled endpoint SD,exact gamma J(n1+n0−2),and LS variance1/n1+1/n0+g²/[2(n1+n0)]. Controlled changes subtract separately baseline-SD-standardized arm changes,using J(n_arm−1) and SMCRH LS2 arm variances; these are summed because randomized arms are independent. This is an arm-standardized change contrast, not necessarily the same quantity as difference-in-change divided by a common pooled baseline SD. Crossover effects use sqrt((SD_active²+SD_sham²)/2),SMCRPH's correlation-dependent correction df and LS2 variance. The marginal scale is not paired-difference SD(dz). All signs were checked against lower/higher-is-better coding. Exact-J differences alone are tiny; Hwang's N error is substantive.

Paper/transcription checks are explicitly separated from arithmetic in the roster. Tang,Dougal,Hwang,Chan difficult-task,Chun pilot,Hassan,Yang2024 and Lee TBI have direct source-text checks. The two Chan figures were visually checked,including SE captions and directions; their retained pixel coordinates were not freshly independently digitized. Berman pairs and deOliveira change SDs remain conditional on prior figure digitization. Yang2025 Supplementary TableA1 and Zhao-X Supplementary Tables1–2 were not independently retrieved; their transcribed values reproduce, but that is not source authentication. Peña Methods says28/arm while demographic denominators/df are inconsistent; retain this limitation rather than silently choosing29. Salehpour uses reported d=.93,not a forced conversion from rounded F.

Shared controls: Tang active arms are pooled with within-plus-between-arm sums of squares and one sham. Hwang's EX arms are not added to the selected PBM-only contrast. Multiple outcomes enter the covariance model,not separate independent k. Lee and Yang crossover n is counted once,not twice. Core unique-participant sum from analyzed Ns after Hwang correction is{sum(float(x['unique_n']) for x in roster):.0f}; it remains conditional on no unreported overlap and Peña's N uncertainty, and is not the review-wide participant count.

Companions: keep Chun pilot/confirmatory/mechanistic report identities distinct; confirmatory is outside this core. Salehpour Stage2 recruitment is separate,so its omission is an outcome/study-selection rule,not proof of participant overlap. Yang2025/Qu2022/Hu2023 share a program; only Yang contributes to the core. Zhao-X may overlap with the broader SILCODE program, but reuse is not demonstrated; both one-at-a-time exclusions were run. EEG Wang2021/Shahdadian2022/Wang2022/Truong2023 share the UTA cohort; Bastola/Pruitt share UTSW. A complete participant-level cross-report linkage cannot be certified from author names alone.

### Risk of bias and sensitivity membership

Original current17 excluding Berman and Zhao-X reproduces k15,{ci(rob_old)}. The corrected results are:

{md(no_rob)}

Memory excludes Zhao-X; global cognition excludes Berman; executive/attention excludes nobody. Every retained/excluded ID appears in `corrected_sensitivity_matrix.csv`,including unfitted k<3 restrictions. These are **historical-major-flag exclusions**,not a newly verified low-risk subset. The flag is derived from locked narrative text beginning “major”,not a documented item-to-major-risk algorithm. Live JBI records give summary totals and overall categories. Their older agreement entries include Dougal70%or lower and Spera80%,while the manuscript reports a finalized≥90%acceptance check. This does not prove the author's later finalization did not occur; it means the final items,denominator,dates and reconciliation are needed to verify that assertion. A stricter no-explicit-concern audit leaves12 overall,not the historical17; its membership and estimates are separately saved. No risk label was inferred from an absent flag.

Design,zero-output,digitization,reconstruction,imputed-r,industry,endpoint/change,PM,fixed-effect,Wald,modified-HK,LOO and influence models were run overall and for major domains where k≥3. Original reconstruction coding excludes selected t/change-SD derivations but not Dougal SE-to-SD or Salehpour reported-d conversion; an explicitly stricter sensitivity is provided. Variance-imputation exclusion concerns paired-r assumptions,not every approximate sampling-variance formula. LOO does not certify source accuracy. Some restricted domains become too small to pool; their absence is logged,not hidden.

### Moderators, dependence and small-study models

Corrected Holm p-values across the same three hypotheses are population.446,schedule.401,domain group.446; no missing categories. Their omnibus F tests use residual df15,15,14,respectively. The domain moderator groups executive,language and convergent thinking into “Other”; it is not an omnibus test of all five separate domains. Membership and analyzed-N counts are saved. No moderator conclusion is based on subgroup significance.

The component all-outcome model at paired r=.5 and outcome rho=.5 gives g={float(ml['g']):.3f},CI[{float(ml['lo']):.3f},{float(ml['hi']):.3f}],CR2/Satterthwaite df={float(ml['df']):.2f},23 effects/17 clusters. We ran the full3×3 paired-r/outcome-rho grid and component/composite/no-digitized-or-reconstructed variants(27 fits). Covariance blocks have vi on the diagonal and rho×sqrt(vi×vj) off diagonal; all were positive definite. Random intercepts nest effect within cohort; CR2 clusters at cohort. The cohort heterogeneity component often approaches zero; this does not mean outcomes are independent. Dougal composite is excluded when components are included.

“All-outcomes” is not exhaustive. Lee TBI Table2 contains span-specific RT,HKLLT,CFT,DST,FPT and trail measures with marginal means/SDs. Additional recoverable Chan MCI and Sabouri endpoints also require explicit inclusion/redundancy decisions. Missing paired correlations cannot by themselves explain Lee's omission when the same model imputes r for its selected span. Preserve the current model as a selected multiple-outcome robustness check; do not claim it eliminates outcome-selection bias. No favorable outcome was added after seeing results.

Corrected Egger-type p=.0668 and Begg p=.1513 do not establish absence of bias. PET intercept=.036[-.356,.428]; PEESE=.206[-.034,.447];trim-and-fill adds4 and gives.281[.107,.455] using Wald inference; the ML two-sided p=.05 step-selection model gives.205[.046,.363],also Wald. Egger and PET slope are the same precision association,not two independent signals. SMD-SE coupling,heterogeneity and k17 limit all these analyses; none is a corrected truth estimate.

### Treatment parameters

{md([dict(Analysis=a,Status=b,Evidence=c) for a,b,c,d in feas[:9]])}

The pulse,device,sham and industry regressions are newly completed post-results exploratory audits,unadjusted and separate from the three Holm hypotheses. Pulse PW cohorts are two global-cognition trials and one convergent-thinking trial; there is no PW memory or executive cohort in that binary fit. Confounding and sparse support preclude a claim that parameters explain heterogeneity. Keep Tang mixed CW/PW,not purely pulsed. The direct within-trial Tang comparison is more informative about the arm contrast than between-study categories,but still cannot separate pulse timing from peak irradiance.

### EEG findings and evidence levels

The package rerun matches212 numeric records:5Zomorrodi rows quarantined,207provisional descriptive effects from9report-clusters. Zhao-C includes two experiments within one cluster,so nine clusters should not be called nine unambiguously independent experiments. Original205arithmetic reconstructions pass. This audit additionally reconstructs Zhao-C CDA from paired t(22)=2.313 and t(17)=2.506 and Mehdizadeh Fp1 from Table2,giving207/207conditional arithmetic reconstructions. These last checks are in `EEG_additional_source_reconstruction.csv`; they do not remove design/source assumptions. Mehdizadeh's table labels adjusted means±SD,so ordinary independent SMD variance remains provisional. Bastola's d_av interpretation and He paired summaries still rely on transcribed author information; searched connected Gmail returned paper attachments,not original explanatory replies/raw arrays.

Chaudhari contributes120dependent digitized outcomes;8/8versus7/9 sensitivity and480independent R numeric comparisons reproduce. Wang2022 contributes66dependent network outcomes. Channels,bands,timepoints and companion reports cannot increase independent k. Fixed-order Spera/Wang2019 and heterogeneous normalizations cannot support a global EEG average. Zomorrodi's crossover/parallel and Wilcoxon/t conflicts justify quarantine. EEG effects retain metric-specific signs and mixed dz/marginal/independent conventions; physiological increase is not inherently beneficial.

Zhao's within-paper association reconstructs Fisher z=.547204,var=.028571 from r=.446(n23) and r=.563(n18). It is a same-session association of treatment differences,not independently validated prediction of individual benefit. No supplied study establishes an EEG-guided adaptive-treatment benefit. The evidence hierarchy must keep treatment effects,EEG–cognition association,out-of-sample prediction,and adaptive-treatment trials separate.

## D. Do conclusions materially change?

**The numerical results require correction; the broad cautious interpretation survives.** The corrected overall point estimate is slightly smaller and retains a positive CI/zero-crossing PI. Memory and global cognition remain inconclusive. Executive/attention is positive under the stated unmodified-HK primary rule but loses conventional significance under modified-HK. Claims of robust domain-wide efficacy,validated EEG prediction,pulse superiority or established closed-loop treatment are not supported. Historical23-cohort estimates cannot be substituted for these results.

## E. Is there a useful defensible contribution?

**Yes,conditionally:** a transparent domain-specific cognitive synthesis plus an EEG evidence map that shows where physiological effects have,and have not,been linked to cognitive outcomes. Its value is not an optimized treatment prescription. Keep the two evidence streams separate; retain the broad cognition mean only as secondary; simplify the reporting-bias battery into clearly labeled sensitivity results; rename the selected multiple-outcome model; keep unsupported EEG pooling and treatment optimization out. The empirical gap between a physiological response and validated individual cognitive benefit is defensible,provided it is presented as an evidence gap rather than proof of future closed-loop efficacy.

Submission blockers are documentary as well as numerical: final source-linked item-level JBI/certainty assessments,source exceptions above,complete outcome-selection and companion mapping,and final PRISMA/search/characteristics artifacts. The live manuscript says the author completed several of these tasks; this audit neither invents nor negates that work. It identifies the exact supporting artifacts absent from the accessible package.

## Reproducibility and files

- `Outputs/cohort_effect_provenance.csv`: complete17-cohort trace with source-verification limits.
- `Outputs/23_to_17_reconciliation.csv`: all historical23 decisions.
- `Outputs/model_discrepancies.csv`: original-current versus source-corrected model differences.
- `Outputs/corrected_sensitivity_matrix.csv`: explicit retained/excluded IDs for every fitted or omitted restriction.
- `Outputs/planned_analysis_feasibility.csv`, `parameter_metadata.csv`: planned/omitted/source-repair analyses.
- `MANUSCRIPT_CORRECTIONS.md`, `Working_corrected/Manuscript_audited_working.txt`: reviewable text corrections,not a live-doc rewrite or submission-ready Word file.
- `Working_corrected/Outputs/`, `Working_corrected/Figures/`: all corrected fits and principal forests.
- `Logs/input_manifest.csv`, `Logs/archive_inventory.csv`, `Logs/final_manifest.csv`, `Logs/preservation_check.csv`: source,archive and output provenance.
- `run_audit.ps1`: reruns local computations without network access; R4.6.1,metafor5.0-1,clubSandwich0.7.0. No package upgrades were used. Initial sandbox library/locale failures are documented; successful final runs are explicit in logs.

The two ZIPs were opened,all1888file entries were read and hashed, and local matches were inventoried; no archived code was executed blindly. The archive records and currently designated v2 directory were not assumed to be the same analysis. Library files are dependencies,not source validation. Publication/current and historical numerical text was scanned; the live manuscript and original Google fetch metadata are saved. Old values in archived historical reports are legitimate history,not automatically contamination.

Method references checked: [metafor effect-size documentation](https://search.r-project.org/CRAN/refmans/metafor/html/escalc.html), [prediction intervals](https://search.r-project.org/CRAN/refmans/metafor/html/predict.rma.html), and [controlled standardized changes](https://www.metafor-project.org/doku.php/analyses:morris2008). Formula compatibility does not certify the input provenance.
'''
(A/'AUDIT_REPORT.md').write_text(report,encoding='utf-8')
(A/'Outputs/principal_results.md').write_text(md(main),encoding='utf-8')
print('Wrote audit report, roster, reconciliation, discrepancy and sensitivity tables.')
