import os
import urllib.request

import numpy as np
import pandas as pd
"""
Semantic distance calculation using Tencent Word2Vec embeddings.
Processes data_original.csv to compute corr vs sameT, diffT, and noP distances.
"""


# ============================================================================
# Configuration
# ============================================================================

REPO_ID = "shibing624/text2vec-word2vec-tencent-chinese"
MODEL_FILENAME = "light_Tencent_AILab_ChineseEmbedding.bin"
PROJECT_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", ".."))
RAW_DIR = os.path.join(PROJECT_DIR, "data", "raw")
INTERMEDIATE_DIR = os.path.join(PROJECT_DIR, "data", "intermediate")
SHARED_FILE = os.path.join(INTERMEDIATE_DIR, "data_measures.csv")
INPUT_FILE = SHARED_FILE if os.path.exists(SHARED_FILE) else os.path.join(
    RAW_DIR, "data_original.csv")
OUTPUT_FILE = SHARED_FILE


def format_csv_float(value):
    """Write floating-point values without scientific notation."""
    return f"{value:.15f}".rstrip("0").rstrip(".")

# ============================================================================
# Helper Functions
# ============================================================================


def download_model(repo_id, filename):
    """
    Download model from Hugging Face hub.

    Args:
        repo_id: Repository ID on Hugging Face
        filename: Model filename to download

    Returns:
        Local path to the downloaded model
    """
    local_path = os.path.join(RAW_DIR, filename)
    if os.path.exists(local_path):
        print(f"Model already exists locally: {local_path}")
        return local_path

    download_url = f"https://huggingface.co/{repo_id}/resolve/main/{filename}"
    print(f"Downloading {filename} from {download_url}...")
    urllib.request.urlretrieve(download_url, local_path)
    print(f"Model downloaded to: {local_path}")
    return local_path


def load_model(model_path):
    """
    Load the Word2Vec binary model and keep only requested vectors.

    Args:
        model_path: Path to the binary model file

    Returns:
        Dict mapping tokens to vectors
    """
    raise NotImplementedError(
        "load_model requires the token set; use load_model_for_tokens instead")


def load_model_for_tokens(model_path, tokens_needed):
    """
    Load only the token vectors needed for this analysis from a Word2Vec binary file.

    Args:
        model_path: Path to the binary model file
        tokens_needed: Iterable of tokens to extract

    Returns:
        Dict mapping token -> numpy vector
    """
    tokens_needed = set(tokens_needed)
    vectors = {}

    print(f"Loading vectors from {model_path}...")
    with open(model_path, "rb") as model_file:
        header = model_file.readline().decode("utf-8", errors="ignore").strip()
        parts = header.split()
        if len(parts) != 2:
            raise ValueError(f"Invalid word2vec header: {header!r}")

        vocab_size = int(parts[0])
        vector_size = int(parts[1])
        print(
            f"Model header: {vocab_size} tokens, {vector_size}-dimensional vectors")

        for _ in range(vocab_size):
            token_bytes = bytearray()
            while True:
                char = model_file.read(1)
                if not char:
                    break
                if char in b" \t\n\r":
                    if token_bytes:
                        break
                    continue
                token_bytes.extend(char)

            if not token_bytes:
                break

            token = token_bytes.decode("utf-8", errors="ignore")
            vector = np.frombuffer(model_file.read(
                4 * vector_size), dtype=np.float32)

            if token in tokens_needed:
                vectors[token] = vector.copy()
                if len(vectors) == len(tokens_needed):
                    break

    print(f"Loaded {len(vectors)} requested vectors.")
    return vectors


def safe_get_vector(model, token):
    """
    Safely get vector for a token, returning None if not found.

    Args:
        model: KeyedVectors model
        token: Token (character or word)

    Returns:
        Vector (numpy array) or None if token not in vocabulary
    """
    try:
        return model.get(token)
    except AttributeError:
        return None


