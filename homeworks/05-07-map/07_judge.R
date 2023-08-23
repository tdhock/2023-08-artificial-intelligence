library(data.table)
library(ggplot2)
this.dir <- "~/teaching/cs470-570-spring-2023/homeworks/05-07-map/"
setwd(this.dir)
(py.file.vec <- Sys.glob("07_judge/*.py"))
get.out <- function(file.py, suffix="path", txt.file="50test.txt", search.type="BREADTH", start="K", goal="C"){
  out.txt <- sub(".txt$", paste0("_", suffix, ".txt"), txt.file)
  unlink(out.txt)
  cmd <- paste(
    paste0("PYTHONPATH=", this.dir),
    "/home/tdhock/.local/share/r-miniconda/envs/cs470s23/bin/python", file.py, txt.file, search.type, start, goal)
  system(cmd)
  tryCatch({
    readLines(out.txt)[1]
  }, error=function(e){
    NA_character_
  })
}
solution <- get.out("solution.py", "solution")

result.dt.list <- list()
for(py.file in py.file.vec){
  for(iteration in 1:3){
    timing <- system.time({
      raw.path <- get.out(py.file, "path")
    })
    path <- sub(",$", "", gsub(" ", "", raw.path))
    result.dt.list[[paste(py.file, iteration)]] <- data.table(
      program=gsub("07_judge/|.py","",py.file), iteration,
      path,
      correct=identical(path, solution),
      seconds=timing[["elapsed"]])
  }
}
result.dt <- rbindlist(result.dt.list)
result.dt[, .(program, path=substr(path, 1,10), correct)]

zero.err <- result.dt[correct==TRUE]
zero.err[, median := median(seconds), by=program]
setkey(zero.err, median)
zero.err[, Program := factor(program, unique(program))]
ggplot()+
  theme(text=element_text(size=40))+
  geom_point(aes(
    seconds, Program),
    data=zero.err)+
  scale_x_log10()
    
## DEPTH: vertin, Persley, Siegel, Valdivia

## BEST: Persley, Valdivia

## BREADTH: vertin, Persley, Valdivia

## Vertin 30 EC 1st place, Persley 20 EC 2nd place, Valdivia/Siegel 10
## EC 3rd place. Participation: 5EC for Carlile, Watlington.
