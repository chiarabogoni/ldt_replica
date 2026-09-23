"""
Character frequency analysis using Jun Da Modern Chinese Corpus.
Calculates absolute frequency, percentage, and relative frequency for
characters in the dataset.
"""

import os
import pandas as pd

# ============================================================================
# Configuration
# ============================================================================

PROJECT_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", ".."))
RAW_DIR = os.path.join(PROJECT_DIR, "data", "raw")
INTERMEDIATE_DIR = os.path.join(PROJECT_DIR, "data", "intermediate")
SHARED_FILE = os.path.join(INTERMEDIATE_DIR, "data_measures.csv")

# Jun Da Modern Chinese Character Frequency data
FREQUENCY_FILE = os.path.join(RAW_DIR, "CharFreq-Modern.xls")
INPUT_FILE = SHARED_FILE if os.path.exists(SHARED_FILE) else os.path.join(
    RAW_DIR, "data_original.csv")
OUTPUT_FILE = SHARED_FILE
TOTAL_CORPUS_CHARACTERS = 193504018


def format_csv_float(value):
    """Write floating-point values without scientific notation."""
    return f"{value:.15f}".rstrip("0").rstrip(".")

# ============================================================================
# Load Frequency Data
# ============================================================================


print("=" * 80)
print("Character Frequency Analysis - Jun Da Modern Chinese Corpus")
print("=" * 80)

# Load the Jun Da frequency data
print(f"\nLoading frequency data from {FREQUENCY_FILE}...")
try:
    # The original file has header starting at row 6 (index 5)
    freq_df = pd.read_excel(FREQUENCY_FILE, header=5)
    print(f"✓ Loaded {len(freq_df)} character frequencies")
    print(f"Columns: {list(freq_df.columns)}")
except FileNotFoundError:
    print(f"ERROR: {FREQUENCY_FILE} not found!")
    print("\nPlease download Jun Da Modern Chinese Character Frequency data:")
    print("Source: http://lingua.mtsu.edu/chinese-computing/statistics/char/list.php?Which=MO")
    exit(1)

# Calculate total frequency for percentage calculations
total_freq = freq_df["频率"].sum()
print(f"Total corpus frequency: {total_freq:,}")

# ============================================================================
# Helper Functions
# ============================================================================


def get_char_stats(char_list, freq_data):
    """
    Get frequency statistics for a list of characters.

    Args:
        char_list: List of Chinese characters
        freq_data: DataFrame with frequency data

    Returns:
        DataFrame with character, frequency, percentage, and relative frequency
    """
    results = []

    for char in char_list:
        # Search for character in the corpus
        result = freq_data.loc[freq_data["汉字"] == char, "频率"]

        if not result.empty:
            freq = result.values[0]
            perc = freq / total_freq * 100
            relative_freq = freq / TOTAL_CORPUS_CHARACTERS
            results.append({
                "汉字": char,
                "频率": freq,
                "百分比": f"{perc:.6f}%",
                "Relative_Frequency": relative_freq,
            })
        else:
            # Character not found in corpus
            results.append({
                "汉字": char,
                "频率": None,
                "百分比": None,
                "Relative_Frequency": None,
            })

    return pd.DataFrame(results)

# ============================================================================
# Process Input Data
# ============================================================================


print(f"\nLoading character data from {INPUT_FILE}...")
try:
    # The dataset uses semicolons as delimiters
    input_df = pd.read_csv(INPUT_FILE, sep=';', encoding='utf-8')
    print(f"✓ Loaded {len(input_df)} rows")
except FileNotFoundError:
    print(f"ERROR: {INPUT_FILE} not found!")
    exit(1)

# Extract unique characters from Last_char column
if "Last_char" not in input_df.columns:
    print("ERROR: 'Last_char' column not found in input file!")
    exit(1)

chars = input_df["Last_char"].dropna().unique().tolist()
print(f"\nFound {len(chars)} unique characters to analyze")

# ============================================================================
# Calculate Frequencies
# ============================================================================

print("\nCalculating character frequencies...")
stats_df = get_char_stats(chars, freq_df)

# Count found vs not found
found = stats_df["频率"].notna().sum()
not_found = stats_df["频率"].isna().sum()

print(f"✓ Characters found in corpus: {found}")
print(f"✗ Characters not found: {not_found}")

# ============================================================================
# Display Results
# ============================================================================

print("\n" + "=" * 80)
print("FREQUENCY RESULTS")
print("=" * 80)

# Set display options to show all rows
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.unicode.east_asian_width", True)

print(stats_df.to_string(index=False))

# ============================================================================
# Merge with Original Data
# ============================================================================

print("\n" + "=" * 80)
print("MERGING WITH ORIGINAL DATA")
print("=" * 80)

# Create a frequency lookup dictionary
freq_lookup = dict(zip(stats_df["汉字"], stats_df["频率"]))
perc_lookup = dict(zip(stats_df["汉字"], stats_df["百分比"]))
relative_freq_lookup = dict(
    zip(stats_df["汉字"], stats_df["Relative_Frequency"])
)

# Add frequency columns to original dataframe
input_df["Frequency"] = input_df["Last_char"].map(freq_lookup)
input_df["Frequency_Percentage"] = input_df["Last_char"].map(perc_lookup)
input_df["Relative_Frequency"] = input_df["Last_char"].map(
    relative_freq_lookup
)

# ============================================================================
# Save Results
# ============================================================================

print("\nSaving results...")

# Save frequency statistics
stats_output = OUTPUT_FILE.replace('.csv', '_stats.csv')
stats_df.to_csv(
    stats_output,
    index=False,
    encoding='utf-8-sig',
    na_rep='NA',
    float_format=format_csv_float,
)
print(f"✓ Frequency statistics saved to: {stats_output}")

# Save merged data with frequencies
merged_output = OUTPUT_FILE
input_df.to_csv(
    merged_output,
    index=False,
    sep=';',
    encoding='utf-8-sig',
    na_rep='NA',
    float_format=format_csv_float,
)
print(f"✓ Data with frequencies saved to: {merged_output}")

# ============================================================================
# Summary Statistics
# ============================================================================

print("\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)

if found > 0:
    valid_freqs = stats_df["频率"].dropna()
    valid_percs = stats_df["百分比"].dropna()

    print(f"Characters analyzed: {len(chars)}")
    print(f"Found in corpus: {found} ({found/len(chars)*100:.1f}%)")
    print(f"Not found: {not_found} ({not_found/len(chars)*100:.1f}%)")
    print(f"\nFrequency range:")
    print(f"  Minimum: {valid_freqs.min():,.0f}")
    print(f"  Maximum: {valid_freqs.max():,.0f}")
    print(f"  Mean: {valid_freqs.mean():,.0f}")
    print(f"  Median: {valid_freqs.median():,.0f}")

    # Show most and least frequent characters
    sorted_stats = stats_df.dropna().sort_values("频率", ascending=False)

    print(f"\nMost frequent characters (top 5):")
    for _, row in sorted_stats.head(5).iterrows():
        print(f"  {row['汉字']}: {row['频率']:,.0f} ({row['百分比']})")

    print(f"\nLeast frequent characters (bottom 5):")
    for _, row in sorted_stats.tail(5).iterrows():
        print(f"  {row['汉字']}: {row['频率']:,.0f} ({row['百分比']})")

print("\n" + "=" * 80)
print("Analysis complete!")
print("=" * 80 + "\n")
