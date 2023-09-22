library(data.table)
library(ggplot2)
setwd("~/teaching/2023-08-artificial-intelligence/homeworks/02-04-boggle/")
(py.file.vec <- Sys.glob("04_judge/*.py"))
board.txt <- "competition_board.txt"
board.size <- 5
python <- "~/.local/share/r-miniconda/envs/2023-08-artificial-intelligence/bin/python"
system(paste(python, "04_generator.py", board.size, board.txt))
words.txt <- sub(".txt", "_words.txt", board.txt)
system(paste("python 04_solution.py", board.txt))
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
for(py.file in py.file.vec){
  py.cmd <- paste(python, py.file, board.txt, "twl06.txt")
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
  theme(text=element_text(size=20))+
  geom_point(aes(
    seconds, Program),
    data=zero.err)
    
