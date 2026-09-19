options(stringsAsFactors=FALSE,warn=1)
invisible(Sys.setlocale('LC_CTYPE','English_United States.utf8'))
args<-commandArgs(FALSE);A<-dirname(normalizePath(sub('^--file=','',args[grepl('^--file=',args)][1]),winslash='/'));B<-dirname(A)
.libPaths(c(file.path(B,'Cognition/Reproducibility/R_library'),'C:/Users/fleck/AppData/Local/R/win-library/4.6',.libPaths()));library(metafor)
rd<-function(p)read.csv(p,check.names=FALSE,fileEncoding='UTF-8-BOM');wr<-function(x,n)write.csv(x,file.path(A,'Outputs',n),row.names=FALSE,na='')
checks<-list()
for(folder in c('Outputs','Working_corrected/Outputs'))for(r in c(.2,.5,.8)){
 d<-rd(file.path(A,folder,paste0('harmonization_r',r,'.csv')))
 for(i in seq_len(nrow(d))){z<-d[i,]
  if(z$route=='SMD')e<-escalc(measure='SMD',m1i=z$m1,m2i=z$m0,sd1i=z$sd1,sd2i=z$sd0,n1i=z$n1,n2i=z$n0,vtype='LS')
  if(z$route=='SMD_t')e<-escalc(measure='SMD',ti=z$t,n1i=z$n1,n2i=z$n0,vtype='LS')
  if(z$route=='SMD_d')e<-escalc(measure='SMD',di=z$reported_d,n1i=z$n1,n2i=z$n0,vtype='LS')
  if(z$route=='SMCRPH')e<-escalc(measure='SMCRPH',m1i=z$m1,m2i=z$m0,sd1i=z$sd1,sd2i=z$sd0,ni=z$n1,ri=r,vtype='LS2')
  if(z$route=='controlled_SMCRH'){
   arm<-function(delta,sd,post,change,n){
    if(z$imputed_r==1)change<-sqrt(sd^2+post^2-2*r*sd*post)
    escalc(measure='SMCRH',m1i=delta,m2i=0,sd1i=sd,sd2i=sqrt(sd^2+change^2),ri=sd/sqrt(sd^2+change^2),ni=n,vtype='LS2')
   }
   a<-arm(z$change1,z$preSD1,z$sd1,z$changeSD1,z$n1);b<-arm(z$change0,z$preSD0,z$sd0,z$changeSD0,z$n0);e<-data.frame(yi=a$yi-b$yi,vi=a$vi+b$vi)
  }
  checks[[length(checks)+1]]<-data.frame(version=folder,r=r,cohort=z$cohort_id,g_error=e$yi*z$sign-z$hedges_g,v_error=e$vi-z$sampling_variance)
 }
}
checks<-do.call(rbind,checks);stopifnot(max(abs(checks$g_error))<1e-10,max(abs(checks$v_error))<1e-10);wr(checks,'metafor_formula_checks.csv')
d<-rd(file.path(A,'Working_corrected/Outputs/harmonization_r0.5.csv'));fits<-readRDS(file.path(A,'Working_corrected/Outputs/audit_models.rds'))
dir.create(file.path(A,'Working_corrected/Figures'),showWarnings=FALSE)
for(dom in c('Overall cognition','Memory','Global cognition','Executive / sustained attention')){
 x<-if(dom=='Overall cognition')d else d[d$domain==dom,];f<-fits[[paste0('primary__',dom)]]
 png(file.path(A,'Working_corrected/Figures',paste0(gsub('[^A-Za-z]+','_',dom),'.png')),width=2200,height=max(1000,nrow(x)*65+450),res=180)
 par(mar=c(5,4,4,3));forest(f,slab=iconv(x$study,to='ASCII//TRANSLIT'),main=paste('Audited:',dom),xlab='Hedges g (positive favors active treatment)',addpred=nrow(x)>=5,mlab='REML / unmodified Hartung-Knapp',cex=.8);dev.off()
}
# Recover rounded-t / digitization robustness from explicit coordinate perturbations.
grid<-expand.grid(a19=c(-1,1),c19=c(-1,1),a21=c(-1,1),c21=c(-1,1),t19=c(-1,1),t21=c(-1,1),mean19=c(-1,1));rr<-list()
J<-function(df)exp(lgamma(df/2)-.5*log(df/2)-lgamma((df-1)/2))
for(j in seq_len(nrow(grid))){z<-d;q<-grid[j,]
 for(row in c(22,58)){
  i<-which(z$source_row==row);is19<-row==22;delta<-if(is19)2/6.81*sqrt(15) else 1/3.8375*3
  z$preSD1[i]<-z$preSD1[i]+delta*if(is19)q$a19 else q$a21;z$preSD0[i]<-z$preSD0[i]+delta*if(is19)q$c19 else q$c21
  if(is19){z$change1[i]<-z$change1[i]+q$mean19*4/6.81;z$change0[i]<-z$change0[i]-q$mean19*4/6.81}
  ta<-if(is19)2.14+q$t19*.005 else 2.3+q$t21*.05;tc<-if(is19).79+q$t19*.005 else .3+q$t21*.05
  s1<-abs(z$change1[i])*sqrt(z$n1[i])/ta;s0<-abs(z$change0[i])*sqrt(z$n0[i])/tc
  ga<-J(z$n1[i]-1)*z$change1[i]/z$preSD1[i];gb<-J(z$n0[i]-1)*z$change0[i]/z$preSD0[i]
  z$hedges_g[i]<-z$sign[i]*(ga-gb);z$sampling_variance[i]<-s1^2/(z$n1[i]*z$preSD1[i]^2)+ga^2/(2*z$n1[i])+s0^2/(z$n0[i]*z$preSD0[i]^2)+gb^2/(2*z$n0[i])
 }
 for(dom in c('Overall cognition','Memory','Executive / sustained attention')){x<-if(dom=='Overall cognition')z else z[z$domain==dom,];f<-rma(x$hedges_g,x$sampling_variance,method='REML',test='knha');rr[[length(rr)+1]]<-data.frame(scenario=j,domain=dom,g=f$b[1],lo=f$ci.lb,hi=f$ci.ub,p=f$pval)}
}
wr(do.call(rbind,rr),'corrected_rounding_sensitivity.csv')
# Separate exploratory reappraisal of historical no-concern flag rule.
lock<-rd(file.path(A,'Inputs/locked.csv'));good<-lock$cohort_id[grepl('^no major',lock$risk_of_bias_flag)]
rr<-list();mem<-list()
for(dom in c('Overall cognition','Memory','Global cognition','Executive / sustained attention')){x<-if(dom=='Overall cognition')d else d[d$domain==dom,];mem[[dom]]<-data.frame(domain=dom,cohort_id=x$cohort_id,included=x$cohort_id %in% good);x<-x[x$cohort_id %in% good,];if(nrow(x)<3)next;f<-rma(x$hedges_g,x$sampling_variance,method='REML',test='knha');rr[[dom]]<-data.frame(domain=dom,k=f$k,g=f$b[1],lo=f$ci.lb,hi=f$ci.ub,p=f$pval)}
wr(do.call(rbind,rr),'corrected_no_explicit_concern.csv');wr(do.call(rbind,mem),'no_explicit_concern_membership.csv')
cat('PASS 102 package formula cross-checks, corrected figures, 128 rounding scenarios, stricter historical flag sensitivity\n')
