options(stringsAsFactors=FALSE,warn=1)
invisible(Sys.setlocale('LC_CTYPE','English_United States.utf8'))
args<-commandArgs(FALSE);A<-dirname(normalizePath(sub('^--file=','',args[grepl('^--file=',args)][1]),winslash='/'));B<-dirname(A)
.libPaths(c(file.path(B,'Cognition/Reproducibility/R_library'),.libPaths()));library(metafor)
rd<-function(p)read.csv(p,fileEncoding='UTF-8-BOM');d<-rd(file.path(A,'Working_corrected/Outputs/harmonization_r0.5.csv'));m<-rd(file.path(A,'parameter_metadata.csv'));d<-merge(d,m,by='cohort_id',sort=FALSE)
out<-list();members<-list()
for(v in c('pulse','device','comparator_intensity','industry_status')){
 x<-if(v=='pulse')d[d$pulse %in% c('CW','PW'),] else d
 x$moderator<-factor(x[[v]]);stopifnot(min(table(x$moderator))>=3)
 f<-rma(hedges_g,sampling_variance,mods=~moderator,data=x,method='REML',test='knha')
 out[[v]]<-data.frame(moderator=v,k=f$k,categories=paste(names(table(x$moderator)),table(x$moderator),collapse='; '),F=f$QM,df1=f$QMdf[1],df2=f$QMdf[2],p=f$QMp,status='Post-results audit of SAP exploratory hypothesis; unadjusted; association only')
 members[[v]]<-data.frame(moderator=v,cohort_id=x$cohort_id,category=x$moderator,population=x$population_group,domain=x$domain,schedule=x$schedule_group)
}
write.csv(do.call(rbind,out),file.path(A,'Outputs/exploratory_parameter_tests.csv'),row.names=FALSE)
write.csv(do.call(rbind,members),file.path(A,'Outputs/exploratory_parameter_membership.csv'),row.names=FALSE)
capture.output(with(d,table(pulse,domain)),with(d,table(device,schedule_group)),with(d,table(pulse,schedule_group)),file=file.path(A,'Outputs/parameter_confounding.txt'))
