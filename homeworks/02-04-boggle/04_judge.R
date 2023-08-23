library(data.table)
library(ggplot2)
setwd("~/teaching/cs470-570-spring-2023/homeworks/")
py.file.vec <- Sys.glob("boggle/*.py")
board.txt <- "board4_test.txt"
words.txt <- sub(".txt", "_words.txt", board.txt)
solution.txt <- sub(".txt", "_solution.txt", board.txt)
read.words <- function(txt.file){
  wdt <- tryCatch({
    data.table::fread(txt.file, col.names="word", header=FALSE)
  }, error=function(e){
    data.table()
  })
  if(nrow(wdt)==0){
    wdt <- data.table(word=character())
  }
  wdt
}
solution.dt <- read.words(solution.txt)
result.dt.list <- list()
system("python3 --version")
for(py.file in py.file.vec){
  py.cmd <- paste("python3", py.file, board.txt, "twl06.txt")
  program <- basename(sub(".py$", "", py.file))
  for(iteration in 1:3){
    unlink(words.txt)
    timing <- system.time({
      system(py.cmd)
    })
    words.dt <- read.words(words.txt)[, word := toupper(word)]
    false.positives <- words.dt[!solution.dt, on="word"]
    false.negatives <- solution.dt[!words.dt, on="word"]
    result.dt.list[[paste(py.file, iteration)]] <- data.table(
      program, iteration,
      FP=nrow(false.positives), FN=nrow(false.negatives), 
      seconds=timing[["elapsed"]])
  }
}
(result.dt <- rbindlist(result.dt.list))
zero.err <- result.dt[FP+FN==0]
zero.err[, median := median(seconds), by=program]
setkey(zero.err, median)
zero.err[, Program := factor(program, unique(program))]
ggplot()+
  geom_point(aes(
    seconds, Program),
    data=zero.err)
    
