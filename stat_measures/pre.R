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