def cosine_distance(v1, v2):
    """
    Calculate cosine distance between two vectors.
    Includes item even if only one vector is available.

    Args:

    Returns:
        Cosine distance (0-2, lower = more similar), NaN if both vectors unavailable
    """
    if v1 is None or v2 is None:
        return np.nan
    denominator = np.linalg.norm(v1) * np.linalg.norm(v2)
    if denominator == 0:
        return np.nan
    similarity = float(np.dot(v1, v2) / denominator)
    return float(1 - similarity)


def process_data_file(model_path, input_file, output_file):
    """
    Process CSV file and calculate semantic distances.

    For each item:
    - Calculate distance between corr and sameT, diffT, and noP (Last_char)

    Args:
        model_path: Path to the binary model file
        input_file: Path to input CSV file
        output_file: Path to save output CSV file
    """
    print(f"\nReading CSV file: {input_file}")
    df = pd.read_csv(input_file, sep=';', encoding='utf-8')

    tokens_needed = set(df.loc[df['Condition'].isin(
        ['corr', 'sameT', 'diffT', 'noP']), 'Last_char'].dropna().astype(str))
    sample_tokens = [token.encode('unicode_escape').decode(
        'ascii') for token in sorted(list(tokens_needed))[:10]]
    print(f"Need {len(tokens_needed)} unique vectors: {', '.join(sample_tokens)}")
    model = load_model_for_tokens(model_path, tokens_needed)

    distance_column = 'Sem_Distance'
    df[distance_column] = np.nan

    print(f"Processing {len(df['Item'].unique())} items...")

    not_found = set()

    # Process each item
    for item_num in sorted(df['Item'].unique()):
        item_df = df[df['Item'] == item_num]

        # Get the corr row and the three comparison rows.
        corr_rows = item_df[item_df['Condition'] == 'corr']

        if corr_rows.empty:
            continue

        corr_char = corr_rows['Last_char'].values[0]
        vec_corr = safe_get_vector(model, corr_char)

        if vec_corr is None:
            not_found.add(corr_char)

        for condition in ['sameT', 'diffT', 'noP']:
            condition_rows = item_df[item_df['Condition'] == condition]
            if condition_rows.empty:
                continue

            condition_char = condition_rows['Last_char'].values[0]
            vec_condition = safe_get_vector(model, condition_char)

            if vec_condition is None:
                not_found.add(condition_char)

            distance = cosine_distance(vec_corr, vec_condition)
            df.loc[condition_rows.index[0], distance_column] = distance

    # Save results
    print(f"\nSaving results to: {output_file}")
    df.to_csv(
        output_file,
        index=False,
        sep=';',
        encoding='utf-8-sig',
        na_rep='NA',
        float_format=format_csv_float,
    )
    print("Results saved successfully!")

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total items processed: {len(df['Item'].unique())}")
    print(f"Characters not found in vocabulary: {len(not_found)}")
    if not_found:
        missing_preview = [token.encode('unicode_escape').decode(
            'ascii') for token in sorted(not_found)[:20]]
        print(f"  Missing characters: {', '.join(missing_preview)}")

    valid_dists = df[distance_column].notna().sum()
    print(f"Valid semantic distances: {valid_dists}")

    if valid_dists > 0:
        print("\nSemantic distance statistics:")
        print(f"  Mean: {df[distance_column].mean():.4f}")
        print(f"  Min: {df[distance_column].min():.4f}")
        print(f"  Max: {df[distance_column].max():.4f}")
        print(f"  Std: {df[distance_column].std():.4f}")

    print(f"{'='*60}\n")

    return df

# ============================================================================
# Main
# ============================================================================


if __name__ == "__main__":
    try:
        # Step 1: Download model
        model_path = download_model(REPO_ID, MODEL_FILENAME)

        # Step 2: Process data file
        if os.path.exists(INPUT_FILE):
            results = process_data_file(model_path, INPUT_FILE, OUTPUT_FILE)
            print(f"Processing complete! Output file: {OUTPUT_FILE}")
        else:
            print(f"Error: {INPUT_FILE} not found in current directory")
            print(f"Current directory: {os.getcwd()}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
