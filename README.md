# Repository for material and software for a lexical decision experiment on chéngyǔ (成语)

Repository of materials and code for a lexical decision task (LDT) on Chinese idioms (成语 / chéngyǔ).  
The repository includes (i) stimulus measurement and statistical evaluation scripts, (ii) analysis utilities, and (iii) the experimental task implemented in HTML/JavaScript.

## License
[![CC BY 4.0](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)

This project is licensed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license. See the `LICENSE` file and the full license at https://creativecommons.org/licenses/by/4.0/.


## Layout

- `experiment/`: consent page, task page, styles, images, and the combined stimulus file.
- `data/raw/`: original datasets and external resources.
- `data/intermediate/`: datasets updated during analysis. `data_measures_stats.csv` contains only the frequency statistics.
- `data/final/`: finalized list files and randomized list JSON files.
- `analysis/`: frequency, orthographic, semantic, and statistical scripts.
- `outputs/`: plots, tables, and execution logs.
- `docs/`: participant instructions (in Italian and in Chinese).

## Python analyses

Run scripts from the project root, for example:

```powershell
python analysis/frequency/freq_ldt.py
python analysis/orthographic_distance/lev_ldt.py
python analysis/semantic_distance/sem_ldt.py
```

The scripts resolve their input and output paths from their own location, so the current working directory does not affect the data paths.

## Documentation

### Data-processing pipeline

- `freq_ldt.py` creates or updates `data/intermediate/data_measures.csv` with character-frequency data.
- `sem_ldt.py` reads the existing `data_measures.csv` and adds `Sem_Distance`.
- `lev_ldt.py` reads the existing `data_measures.csv` and adds `Levenshtein_Distance`.
- Existing columns are preserved when each script runs.
- All scripts use semicolon-separated CSV files.
- Chinese characters are saved with UTF-8 encoding.
- Missing values are written as `NA`.
- Frequency and distance values are written as ordinary decimal numbers rather than scientific notation, so they remain readable in the exported CSV files.


It is recommended to run the scripts in this order:

1. `freq_ldt.py`
2. `sem_ldt.py`
3. `lev_ldt.py`

### Variable definitions and levels

The main experimental variable is `Condition` (which explains the degree of phonological overlap of the last word with the target word), with four levels:

| Variable | Levels | Description |
| --- | --- | --- |
| `Condition` | `corr` | Correct idiom |
| `Condition` | `sameT` | Incorrect idiom, the last word is a full homophone of the target word |
| `Condition` | `diffT` | Incorrect idiom, the last word shares only the segmental phonology of the target word, but not the tone|
| `Condition` | `noP` | Incorrect idiom, the last word does not share phonology with the target word |


### Design

Between-subjects design: Groups `G1`-`G3` use the conditions `corr`, `sameT`, and `diffT`; groups `G4`-`G6` use the conditions `corr`, `sameT`, and `noP`. Random assignment balances the materials across six groups and generates lists `L1`-`L6`, including their CSV and JSON files.

The list rotations are:

| List | Conditions |
| --- | --- |
| `L1` | `corr`, `diffT`, `sameT` |
| `L2` | `diffT`, `sameT`, `corr` |
| `L3` | `sameT`, `corr`, `diffT` |
| `L4` | `corr`, `noP`, `sameT` |
| `L5` | `noP`, `sameT`, `corr` |
| `L6` | `sameT`, `corr`, `noP` |

Each list receives one row from all six item groups, giving 54 experimental items per list, with the addition of 18 correct fillers to balance the true/false condition. Each list contains a total of 72 items (36 wrong idioms, 36 correct idioms). Each list has two versions, A and B, which contain the same stimuli, in two pseudo-randomized order. We set a pseudo-randomization with constraints (no more than 4 items in a row with the same response). The randomized combined stimulus file is written to `experiment/stimuli_ldt.json`.


## Analysis

### Familiarity, compositionality and predictability

All the idioms were selected from a list elaborated by Zheng (2019), who reported descriptive norms for 182 guànyòngyǔ (惯用语) and 243 chéngyǔ (成語). All idioms in Zheng’s list were extracted from the Contemporary Chinese dictionary (6th edition, 2015), and were therefore selected from the top frequency band of the Google 1-gram database (Zheng, 2019).

Zheng (2019) normed the chengyu on the basis of data from 2,748 native speakers recruited from four Chinese universities in Beijing, for six dimensions: (i) familiarity; (ii) meaningfulness; (iii) literality; (iv) compositionality; (v) final-word predictability; and (vi) linguistic register. These dimensions were chosen on the basis of previous research on idioms.

We selected three of these measures:

- Familiarity indicates the probability of encountering a certain idiom in daily conversation (0 = improbable, 5 = very probable).
- Compositionality indicates the degree to which the literal meaning of the individual words contributes to the idiomatic meaning (0 = lowest, 5 = highest).
- Predictability indicates the likelihood of completing the idiom with the correct final word in a cloze task (0 = incorrect, 1 = correct).

### Frequency

Frequency was calculated using the Jun Da Corpus (2004). It includes both Classical and Modern Chinese, as well as various genres of written text. The Modern Chinese corpus contains a total of 193,504,018 characters.

For each character, it computes:

- Raw frequency
- Frequency percentage
- Relative frequency, calculated as `character frequency / 193,504,018` and log-transformed in `pre.R` for the t-tests.

### Semantic distance

For every item, the script calculates three comparisons:

- `corr` vs `sameT`
- `corr` vs `diffT`
- `corr` vs `noP`

The cosine distance is calculated as:

```text
1 - cosine similarity
```

The `corr` rows remain blank in `Sem_Distance`; the three calculated values are stored on the corresponding comparison rows. Identical vectors have distance `0`, while more different vectors have larger distances. The script returns `NA` when a vector is missing or has zero length.

### Orthographic distance

For every item, the character in the `corr` row is used as the reference character. The script calculates a normalized IDS-based Levenshtein distance between the reference character and the final character in each row:

- `corr` vs `corr` (distance `0`)
- `corr` vs `sameT`
- `corr` vs `diffT`
- `corr` vs `noP`

The distance is based on Ideographic Description Sequences (IDS), tokenization, and weighted Levenshtein distance (Wang and Keuleers, 2024). 0 indicates that the characters are equal, 1 indicates that the characters are completely different.

## Statistics

- `pre.R` contains the t-tests used to assess whether the experimental conditions are balanced across the measured properties.
- `analysis/statistics/list.r` creates the pseudo-randomized lists and balances the item distribution across lists.

## References

### Idioms

Zheng, H. (2019). *The processing of two types of Chinese idioms by L1 and L2 speakers*. Unpublished PhD thesis, University of Illinois.

### Character frequency

Jun Da. (2004). *Chinese character frequency list: Modern Chinese corpus*. Chinese Computing, Middle Tennessee State University. http://lingua.mtsu.edu/chinese-computing/statistics/char/list.php?Which=MO

### Semantic distance

Tencent AI Lab. (2026). *Tencent Chinese word vectors* [Pre-trained Word2Vec model]. Hugging Face. https://huggingface.co/shibing624/text2vec-word2vec-tencent-chinese

### Orthographic distance

Wang, Y., & Keuleers, E. (2024). Simplified Chinese character distance based on ideographic description sequences. In *Proceedings of the Second Workshop on Computation and Written Language (CAWL) @ LREC-COLING 2024* (pp. 59–66). Torino, Italy: ELRA and ICCL.

The IDS decompositions and radical information used by `lev_ldt.py` are stored in `data/raw/IDSdecomp.csv`.
