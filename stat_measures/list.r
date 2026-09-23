library(dplyr)
library(ggstatsplot)
library(jsonlite)
library(patchwork)
library(ggplot2)

d <- d1

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
View(d2)


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
# Prepare Experimental Materials
# ============================================================================

# Add correct response column
d2$correct_response <- ifelse(d2$Condition == "corr", "true", "false")
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
  correct_response = "true"
)
View(filler_final)

# ============================================================================
# Save Experimental Files
# ============================================================================

write.csv(d2, "data_with_lists.csv", row.names = FALSE)
write.csv(dl1, "L1.csv", row.names = FALSE)
write.csv(dl2, "L2.csv", row.names = FALSE)
write.csv(dl3, "L3.csv", row.names = FALSE)
write.csv(dl4, "L4.csv", row.names = FALSE)
write.csv(dl5, "L5.csv", row.names = FALSE)
write.csv(dl6, "L6.csv", row.names = FALSE)
write.csv(filler_final, "filler.csv", row.names = FALSE)

# ============================================================================
# Pseudo-randomization Function
# ============================================================================

# Randomize trial order with constraint on consecutive responses
# Maximum 4 consecutive identical responses allowed
randomize <- function(input_list, input_filler, max_consecutive = 4) {
  full_list <- rbind(input_list, input_filler)
  for (trial in seq_len(10000)) {
    # Shuffle items
    shuffled_list <- full_list[sample(1:nrow(full_list)), ]
    
    resp_vector <- as.character(shuffled_list$correct_response)
    
    # Check run length of consecutive responses
    check_resp <- rle(resp_vector)$lengths
    
    if (max(check_resp) <= max_consecutive) {
      return(shuffled_list)
    }
  }
  
  stop("Could not create a list with the requested response constraint")
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

# Generate each randomized version once. The same objects are used for both
# the standalone files and the combined stimulus file.
randomized_lists <- list(
  L1A_difft = randomize(dl1, filler_final),
  L1B_difft = randomize(dl1, filler_final),
  L2A_difft = randomize(dl2, filler_final),
  L2B_difft = randomize(dl2, filler_final),
  L3A_difft = randomize(dl3, filler_final),
  L3B_difft = randomize(dl3, filler_final),
  L1A_nop = randomize(dl4, filler_final),
  L1B_nop = randomize(dl4, filler_final),
  L2A_nop = randomize(dl5, filler_final),
  L2B_nop = randomize(dl5, filler_final),
  L3A_nop = randomize(dl6, filler_final),
  L3B_nop = randomize(dl6, filler_final)
)

for (list_name in names(randomized_lists)) {
  cat(
    toJSON(randomized_lists[[list_name]], pretty = TRUE),
    file = paste0(list_name, '.json')
  )
}

cat(toJSON(randomized_lists, pretty = TRUE), file = 'stimuli_ldt.json')