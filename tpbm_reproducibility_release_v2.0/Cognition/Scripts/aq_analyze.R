# AQ4: exact small-sample corrections, design-specific variance, REML/HK.
options(stringsAsFactors=FALSE,warn=1,scipen=999)
if(.Platform$OS.type=='windows')invisible(Sys.setlocale('LC_CTYPE','English_United States.utf8'))
arg<-commandArgs(FALSE);root<-dirname(dirname(normalizePath(sub('^--file=','',arg[grepl('^--file=',arg)][1]),winslash='/')))
if(nzchar(Sys.getenv('TPBM_R_LIBRARY'))) .libPaths(c(Sys.getenv('TPBM_R_LIBRARY'),.Library))
library(metafor);library(clubSandwich)
out<-file.path(root,'Outputs');fig<-file.path(out,'Figures');dir.create(fig,showWarnings=FALSE)
rd<-function(f)read.csv(f,check.names=FALSE,fileEncoding='UTF-8-BOM')
wr<-function(x,n)write.csv(x,file.path(out,n),row.names=FALSE,na='')
J<-function(df)exp(lgamma(df/2)-log(df/2)/2-lgamma((df-1)/2))
spec<-rd(file.path(root,'Inputs','harmonization_specification_v3.csv'))
allspec<-rd(file.path(root,'Inputs','all_outcomes_specification_v3.csv'))
convert<-function(z,r=.5) {
 z$paired_r_scenario<-r;z$hedges_g<-NA_real_;z$sampling_variance<-NA_real_;z$correction_df<-NA_character_;z$correction_J<-NA_character_;z$arm_r1<-NA_real_;z$arm_r0<-NA_real_
 for(i in which(z$include==1)) {
  x<-z[i,];df<-x$n1+x$n0-2;corr<-J(df)
  if(x$route=='SMD')e<-escalc(measure='SMD',m1i=x$m1,m2i=x$m0,sd1i=x$sd1,sd2i=x$sd0,n1i=x$n1,n2i=x$n0,vtype='LS')
  if(x$route=='SMD_t')e<-escalc(measure='SMD',ti=x$t,n1i=x$n1,n2i=x$n0,vtype='LS')
  if(x$route=='SMD_d')e<-escalc(measure='SMD',di=x$reported_d,n1i=x$n1,n2i=x$n0,vtype='LS')
  if(x$route=='SMCRPH') {
   e<-escalc(measure='SMCRPH',m1i=x$m1,m2i=x$m0,sd1i=x$sd1,sd2i=x$sd0,ni=x$n1,ri=r,vtype='LS2')
   df<-2*(x$n1-1)/(1+r^2);corr<-J(df);z$arm_r1[i]<-r
  }
  if(x$route=='SMCRPH_obs') {
   robs<-x$observed_r
   e<-escalc(measure='SMCRPH',m1i=x$m1,m2i=x$m0,sd1i=x$sd1,sd2i=x$sd0,ni=x$n1,ri=robs,vtype='LS2')
   df<-2*(x$n1-1)/(1+robs^2);corr<-J(df);z$arm_r1[i]<-robs
  }
  if(x$route=='controlled_SMCRH') {
   s1<-x$changeSD1;s0<-x$changeSD0
   if(x$imputed_r==1) {s1<-sqrt(x$preSD1^2+x$sd1^2-2*r*x$preSD1*x$sd1);s0<-sqrt(x$preSD0^2+x$sd0^2-2*r*x$preSD0*x$sd0);z$arm_r1[i]<-r;z$arm_r0[i]<-r}
   if(x$imputed_r==0 && all(is.finite(c(x$sd1,x$sd0)))) {z$arm_r1[i]<-(x$preSD1^2+x$sd1^2-s1^2)/(2*x$preSD1*x$sd1);z$arm_r0[i]<-(x$preSD0^2+x$sd0^2-s0^2)/(2*x$preSD0*x$sd0)}
   ga<-J(x$n1-1)*x$change1/x$preSD1;gc<-J(x$n0-1)*x$change0/x$preSD0
   va<-s1^2/(x$n1*x$preSD1^2)+ga^2/(2*x$n1);vc<-s0^2/(x$n0*x$preSD0^2)+gc^2/(2*x$n0)
   # SMCRH LS2 depends on observed SDdifference and baseline SD. Synthetic
   # covariance inputs below only verify that algebra in the installed package;
   # they are NOT imputed study correlations and are never written as such.
   checkarm<-function(delta,preSD,sdchange,n)escalc(measure='SMCRH',m1i=delta,m2i=0,sd1i=preSD,sd2i=sqrt(preSD^2+sdchange^2),ri=preSD/sqrt(preSD^2+sdchange^2),ni=n,vtype='LS2')
   ca<-checkarm(x$change1,x$preSD1,s1,x$n1);cc<-checkarm(x$change0,x$preSD0,s0,x$n0)
   stopifnot(abs(ca$yi-ga)<1e-10,abs(cc$yi-gc)<1e-10,abs(ca$vi-va)<1e-10,abs(cc$vi-vc)<1e-10)
   e<-data.frame(yi=ga-gc,vi=va+vc);df<-paste(x$n1-1,x$n0-1,sep=';');corr<-paste(J(x$n1-1),J(x$n0-1),sep=';')
  }
  z$hedges_g[i]<-as.numeric(e$yi)*x$sign;z$sampling_variance[i]<-as.numeric(e$vi);z$correction_df[i]<-as.character(df);z$correction_J[i]<-as.character(corr)
 }
 z
}
d<-convert(spec);wr(d,'study_level_harmonization_audit.csv')
for(r in c(.2,.5,.8)) {dd<-convert(spec,r);write.csv(dd[dd$include==1,],file.path(root,'Inputs',paste0('harmonized_cognition_v3_r',r,'.csv')),row.names=FALSE,na='')}
d<-d[d$include==1,];stopifnot(!anyDuplicated(d$cohort_id),all(is.finite(d$hedges_g)),all(d$sampling_variance>0))
old<-rd(file.path(root,'Original_snapshot','Approved_plan_outputs','analysis_coding.csv'))
results<-list();skips<-list();fits<-list();members<-list()
fit<-function(x,id,domain,scenario='harmonized',method='REML',test='knha') {
 if(nrow(x)<3) {skips[[length(skips)+1]]<<-data.frame(id=id,domain=domain,k=nrow(x),reason='Fewer than 3 independent cohort estimates');return(NULL)}
 f<-rma(x$hedges_g,x$sampling_variance,method=method,test=test,slab=x$study,control=list(threshold=1e-10,maxiter=1000));pr<-predict(f)
 results[[length(results)+1]]<<-data.frame(id=id,domain=domain,scenario=scenario,k=f$k,g=as.numeric(f$b),se=f$se,ci_low=f$ci.lb,ci_high=f$ci.ub,p=f$pval,I2=f$I2,tau2=f$tau2,Q=f$QE,Qp=f$QEp,pi_low=if(f$k>=5&&method!='FE')pr$pi.lb else NA,pi_high=if(f$k>=5&&method!='FE')pr$pi.ub else NA,method=method,test=test)
 fits[[id]]<<-f;members[[length(members)+1]]<<-data.frame(id=id,cohort_id=x$cohort_id,yi=x$hedges_g,vi=x$sampling_variance)
 f
}
domains<-c('Overall cognition','Memory','Global cognition','Executive / sustained attention','Language','Convergent thinking')
pick<-function(x,dom)if(dom=='Overall cognition')x else x[x$domain==dom,]
for(dom in domains) {
 x<-pick(d,dom);oo<-pick(old,dom)
 fit(oo,paste('old',dom,sep='__'),dom,'Original reproduced')
 fit(oo[oo$cohort_id %in% d$cohort_id,],paste('old_retained',dom,sep='__'),dom,'Original values; retained cohorts only')
 f<-fit(x,paste('new',dom,sep='__'),dom)
 if(is.null(f))next
 key<-gsub('[^A-Za-z0-9]+','_',dom)
 loo<-leave1out(f);wr(data.frame(omitted=x$cohort_id,as.data.frame(loo)),paste0('leave_one_out_',key,'.csv'))
 inf<-influence(f);wr(data.frame(cohort_id=x$cohort_id,as.data.frame(inf$inf)),paste0('influence_',key,'.csv'))
 restrictions<-list(no_major_rob=x[x$major_rob==0,],parallel_only=x[x$design_group=='Parallel-group',],no_digitization=x[x$digitized==0,],no_F_t_reconstruction=x[x$reconstructed==0,],no_imputed_r=x[x$imputed_r==0,],zero_output_control=x[x$comparator_intensity=='No therapeutic light/control',],no_industry=x[x$industry_status=='No documented industry association',],post_endpoint_only=x[x$route %in% c('SMD','SMD_t','SMD_d','SMCRPH'),],controlled_change_only=x[x$route=='controlled_SMCRH',],exclude_SILCODE_Yang=x[x$cohort_id!='COG-YANG-2025-OLDER-WM',],exclude_SILCODE_Zhao=x[x$cohort_id!='COG-ZHAO-X-2022-SCD',])
 for(sc in names(restrictions))fit(restrictions[[sc]],paste(dom,sc,sep='__'),dom,sc)
 for(r in c(.2,.8)){q<-convert(spec,r);q<-q[q$include==1,];fit(pick(q,dom),paste(dom,'r',r,sep='__'),dom,paste('paired correlation',r))}
 fit(x,paste(dom,'FE',sep='__'),dom,'Fixed effect','FE','z');fit(x,paste(dom,'PM',sep='__'),dom,'Paule-Mandel','PM');fit(x,paste(dom,'Wald',sep='__'),dom,'Wald sensitivity','REML','z')
}
ext<-convert(rd(file.path(root,'Inputs','external_specification_v3.csv')));wr(ext,'external_harmonization_audit.csv');ee<-ext[ext$include==1,]
for(cid in ee$cohort_id)fit(rbind(d,ee[ee$cohort_id==cid,]),paste0('boundary_add__',cid),'Overall cognition',paste('External boundary addition',cid))
fit(rbind(d,ee),'boundary_maximum_supported','Overall cognition','Maximum supported external expansion; not primary')
fit(ee[ee$source_row %in% c(67,222),],'boundary_mixed_route_only','Overall cognition','Mixed-route only')
wr(do.call(rbind,results),'all_model_results.csv');wr(do.call(rbind,skips),'models_not_run.csv');wr(do.call(rbind,members),'model_membership.csv')
comparison<-do.call(rbind,results);comparison<-comparison[grepl('^(old|old_retained|new)__',comparison$id),];wr(comparison,'old_versus_new.csv')
main<-fits[['new__Overall cognition']];stopifnot(!is.null(main))
# Moderator hypotheses retained; Holm adjustment is across the same three tests.
mr<-list()
for(m in c('population_group','schedule_group','domain_group')) {
 v<-factor(d[[m]]);counts<-table(v)
 if(length(counts)<2 || any(counts<3) || nrow(d)<10)mr[[m]]<-data.frame(moderator=m,status='Not eligible: insufficient category counts',F=NA,df1=NA,df2=NA,p=NA)
 else {f<-rma(d$hedges_g,d$sampling_variance,mods=~v,method='REML',test='knha');mr[[m]]<-data.frame(moderator=m,status='Exploratory eligible',F=f$QM,df1=f$QMdf[1],df2=f$QMdf[2],p=f$QMp)}
}
mr<-do.call(rbind,mr);mr$Holm_p<-p.adjust(mr$p,'holm',n=3);wr(mr,'moderators_Holm.csv')
small<-list()
for(dom in domains[1:4]) {
 x<-pick(d,dom);if(nrow(x)<10)next;f<-fits[[paste('new',dom,sep='__')]]
 eg<-regtest(f,model='rma',predictor='sei');be<-ranktest(f)
 small[[dom]]<-data.frame(domain=dom,k=nrow(x),Egger_stat=eg$zval,Egger_p=eg$pval,Begg_tau=be$tau,Begg_p=be$pval)
 tf<-trimfill(rma(x$hedges_g,x$sampling_variance,method='REML',test='z'));wr(data.frame(imputed=tf$k0,g=tf$b[1],ci_low=tf$ci.lb,ci_high=tf$ci.ub),'trimfill_exploratory.csv')
 pet<-rma(x$hedges_g,x$sampling_variance,mods=~sqrt(x$sampling_variance),method='REML',test='knha');peese<-rma(x$hedges_g,x$sampling_variance,mods=~x$sampling_variance,method='REML',test='knha')
 wr(data.frame(model=c('PET','PEESE'),g=c(pet$b[1],peese$b[1]),lo=c(pet$ci.lb[1],peese$ci.lb[1]),hi=c(pet$ci.ub[1],peese$ci.ub[1]),p=c(pet$pval[1],peese$pval[1])),'PET_PEESE_exploratory.csv')
 sm<-tryCatch(selmodel(rma(x$hedges_g,x$sampling_variance,method='ML',test='z'),type='stepfun',alternative='two.sided',steps=.05,control=list(optimizer='nlminb')),error=function(e)e)
 capture.output(print(sm),file=file.path(out,'selection_model_exploratory.txt'))
 if(!inherits(sm,'error'))wr(data.frame(g=sm$b[1],se=sm$se,ci_low=sm$ci.lb,ci_high=sm$ci.ub,p=sm$pval,tau2=sm$tau2,relative_selection=sm$delta[2],alternative='two.sided',optimizer='nlminb'),'selection_model_exploratory.csv')
}
if(length(small))wr(do.call(rbind,small),'small_study_tests.csv')
# Re-audit all prior extension rows; use only harmonizable rows from retained cohorts.
aa<-convert(allspec);wr(aa,'all_outcomes_audit.csv');aa<-aa[aa$include==1,]
if(any(aa$cohort_id=='COG-DOUGAL-2021' & aa$role=='secondary'))aa<-aa[aa$source_row!=29,]
aa$effect_id<-seq_len(nrow(aa));ml<-list()
for(rho in c(.2,.5,.8)) {
 V<-diag(aa$sampling_variance)
 for(cid in unique(aa$cohort_id)){ii<-which(aa$cohort_id==cid);V[ii,ii]<-rho*sqrt(outer(aa$sampling_variance[ii],aa$sampling_variance[ii]));diag(V)[ii]<-aa$sampling_variance[ii]}
 f<-rma.mv(aa$hedges_g,V,random=~1|cohort_id/effect_id,data=aa,method='REML');ct<-coef_test(f,vcov='CR2',cluster=aa$cohort_id,test='Satterthwaite')
 ml[[length(ml)+1]]<-data.frame(rho=rho,effects=nrow(aa),clusters=length(unique(aa$cohort_id)),g=ct$beta,se=ct$SE,df=ct$df_Satt,p=ct$p_Satt,lo=ct$beta-qt(.975,ct$df_Satt)*ct$SE,hi=ct$beta+qt(.975,ct$df_Satt)*ct$SE)
}
wr(ml<-do.call(rbind,ml),'multilevel_CR2.csv');wr(aa,'all_outcomes_harmonized.csv')
# Full paired-r by within-cohort outcome-rho grid for Supplementary Table S12.
grid<-list()
for(pr in c(.2,.5,.8)) {
 gx<-convert(allspec,pr);gx<-gx[gx$include==1,]
 if(any(gx$cohort_id=='COG-DOUGAL-2021' & gx$role=='secondary'))gx<-gx[gx$source_row!=29,]
 gx$effect_id<-seq_len(nrow(gx))
 for(rho in c(.2,.5,.8)) {
  V<-diag(gx$sampling_variance)
  for(cid in unique(gx$cohort_id)){ii<-which(gx$cohort_id==cid);V[ii,ii]<-rho*sqrt(outer(gx$sampling_variance[ii],gx$sampling_variance[ii]));diag(V)[ii]<-gx$sampling_variance[ii]}
  f<-rma.mv(gx$hedges_g,V,random=~1|cohort_id/effect_id,data=gx,method='REML');ct<-coef_test(f,vcov='CR2',cluster=gx$cohort_id,test='Satterthwaite')
  grid[[length(grid)+1]]<-data.frame(paired_r=pr,outcome_rho=rho,effects=nrow(gx),clusters=length(unique(gx$cohort_id)),g=ct$beta,se=ct$SE,df=ct$df_Satt,p=ct$p_Satt,lo=ct$beta-qt(.975,ct$df_Satt)*ct$SE,hi=ct$beta+qt(.975,ct$df_Satt)*ct$SE)
 }
}
wr(do.call(rbind,grid),'multilevel_grid_CR2.csv')
variants<-list(composite_only=convert(allspec),no_digitized_or_reconstructed=aa[aa$digitized==0 & aa$reconstructed==0,])
variants$composite_only<-variants$composite_only[variants$composite_only$include==1 & !(variants$composite_only$source_row %in% c(30,31)),]
mv<-list()
for(nm in names(variants))for(rho in c(.2,.5,.8)) {
 x<-variants[[nm]];x$effect_id<-seq_len(nrow(x));V<-diag(x$sampling_variance)
 for(cid in unique(x$cohort_id)){ii<-which(x$cohort_id==cid);V[ii,ii]<-rho*sqrt(outer(x$sampling_variance[ii],x$sampling_variance[ii]));diag(V)[ii]<-x$sampling_variance[ii]}
 f<-rma.mv(x$hedges_g,V,random=~1|cohort_id/effect_id,data=x,method='REML');ct<-coef_test(f,vcov='CR2',cluster=x$cohort_id,test='Satterthwaite')
 mv[[length(mv)+1]]<-data.frame(variant=nm,rho=rho,effects=nrow(x),clusters=length(unique(x$cohort_id)),g=ct$beta,se=ct$SE,df=ct$df_Satt,p=ct$p_Satt,lo=ct$beta-qt(.975,ct$df_Satt)*ct$SE,hi=ct$beta+qt(.975,ct$df_Satt)*ct$SE)
}
wr(do.call(rbind,mv),'multilevel_variants_CR2.csv')
# Source-based raw MMSE MD remains in its own units; no change-SD SMD mixing.
mm<-rd(file.path(root,'Original_snapshot','Approved_plan_outputs','mmse_raw_input.csv'));fm<-rma(mm$mean_difference,mm$sampling_variance,method='REML',test='knha');wr(data.frame(k=fm$k,MD=fm$b[1],lo=fm$ci.lb,hi=fm$ci.ub,p=fm$pval),'MMSE_raw_MD.csv')
saveRDS(fits,file.path(out,'models.rds'));capture.output(sessionInfo(),file=file.path(out,'sessionInfo.txt'))
cat('PASS: AQ4 models complete. Harmonized cohorts:',nrow(d),'\n')
