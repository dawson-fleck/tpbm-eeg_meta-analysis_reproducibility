# Standalone descriptive EEG estimates, independent numeric checks, no pooled models.
if (.Platform$OS.type=='windows') invisible(Sys.setlocale('LC_CTYPE','English_United States.utf8'))
args <- commandArgs(trailingOnly=FALSE)
here <- dirname(normalizePath(sub('^--file=', '', args[grepl('^--file=',args)][1]), winslash='/'))
root <- dirname(here); out <- file.path(root,'Outputs'); fig <- file.path(out,'Figures')
dir.create(fig,showWarnings=FALSE)
read <- function(path) read.csv(path,check.names=FALSE,fileEncoding='UTF-8-BOM',stringsAsFactors=FALSE)
d <- read(file.path(root,'Inputs','EEG_effects_audited.csv'))
a <- d[d$eligible_for_new_pool==1,]
stopifnot(nrow(d)==212,nrow(a)==207,length(unique(a$cluster_id))==9,all(a$vi>0),!anyDuplicated(a$effect_id))
gate <- read(file.path(out,'EEG_compatibility_gates.csv'))
stopifnot(all(gate$independent_datasets_upper_bound<3))
a$se <- sqrt(a$vi); a$ci_low <- a$g-qnorm(.975)*a$se; a$ci_high <- a$g+qnorm(.975)*a$se
a$interval_note <- 'Approximate unadjusted Wald interval; recorded variance assumptions; descriptive only'
write.csv(a,file.path(out,'EEG_study_level_estimates.csv'),row.names=FALSE,na='')

# Independent R reconstruction of all digitized Chaudhari cells and both n scenarios.
raw <- read(file.path(root,'Reproducibility','Source_snapshots','Chaudhari_digitized.csv'))
s <- read(file.path(out,'EEG_Chaudhari_sample_size_sensitivity.csv'))
c <- a[a$study_key=='Chaudhari',]
net <- as.integer(sub('.*(?:network | N)([0-9]+).*','\\1',c$metric,perl=TRUE))
tp <- sub('.*(TP[12])$','\\1',c$timing_group)
idx <- match(paste(tp,c$band,net),paste(raw$TP,raw$band,raw$network))
stopifnot(!anyNA(idx)); rr <- raw[idx,]
j <- 1-3/55
g88 <- j*(rr$tpbm_mean-rr$sham_mean)/sqrt((7*8*rr$tpbm_sem^2+7*8*rr$sham_sem^2)/14)
g79 <- j*(rr$tpbm_mean-rr$sham_mean)/sqrt((6*7*rr$tpbm_sem^2+8*9*rr$sham_sem^2)/14)
si <- match(c$effect_id,s$effect_id)
checks <- data.frame(effect_id=c$effect_id,g88_error=abs(g88-c$g),v88_error=abs(.25+g88^2/28-c$vi),g79_error=abs(g79-s$sensitivity_g[si]),v79_error=abs(1/7+1/9+g79^2/28-s$sensitivity_vi[si]))
stopifnot(max(as.matrix(checks[,-1]))<1e-7)
write.csv(checks,file.path(out,'EEG_independent_R_checks.csv'),row.names=FALSE)
s$ci_low <- s$sensitivity_g-qnorm(.975)*sqrt(s$sensitivity_vi)
s$ci_high <- s$sensitivity_g+qnorm(.975)*sqrt(s$sensitivity_vi)
write.csv(s,file.path(out,'EEG_Chaudhari_sensitivity_intervals.csv'),row.names=FALSE)

# Keep separate panels for dependent outcomes. These are not pooled forest plots.
ascii <- function(x) {x<-gsub('\u2192',' -> ',x,fixed=TRUE);iconv(x,to='ASCII//TRANSLIT',sub='?')}
panel <- ifelse(a$study_key %in% c('Chaudhari','Wang2022'),paste(a$study_key,a$band,a$timing_group,sep=' | '),a$study_key)
pages <- split(seq_len(nrow(a)),panel)
draw <- function(z,title) {
 n<-nrow(z); par(mar=c(6.5,15,4,2)); lim<-range(c(z$ci_low,z$ci_high,0)); pad<-max(diff(lim)*.08,.2)
 plot(z$g,rev(seq_len(n)),xlim=lim+c(-pad,pad),ylim=c(.3,n+.7),yaxt='n',ylab='',xlab='Recorded Hedges g (metric-specific sign)',pch=19,col='#195B80',main=title,cex.main=.9)
 segments(z$ci_low,rev(seq_len(n)),z$ci_high,rev(seq_len(n)),col='#195B80');abline(v=0,lty=2,col='gray60')
 labs<-if(z$study_key[1]=='Spera')paste(z$metric,z$state) else z$metric
 axis(2,at=rev(seq_len(n)),labels=ascii(labs),las=1,cex.axis=.75)
 mtext('Study-level estimates; dependent rows; approximate 95% intervals; no pooled estimate',side=1,line=5,cex=.7)
}
pdf(file.path(fig,'EEG_study_level_panels.pdf'),width=11,height=7.5,onefile=TRUE)
for(p in names(pages))draw(a[pages[[p]],],p)
dev.off()
for(i in seq_along(pages)) {
 png(file.path(fig,sprintf('EEG_panel_%02d.png',i)),width=1650,height=1125,res=150)
 draw(a[pages[[i]],],names(pages)[i]);dev.off()
}
write.csv(data.frame(page=seq_along(pages),panel=names(pages),effects=sapply(pages,length)),file.path(out,'EEG_figure_index.csv'),row.names=FALSE)
capture.output(sessionInfo(),file=file.path(out,'R_sessionInfo.txt'))
cat('PASS: 207 descriptive estimates; 120 independent four-part sensitivity checks;',length(pages),'figure panels; zero eligible pooled models.\n')
