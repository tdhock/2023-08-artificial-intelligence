if(!file.exists("ESL.mixture.rda")){
  download.file(
    "https://web.stanford.edu/~hastie/ElemStatLearn/datasets/ESL.mixture.rda",
    "ESL.mixture.rda")
}
load("ESL.mixture.rda")
str(ESL.mixture)
library(data.table)
norm.to <- function(z,to)z-mean(z)+to
mixture.dt <- with(ESL.mixture, data.table(
  party=ifelse(y==0, "democratic", "republican"),
  height_in=norm.to(x[,1], 70),
  weight_lb=norm.to(x[,2], 150)))
library(ggplot2)
ggplot()+
  geom_point(aes(
    height_in, weight_lb, color=party),
    data=mixture.dt)+
  scale_color_manual(values=c(democratic="blue", republican="red"))
fwrite(mixture.dt, "ESL.mixture.csv", col.names=TRUE)
