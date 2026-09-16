d1 <- data_measures
View(d1)
d1$Condition <- as.factor(d1$Condition)
d1$Sem_Distance <- as.numeric(as.character(d1$Sem_Distance))

# T-test of semantic distance between sameT and diffT conditions
t.test(Sem_Distance ~ Condition, data = subset(d1, Condition %in% c("sameT", "diffT")))

# T-test of semantic distance between sameT and noP conditions
t.test(Sem_Distance ~ Condition, data = subset(d1, Condition %in% c("sameT", "noP")))


# T-test of Levenshtein distance between sameT and diffT 
t.test(Levenshtein_Distance ~ Condition, data = subset(d1, Condition %in% c("sameT", "diffT")))

t.test(Levenshtein_Distance ~ Condition, data = subset(d1, Condition %in% c("sameT", "noP")))

library(ggstatsplot)
library(patchwork)

d1 <- na.omit(d1[, c("Condition", "StrokeDiff", "Sem_Distance", "Levenshtein_Distance")])

plotComparison <- function(dta, comment = '') {
  pSt = ggwithinstats(
    data = dta,
    x = Condition,
    y = StrokeDiff,
    title = paste('Stroke Difference Comparison', comment, sep = ' - '),
    type = 'np'
  )
  pSe = ggwithinstats(
    data = dta,
    x = Condition,
    y = Sem_Distance,
    title = paste('Semantic Distance Comparison', comment, sep = ' - '),
    type = 'p'
  )
  pLd = ggwithinstats(
    data = dta,
    x = Condition,
    y = Levenshtein_Distance,
    title = paste('Levenshtein Distance Comparison', comment, sep = ' - '),
    type = 'np'
  )
  
  p = pSt + pSe + pLd + plot_layout(ncol = 3)
  return(p)
}

# Per eseguirla:
plotComparison(d1, 'Whole Group')
