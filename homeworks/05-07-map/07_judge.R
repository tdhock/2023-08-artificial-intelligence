library(data.table)
library(ggplot2)
this.dir <- "~/teaching/2023-08-artificial-intelligence/homeworks/05-07-map/"
setwd(this.dir)
(py.file.vec <- Sys.glob("07_judge/*.py"))
txt.file="30node.txt"
python=paste(
  paste0("PYTHONPATH=", this.dir),
  "/home/tdhock/.local/share/r-miniconda/envs/cs470s23/bin/python")
get.out <- function(file.py, suffix="path", search.type="DEPTH", start="K", goal="C"){
  out.txt <- sub(".txt$", paste0("_", suffix, ".txt"), txt.file)
  unlink(out.txt)
  cmd <- paste(
    python, file.py, txt.file, search.type, start, goal)
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
    cmd.out <- system(paste(python, "cost.py", txt.file, path), intern=TRUE)
    cost <- as.integer(cmd.out)
    if(length(cost)==0)cost <- NA
    result.dt.list[[paste(py.file, iteration)]] <- data.table(
      program=gsub("07_judge/|.py","",py.file), iteration,
      path,
      cost,
      correct=identical(path, solution),
      seconds=timing[["elapsed"]])
  }
}
(result.dt <- rbindlist(result.dt.list))
result.dt[order(cost), .(program, cost, path=substr(path, 1,10), 
plen=sapply(strsplit(result.dt$path,","),length), correct)]

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
    
## 1st Bruce Angus
## 2nd Milizia Nathan
## 3rd Karlsson Kirk Perez Salazar Bauck
## Participation chase mcauslin smith


