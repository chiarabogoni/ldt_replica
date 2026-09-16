# ============================================================================
# List Assignment and Counterbalancing
# ============================================================================

# Verify item count is divisible by 6 for balanced assignment across all groups
it = levels(factor(d$Item))

if ((length(it) %% 6) != 0) {
  warning('Item number not divisible by 6')
}

# Design matrix: each list contains all 54 items.
# L1-L3 rotate corr, diffT, and sameT; L4-L6 rotate corr, noP, and sameT.
des = data.frame(
  Group = c(rep('G1', 3), rep('G2', 3), rep('G3', 3),
            rep('G4', 3), rep('G5', 3), rep('G6', 3)),
  Condition = c('corr', 'diffT', 'sameT', 'diffT', 'sameT', 'corr',
                'sameT', 'corr', 'diffT', 'corr', 'noP', 'sameT',
                'noP', 'sameT', 'corr', 'sameT', 'corr', 'noP'),
  List = c('L1', 'L2', 'L3', 'L1', 'L2', 'L3', 'L1', 'L2', 'L3',
           'L4', 'L5', 'L6', 'L4', 'L5', 'L6', 'L4', 'L5', 'L6')
)

# Random assignment of items to one old-list group and one noP-list group.
# Every item therefore appears once in each of L1-L3 and once in each of L4-L6.
# Seed: 60224 provides reproducible balance across lists.
set.seed(60224)
grp_old = data.frame(
  Item = it,
  Group = sample(rep(c('G1', 'G2', 'G3'), length(it) / 3))
)
grp_new = data.frame(
  Item = it,
  Group = sample(rep(c('G4', 'G5', 'G6'), length(it) / 3))
)

des_old = subset(des, Group %in% c('G1', 'G2', 'G3'))
des_new = subset(des, Group %in% c('G4', 'G5', 'G6'))

d2_old = merge(d, merge(grp_old, des_old), by = c('Item', 'Condition'))
d2_new = merge(d, merge(grp_new, des_new), by = c('Item', 'Condition'))
d2 = rbind(d2_old, d2_new)

list_counts = table(d2$List)
if (any(list_counts != length(it))) {
  stop('Each list must contain exactly one row per item')
}
print(list_counts)

# Generate comparison plots for each list
pL1 = plotComparison(subset(d2, d2$List == 'L1' & Condition != 'corr'), 'List 1')
pL2 = plotComparison(subset(d2, d2$List == 'L2' & Condition != 'corr'), 'List 2')
pL3 = plotComparison(subset(d2, d2$List == 'L3' & Condition != 'corr'), 'List 3')
pL4 = plotComparison(subset(d2, d2$List == 'L4' & Condition != 'corr'), 'List 4')
pL5 = plotComparison(subset(d2, d2$List == 'L5' & Condition != 'corr'), 'List 5')
pL6 = plotComparison(subset(d2, d2$List == 'L6' & Condition != 'corr'), 'List 6')
balance_plots = pL1 / pL2 / pL3 / pL4 / pL5 / pL6
ggsave('balance_checks.png', balance_plots, width = 12, height = 36, limitsize = FALSE)

View(d2)

# ============================================================================
# Balance Checks
# ============================================================================

# Check predictability balance across lists
# Propagate 'corr' predictability to all conditions within each item
d2 <- d2 %>%
  group_by(Item) %>%
  mutate(Predictability = max(Predictability, na.rm = TRUE)) %>%
  ungroup()

anova_predictability <- aov(Predictability ~ List, data = d2)
summary(anova_predictability)

# Check familiarity balance across lists
d2 <- d2 %>%
  group_by(Item) %>%
  mutate(Familiarity = max(Familiarity, na.rm = TRUE)) %>%
  ungroup()

anova_familiarity <- aov(Familiarity ~ List, data = d2)
summary(anova_familiarity)

# ============================================================================
# Prepare Experimental Materials
# ============================================================================

# Add correct response column
d2$correct_response <- ifelse(d2$Condition == "corr", "vero", "falso")
View(d2)

# Create list dataframes with standardized column names
dl1 = subset(d2, List == 'L1', select = c(Item, Condition, Spelling, correct_response))
colnames(dl1) = c("item", "condition", "spelling", "correct_response")
View(dl1)

dl2 = subset(d2, List == 'L2', select = c(Item, Condition, Spelling, correct_response))
colnames(dl2) = c("item", "condition", "spelling", "correct_response")
View(dl2)

dl3 = subset(d2, List == 'L3', select = c(Item, Condition, Spelling, correct_response))
colnames(dl3) = c("item", "condition", "spelling", "correct_response")
View(dl3)

dl4 = subset(d2, List == 'L4', select = c(Item, Condition, Spelling, correct_response))
colnames(dl4) = c("item", "condition", "spelling", "correct_response")
View(dl4)

