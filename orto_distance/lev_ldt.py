"""
Levenshtein distance calculation for Chinese character decomposition.
Uses IDS (Ideographic Description Sequences) to compute structural distances
between characters based on their radical decomposition.
"""

import re
from typing import List
from Levenshtein import distance
import pandas as pd

# ============================================================================
# Configuration
# ============================================================================

IDS_FILE = 'IDSdecomp.csv'
INPUT_FILE = 'new_data.csv'
OUTPUT_FILE = 'data_levenshtein.csv'

# ============================================================================
# IDS Tokenization
# ============================================================================

IDS_TOKEN_RE = re.compile(
    r"""
    &CDP-[0-9A-Fa-f]+;      |  # CDP entity reference
    [\u2FF0-\u2FFB]         |  # IDS operators
    .                          # any single Unicode code point
    """,
    re.VERBOSE
)


def tokenize_ids(s: str) -> List[str]:
    """
    Tokenize an IDS decomposition string into logical units suitable
    for Levenshtein distance over Sequence[Hashable].

    Args:
        s: IDS decomposition string

    Returns:
        List of tokens
    """
    return IDS_TOKEN_RE.findall(s)


# ============================================================================
# Helper Functions
# ============================================================================

def get_ids(char: str, ids_df: pd.DataFrame):
    """
    Get IDS decomposition for a character.

    Args:
        char: Chinese character
        ids_df: DataFrame with IDS data

    Returns:
        IDS decomposition string or None if not found
    """
    if not any(ids_df.item == char):
        return None
    return ids_df.decomposition[ids_df.item == char].to_string(header=False, index=False)


def get_rad(char: str, ids_df: pd.DataFrame):
    """
    Get radical for a character.

    Args:
        char: Chinese character
        ids_df: DataFrame with IDS data

    Returns:
        Radical string or None if not found
    """
    if not any(ids_df.item == char):
        return None
    return ids_df.radical[ids_df.item == char].to_string(header=False, index=False)


def dist(char1: str, char2: str, ids_df: pd.DataFrame, norm=True):
    """
    Calculate Levenshtein distance between two characters based on IDS decomposition.

    Args:
        char1: First character
        char2: Second character
        ids_df: DataFrame with IDS data
        norm: Whether to normalize distance

    Returns:
        Levenshtein distance (normalized if norm=True) or None if decomposition unavailable
    """
    id1 = get_ids(char1, ids_df)
    id2 = get_ids(char2, ids_df)

    if (id1 is None) or (id2 is None):
        return None

    s1 = tokenize_ids(id1)
    s2 = tokenize_ids(id2)

    # Calculate Levenshtein distance with custom weights (insert=1, delete=1, substitute=2)
    d = distance(s1, s2, weights=(1, 1, 2))

    if norm:
        n1 = len(s1)
        n2 = len(s2)
        # Maximum possible distance for normalization
        md = min(n1, n2) * 2 + abs(n2 - n1)
        d = d / md if md > 0 else 0

    return d


# ============================================================================
# Main Processing
# ============================================================================

print("=" * 80)
print("Levenshtein Distance Calculation for Character Decomposition")
print("=" * 80)

# Load IDS decomposition data
print(f"\nLoading IDS decomposition from {IDS_FILE}...")
try:
    ids = pd.read_csv(IDS_FILE)
    print(f"✓ Loaded {len(ids)} IDS entries")
except FileNotFoundError:
    print(f"ERROR: {IDS_FILE} not found!")
    print("Please ensure IDSdecomp.csv is in the same directory.")
    exit(1)

# Load character data
print(f"\nLoading character data from {INPUT_FILE}...")
try:
    ch = pd.read_csv(INPUT_FILE, sep=';')
    print(f"✓ Loaded {len(ch)} rows")
except FileNotFoundError:
    print(f"ERROR: {INPUT_FILE} not found!")
    exit(1)

# Add new column for Levenshtein distance
ch["Levenshtein_Distance"] = None

# Process each row
print(f"\nProcessing characters...")
ld = []
rowlist = []

for row in ch.itertuples(index=False):
    item = row.Item
    condition = row.Condition

    # Get the correct character for this item
    corr_mask = (ch['Item'] == row.Item) & (ch['Condition'] == 'corr')
    if not any(corr_mask):
        print(f"Warning: No 'corr' condition found for Item {item}")
        ld.append(None)
        continue

    corr = ch.Last_char[corr_mask].to_string(header=False, index=False)

    # Calculate distance
    d = dist(corr, row.Last_char, ids)

    # Store information
    info = {
        'Item': row.Item,
        'Condition': row.Condition,
        'RefChar': corr,
        'Char': row.Last_char,
        'Wang_Rad': get_rad(row.Last_char, ids),
        'Wang_IDS': get_ids(row.Last_char, ids),
        'Levenshtein_Distance': d
    }

    ld.append(d)
    rowlist.append(info)

    # Print progress
    dist_str = f"{d:.4f}" if d is not None else "N/A"
    print(
        f"  Item {item} [{condition}]: {corr} → {row.Last_char} = {dist_str}")

# Add distances to original dataframe
ch["Levenshtein_Distance"] = ld

# Save results
print(f"\n{'='*80}")
print("Saving results...")

# Save detailed measures
detailed_df = pd.DataFrame(rowlist)
detailed_df.to_csv(OUTPUT_FILE, index=False, na_rep='NA')
print(f"✓ Detailed results saved to: {OUTPUT_FILE}")

# Save updated original file
updated_file = INPUT_FILE.replace('.csv', '_with_levenshtein.csv')
ch.to_csv(updated_file, index=False, na_rep='NA')
print(f"✓ Updated data saved to: {updated_file}")

# Print summary statistics
print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")
valid_distances = [d for d in ld if d is not None]
if valid_distances:
    print(f"Total calculations: {len(ld)}")
    print(f"Valid distances: {len(valid_distances)}")
    print(f"Missing distances: {len(ld) - len(valid_distances)}")
    print(f"\nDistance statistics:")
    print(f"  Mean: {sum(valid_distances)/len(valid_distances):.4f}")
    print(f"  Min: {min(valid_distances):.4f}")
    print(f"  Max: {max(valid_distances):.4f}")
else:
    print("No valid distances calculated!")

print(f"{'='*80}\n")
