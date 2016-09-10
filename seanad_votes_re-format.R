getwd()
rm(list=ls())
setwd('~/Desktop/gitstuff/ireland_minutes')
getwd()
list.files()

#rc_full = read.csv('seanad_sep12-cur_votes.csv', stringsAsFactors = F)
rc_full = read.csv('seanad_jan04-sep12_votes.csv', stringsAsFactors = F)
names = names(rc_full)
rc_full = as.matrix(rc_full)
names(rc_full) = names

rc_no_leg = rc_full[,1:9]

for (r in 1:nrow(rc_no_leg)){
  if (r%%2==1){
      if (any(rc_no_leg[r,1:6]!=(rc_no_leg[r+1,1:6]))){
          print("problem")  }
  }
}
## no problem! All pairs of rows match up perfectly, except for TA/NIL split

rc_by_vote = rep(NA,9)

## creating new matrix, where TA and NIL tallies are in same row
for (r in 1:nrow(rc_no_leg)){
  if (r%%2==1){
    new_row = c(rc_no_leg[r,1:7],rc_no_leg[r,9],rc_no_leg[r+1,9])
    rc_by_vote = rbind(rc_by_vote,new_row)
  }
}
rownames(rc_by_vote)=NULL

colnames(rc_by_vote) = c(colnames(rc_no_leg)[1:7],"TA_Tally", "NIL_Tally")


## dropping first row (which was all NAs, as a placeholder)
rc_by_vote = rc_by_vote[-1,]

months = c('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September','October', 'November', 'December')

## adding a column of NAs at the back, to be replaced by numeric month value
rc_by_vote= cbind( rc_by_vote, rep(NA,nrow(rc_by_vote)))
rc_by_vote= cbind( rc_by_vote, rep(NA,nrow(rc_by_vote))) ## run both lines as written

for (r in 1:nrow(rc_by_vote)) {
  rc_by_vote[r,ncol(rc_by_vote)-1]=(which(months==rc_by_vote[r,"Month"],arr.ind=T))
  rc_by_vote[r,ncol(rc_by_vote)] = paste( c(rc_by_vote[r,1],rc_by_vote[r,ncol(rc_by_vote)-1],rc_by_vote[r,3]), collapse = "/")
}
colnames(rc_by_vote)[10:11] = c("numeric_month","numeric_date")


#Number = c(1:nrow(rc_by_vote))
## number, file_name, date, subject, result, ta_tally, nil_tally
#vote_output = cbind(Number,rc_by_vote[,5],rc_by_vote[,11],rc_by_vote[,6:9])
vote_output = cbind(rc_by_vote[,5],rc_by_vote[,11],rc_by_vote[,6:9])

colnames(vote_output)[1:2] = c("File","Date")

write.csv(vote_output,"IrelandSeanadJan04toSep12-Votes.csv")