dl5 = subset(d2, List == 'L5', select = c(Item, Condition, Spelling, correct_response))
colnames(dl5) = c("item", "condition", "spelling", "correct_response")
View(dl5)

dl6 = subset(d2, List == 'L6', select = c(Item, Condition, Spelling, correct_response))
colnames(dl6) = c("item", "condition", "spelling", "correct_response")
View(dl6)

# Prepare filler items
filler <- read.csv("filler.csv", sep = ',')
filler_final <- data.frame(
  item = filler$item,
  condition = "filler",
  spelling = filler$spelling,
  correct_response = "vero"
)
View(filler_final)

# ============================================================================
# Save Experimental Files
# ============================================================================

write.csv(d2, "Final_data.csv", row.names = FALSE)
write.csv(dl1, "L1.csv", row.names = FALSE)
write.csv(dl2, "L2.csv", row.names = FALSE)
write.csv(dl3, "L3.csv", row.names = FALSE)
write.csv(dl4, "L4.csv", row.names = FALSE)
write.csv(dl5, "L5.csv", row.names = FALSE)
write.csv(dl6, "L6.csv", row.names = FALSE)
write.csv(filler_final, "Filler.csv", row.names = FALSE)

# ============================================================================
# Pseudo-randomization Function
# ============================================================================

# Randomize trial order with constraint on consecutive responses
# Maximum 4 consecutive identical responses allowed
randomize <- function(input_list, input_filler, max_consecutive = 4) {
  full_list <- rbind(input_list, input_filler)
  valida <- FALSE
  trial <- 0
  
  while (!valida) {
    trial <- trial + 1
    
    # Shuffle items
    shuffled_list <- full_list[sample(1:nrow(full_list)), ]
    
    # Check run length of consecutive responses
    check_resp <- rle(shuffled_list$correct_response)$lengths
    
    if (max(check_resp) <= max_consecutive) {
      valida <- TRUE
    }
    
    # Safety limit to prevent infinite loops
    if (trial > 10000) {
      warning("Maximum trial limit reached (10,000 attempts)")
      valida <- TRUE
    }
  }
  
  return(shuffled_list)
}

# ============================================================================
# Generate Randomized Lists
# ============================================================================

# Combine experimental items with fillers
L1.data <- rbind(dl1, filler_final)
L2.data <- rbind(dl2, filler_final)
L3.data <- rbind(dl3, filler_final)
L4.data <- rbind(dl4, filler_final)
L5.data <- rbind(dl5, filler_final)
L6.data <- rbind(dl6, filler_final)

View(L1.data)
View(L2.data)
View(L3.data)
View(L4.data)
View(L5.data)
View(L6.data)

# Generate two randomized versions (A and B) for each list
# List 1
cat(toJSON(randomize(dl1, filler_final), pretty = TRUE), file = 'L1A.json')
cat(toJSON(randomize(dl1, filler_final), pretty = TRUE), file = 'L1B.json')

# List 2
cat(toJSON(randomize(dl2, filler_final), pretty = TRUE), file = 'L2A.json')
cat(toJSON(randomize(dl2, filler_final), pretty = TRUE), file = 'L2B.json')

# List 3
cat(toJSON(randomize(dl3, filler_final), pretty = TRUE), file = 'L3A.json')
cat(toJSON(randomize(dl3, filler_final), pretty = TRUE), file = 'L3B.json')

# List 4
cat(toJSON(randomize(dl4, filler_final), pretty = TRUE), file = 'L4A.json')
cat(toJSON(randomize(dl4, filler_final), pretty = TRUE), file = 'L4B.json')

# List 5
cat(toJSON(randomize(dl5, filler_final), pretty = TRUE), file = 'L5A.json')
cat(toJSON(randomize(dl5, filler_final), pretty = TRUE), file = 'L5B.json')

# List 6
cat(toJSON(randomize(dl6, filler_final), pretty = TRUE), file = 'L6A.json')
cat(toJSON(randomize(dl6, filler_final), pretty = TRUE), file = 'L6B.json')

# ============================================================================
# Generate Combined Stimulus File
# ============================================================================

# Compile all lists into a single JSON file for experimental software
material = list()
material[['L1A']] = randomize(dl1, filler_final)
material[['L1B']] = randomize(dl1, filler_final)
material[['L2A']] = randomize(dl2, filler_final)
material[['L2B']] = randomize(dl2, filler_final)
material[['L3A']] = randomize(dl3, filler_final)
material[['L3B']] = randomize(dl3, filler_final)
material[['L4A']] = randomize(dl4, filler_final)
material[['L4B']] = randomize(dl4, filler_final)
material[['L5A']] = randomize(dl5, filler_final)
material[['L5B']] = randomize(dl5, filler_final)
material[['L6A']] = randomize(dl6, filler_final)
material[['L6B']] = randomize(dl6, filler_final)

cat(toJSON(material, pretty = TRUE), file = 'stimuli.json')