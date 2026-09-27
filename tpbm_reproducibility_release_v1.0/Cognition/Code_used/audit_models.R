options(stringsAsFactors=FALSE,warn=1)
invisible(Sys.setlocale('LC_CTYPE','English_United States.utf8'))
args<-commandArgs(FALSE);A<-dirname(normalizePath(sub('^--file=','',args[grepl('^--file=',args)][1]),winslash='/'));B<-dirname(A)
extra<-commandArgs(TRUE);if(length(extra))A<-normalizePath(extra[1],winslash='/')
.libPaths(c(file.path(B,'Cognition/Reproducibility/R_library'),.libPaths()))
library(metafor);library(clubSandwich)
rd<-function(p)read.csv(p,check.names=FALSE,fileEncoding='UTF-8-BOM')
wr<-function(x,n)write.csv(x,file.path(A,'Outputs',n),row.names=FALSE,na='')
loadr<-function(kind='harmonization',r=.5)rd(file.path(A,'Outputs',paste0(kind,'_r',r,'.csv')))
d<-loadr();old<-rd(file.path(A,'Inputs/historical_coding.csv'));locked<-rd(file.path(A,'Inputs/locked.csv'))
results<-list();members<-list();skips<-list();fits<-list()
fit<-function(x,id,method='REML',test='knha',universe=d){
 members[[length(members)+1]]<<-data.frame(model=id,cohort_id=universe$cohort_id,included=universe$cohort_id %in% x$cohort_id)
 if(nrow(x)<3){skips[[length(skips)+1]]<<-data.frame(model=id,k=nrow(x),reason='Fewer than three cohorts');return(NULL)}
 f<-rma.uni(yi=x$hedges_g,vi=x$sampling_variance,method=method,test=test,control=list(threshold=1e-10,maxiter=1000));p<-predict(f)
 results[[length(results)+1]]<<-data.frame(model=id,k=f$k,g=f$b[1],se=f$se,df=if(test=='z')NA else f$k-f$p,p=f$pval,lo=f$ci.lb,hi=f$ci.ub,tau2=f$tau2,I2=f$I2,Q=f$QE,Qdf=f$k-f$p,HK_scale=if(is.null(f$s2w))NA else f$s2w,pi_lo=if(f$k>=5&&method!='FE')p$pi.lb else NA,pi_hi=if(f$k>=5&&method!='FE')p$pi.ub else NA,method=method,test=test)
 fits[[id]]<<-f;f
}
doms<-c('Overall cognition','Memory','Global cognition','Executive / sustained attention')
pick<-function(x,dom)if(dom=='Overall cognition')x else x[x$domain==dom,]
for(dom in doms){
 x<-pick(d,dom);f<-fit(x,paste0('primary__',dom),universe=x)
 fit(pick(old,dom),paste0('historical__',dom),universe=old)
 fit(pick(old,dom)[pick(old,dom)$cohort_id %in% d$cohort_id,],paste0('historical_retained__',dom),universe=old)
 restrictions<-list(no_major_rob=x$major_rob==0,parallel_only=x$design_group=='Parallel-group',no_digitization=x$digitized==0,no_reconstruction=x$reconstructed==0,no_imputed_r=x$imputed_r==0,zero_output=x$comparator_intensity=='No therapeutic light/control',no_industry=x$industry_status=='No documented industry association',endpoint_only=x$route %in% c('SMD','SMD_t','SMD_d','SMCRPH'),controlled_change_only=x$route=='controlled_SMCRH',exclude_Yang=x$cohort_id!='COG-YANG-2025-OLDER-WM',exclude_ZhaoX=x$cohort_id!='COG-ZHAO-X-2022-SCD')
 # Explicit stricter extraction rule includes SD-from-SE and reported-d routes.
 restrictions$strict_no_reconstruction<-x$reconstructed==0 & !x$cohort_id %in% c('COG-DOUGAL-2021','COG-SALEHPOUR-2026-STAGE1-ADHD')
 for(n in names(restrictions))fit(x[restrictions[[n]],],paste(dom,n,sep='__'),universe=x)
 for(r in c(.2,.8))fit(pick(loadr(r=r),dom),paste(dom,'paired_r',r,sep='__'),universe=x)
 for(tt in c('adhoc','z'))fit(x,paste(dom,tt,sep='__'),test=tt,universe=x)
 fit(x,paste(dom,'PM',sep='__'),method='PM',universe=x)
 fit(x,paste(dom,'FE',sep='__'),method='FE',test='z',universe=x)
 loo<-as.data.frame(leave1out(f));wr(data.frame(cohort_id=x$cohort_id,loo),paste0('LOO_',gsub('[^A-Za-z]+','_',dom),'.csv'))
 inf<-influence(f);wr(data.frame(cohort_id=x$cohort_id,as.data.frame(inf$inf)),paste0('influence_',gsub('[^A-Za-z]+','_',dom),'.csv'))
}
ex<-loadr('external');fit(rbind(d,ex),'external_expansion',universe=rbind(d,ex))
for(i in seq_len(nrow(ex)))fit(rbind(d,ex[i,]),paste0('external_add__',ex$cohort_id[i]),universe=rbind(d,ex))
mm<-rd(file.path(A,'Inputs/historical_mmse.csv'));fm<-rma(mm$mean_difference,mm$sampling_variance,method='REML',test='knha');wr(data.frame(mm), 'MMSE_membership.csv');wr(data.frame(k=fm$k,MD=fm$b[1],lo=fm$ci.lb,hi=fm$ci.ub,p=fm$pval),'MMSE_result.csv')
mods<-list();cats<-list()
for(n in c('population_group','schedule_group','domain_group')){
 x<-d[!is.na(d[[n]])&d[[n]]!='',];x$moderator<-factor(x[[n]]);f<-rma(hedges_g,sampling_variance,mods=~moderator,data=x,method='REML',test='knha')
 mods[[n]]<-data.frame(moderator=n,k=nrow(x),missing=nrow(d)-nrow(x),F=f$QM,df1=f$QMdf[1],df2=f$QMdf[2],p=f$QMp)
 cats[[n]]<-data.frame(moderator=n,cohort_id=x$cohort_id,category=x$moderator,n_unique=ifelse(x$route=='SMCRPH',x$n1,x$n1+x$n0))
}
mods<-do.call(rbind,mods);mods$Holm<-p.adjust(mods$p,'holm',n=3);wr(mods,'moderators.csv');wr(do.call(rbind,cats),'moderator_membership.csv')
f<-fits[['primary__Overall cognition']];eg<-regtest(f,model='rma',predictor='sei');be<-ranktest(f)
wr(data.frame(Egger_stat=eg$zval,Egger_df=eg$dfs,Egger_p=eg$pval,Begg_tau=be$tau,Begg_p=be$pval),'small_study.csv')
tf<-trimfill(rma(d$hedges_g,d$sampling_variance,method='REML',test='z'));wr(data.frame(added=tf$k0,g=tf$b[1],lo=tf$ci.lb,hi=tf$ci.ub),'trimfill.csv')
d$SE<-sqrt(d$sampling_variance)
pet<-rma(hedges_g,sampling_variance,mods=~SE,data=d,method='REML',test='knha');peese<-rma(hedges_g,sampling_variance,mods=~sampling_variance,data=d,method='REML',test='knha')
wr(data.frame(model=c('PET','PEESE'),g=c(pet$b[1],peese$b[1]),lo=c(pet$ci.lb[1],peese$ci.lb[1]),hi=c(pet$ci.ub[1],peese$ci.ub[1]),slope_p=c(pet$pval[2],peese$pval[2])),'PET_PEESE.csv')
sm<-selmodel(rma(d$hedges_g,d$sampling_variance,method='ML',test='z'),type='stepfun',alternative='two.sided',steps=.05,control=list(optimizer='nlminb'))
wr(data.frame(g=sm$b[1],lo=sm$ci.lb,hi=sm$ci.ub,tau2=sm$tau2,selection_weight=sm$delta[2]),'selection.csv');capture.output(sm,file=file.path(A,'Logs/selection.txt'))
ml<-list();mlmembers<-list()
for(pair in c(.2,.5,.8))for(rho in c(.2,.5,.8))for(variant in c('components','composite','no_digitized_reconstructed')){
 aa<-loadr('all_outcomes',pair);aa<-aa[if(variant=='composite')!aa$source_row %in% c(30,31) else aa$source_row!=29,]
 if(variant=='no_digitized_reconstructed')aa<-aa[aa$digitized==0 & aa$reconstructed==0,]
 aa$eid<-seq_len(nrow(aa));V<-diag(aa$sampling_variance)
 for(cid in unique(aa$cohort_id)){ii<-which(aa$cohort_id==cid);V[ii,ii]<-rho*sqrt(outer(aa$sampling_variance[ii],aa$sampling_variance[ii]));diag(V)[ii]<-aa$sampling_variance[ii]}
 stopifnot(min(eigen(V,symmetric=TRUE,only.values=TRUE)$values)>0)
 mv<-rma.mv(hedges_g,V,random=~1|cohort_id/eid,data=aa,method='REML');ct<-coef_test(mv,vcov='CR2',cluster=aa$cohort_id,test='Satterthwaite')
 ml[[length(ml)+1]]<-data.frame(variant=variant,paired_r=pair,rho=rho,effects=nrow(aa),cohorts=length(unique(aa$cohort_id)),g=ct$beta,se=ct$SE,df=ct$df_Satt,lo=ct$beta-qt(.975,ct$df_Satt)*ct$SE,hi=ct$beta+qt(.975,ct$df_Satt)*ct$SE,p=ct$p_Satt,tau_cohort=mv$sigma2[1],tau_effect=mv$sigma2[2])
 if(pair==.5&&rho==.5)mlmembers[[variant]]<-data.frame(variant=variant,cohort_id=aa$cohort_id,outcome_id=aa$outcome_id,source_row=aa$source_row)
}
wr(do.call(rbind,ml),'multilevel.csv');wr(do.call(rbind,mlmembers),'multilevel_membership.csv')
wr(do.call(rbind,results),'model_results.csv');wr(do.call(rbind,members),'sensitivity_membership.csv');wr(do.call(rbind,skips),'models_not_run.csv')
saveRDS(fits,file.path(A,'Outputs/audit_models.rds'));capture.output(sessionInfo(),file=file.path(A,'Logs/R_session.txt'))
cat('PASS independent R refits:',length(results),'models;',length(ml),'multilevel models\n')
