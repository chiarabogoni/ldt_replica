"""
Visual distance analysis with stroke path visualization for Chinese characters.
Creates plots showing stroke overlays and calculates average distances between characters.
"""
import os
import urllib.parse
import urllib.request
import json
import math
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================================
# Configuration
# ============================================================================

INPUT_FILE = 'new_data.csv'
OUTPUT_FILE = 'new_data_visual_analysis.csv'

# ============================================================================
# Helper Functions
# ============================================================================

def get_points(char):
    """Fetch stroke points for a character from HanziWriter CDN."""
    encoded = urllib.parse.quote(char)
    url = f"https://cdn.jsdelivr.net/npm/hanzi-writer-data@2.0/{encoded}.json"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            medians = data.get("medians", [])
            points = []
            for stroke in medians:
                points.extend(stroke)
            return points
    except:
        return None


def get_medians(char):
    """Fetch stroke median paths for a character."""
    encoded = urllib.parse.quote(char)
    url = f"https://cdn.jsdelivr.net/npm/hanzi-writer-data@2.0/{encoded}.json"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return data.get("medians", [])
    except:
        return None


def avg_distance(points1, points2):
    """Calculate average minimum distance between two sets of points."""
    if not points1 or not points2:
        return None
    dists = []
    for p1 in points1:
        min_d = min(math.dist(p1, p2) for p2 in points2)
        dists.append(min_d)
    for p2 in points2:
        min_d = min(math.dist(p2, p1) for p1 in points1)
        dists.append(min_d)
    return sum(dists) / len(dists)


def medians_to_svg_path(medians):
    """Convert median stroke data to SVG path format."""
    path = ""
    for stroke in medians:
        if stroke:
            path += f"M {stroke[0][0]} {stroke[0][1]} "
            for point in stroke[1:]:
                path += f"L {point[0]} {point[1]} "
    return path


# ============================================================================
# Main Processing
# ============================================================================

print("=" * 80)
print("Visual Distance Analysis with Stroke Visualization")
print("=" * 80)

# Load data from CSV
if not os.path.exists(INPUT_FILE):
    print(f"ERROR: Could not find {INPUT_FILE}")
    exit(1)

df = pd.read_csv(INPUT_FILE)
print(f"Loaded {len(df)} rows from {INPUT_FILE}")

# Group by Item
groups = {}
for _, row in df.iterrows():
    item = str(row['Item'])
    condition = row['Condition']
    last_char = row['Last_char']
    if item not in groups:
        groups[item] = {}
    groups[item][condition] = last_char

print(f"Processing {len(groups)} items...\n")

# Select all items to visualize
selected_items = list(groups.keys())

# Results storage
results = []

for item in selected_items:
    if item in groups and 'corr' in groups[item] and 'diffT' in groups[item] and 'sameT' in groups[item]:
        corr_char = groups[item]['corr']
        diff_char = groups[item]['diffT']
        same_char = groups[item]['sameT']
        
        print(f"\n{'='*60}")
        print(f"Processing Item {item}")
        print(f"{'='*60}")
        print(f"Corr: {corr_char}, DiffT: {diff_char}, SameT: {same_char}")
        
        corr_medians = get_medians(corr_char)
        diff_medians = get_medians(diff_char)
        same_medians = get_medians(same_char)
        
        # Include item even if some medians are missing
        if corr_medians or diff_medians or same_medians:
            corr_points = [p for stroke in (corr_medians or []) for p in stroke]
            diff_points = [p for stroke in (diff_medians or []) for p in stroke]
            same_points = [p for stroke in (same_medians or []) for p in stroke]
            
            dist_corr_diff = avg_distance(corr_points, diff_points)
            dist_corr_same = avg_distance(corr_points, same_points)
            
            # Store results
            results.append({
                'Item': item,
                'Corr_Char': corr_char,
                'DiffT_Char': diff_char,
                'SameT_Char': same_char,
                'Dist_Corr_DiffT': dist_corr_diff,
                'Dist_Corr_SameT': dist_corr_same
            })
            
            # Print SVG paths
            print(f"\nSVG Paths:")
            if corr_medians:
                print(f"  Corr {corr_char}: {medians_to_svg_path(corr_medians)}")
            else:
                print(f"  Corr {corr_char}: NOT FOUND")
            if diff_medians:
                print(f"  DiffT {diff_char}: {medians_to_svg_path(diff_medians)}")
            else:
                print(f"  DiffT {diff_char}: NOT FOUND")
            if same_medians:
                print(f"  SameT {same_char}: {medians_to_svg_path(same_medians)}")
            else:
                print(f"  SameT {same_char}: NOT FOUND")
            
            # Print distances
            if dist_corr_diff is not None or dist_corr_same is not None:
                dist_diff_str = f"{dist_corr_diff:.2f}" if dist_corr_diff is not None else "N/A"
                dist_same_str = f"{dist_corr_same:.2f}" if dist_corr_same is not None else "N/A"
                print(f"\nDistances:")
                print(f"  Corr-DiffT: {dist_diff_str}")
                print(f"  Corr-SameT: {dist_same_str}")
            else:
                print(f"\nDistances: Could not calculate (missing data)")
            
            # Print segment distances
            print(f"\nSegment distances:")
            if corr_medians:
                for i, stroke in enumerate(corr_medians):
                    if len(stroke) > 1:
                        dists = [math.dist(stroke[j], stroke[j+1]) for j in range(len(stroke)-1)]
                        print(f"  Corr {corr_char} stroke {i+1}: {dists}")
            if diff_medians:
                for i, stroke in enumerate(diff_medians):
                    if len(stroke) > 1:
                        dists = [math.dist(stroke[j], stroke[j+1]) for j in range(len(stroke)-1)]
                        print(f"  DiffT {diff_char} stroke {i+1}: {dists}")
            if same_medians:
                for i, stroke in enumerate(same_medians):
                    if len(stroke) > 1:
                        dists = [math.dist(stroke[j], stroke[j+1]) for j in range(len(stroke)-1)]
                        print(f"  SameT {same_char} stroke {i+1}: {dists}")
            
            # Create visualization
            if corr_medians or diff_medians or same_medians:
                plt.figure(figsize=(8, 6))
                
                # Plot corr strokes
                if corr_medians:
                    for stroke in corr_medians:
                        if stroke:
                            x, y = zip(*stroke)
                            plt.plot(x, y, color='blue', linewidth=2)
                            plt.scatter(x, y, color='blue', s=20)
                plt.scatter([], [], color='blue', label=f'Corr: {corr_char}')
                
                # Plot diffT strokes
                if diff_medians:
                    for stroke in diff_medians:
                        if stroke:
                            x, y = zip(*stroke)
                            plt.plot(x, y, color='red', linewidth=2)
                            plt.scatter(x, y, color='red', s=20)
                plt.scatter([], [], color='red', label=f'DiffT: {diff_char}')
                
                # Plot sameT strokes
                if same_medians:
                    for stroke in same_medians:
                        if stroke:
                            x, y = zip(*stroke)
                            plt.plot(x, y, color='green', linewidth=2)
                            plt.scatter(x, y, color='green', s=20)
                plt.scatter([], [], color='green', label=f'SameT: {same_char}')
                
                # Draw lines between closest points (diffT to corr)
                if diff_points and corr_points:
                    for p1 in diff_points:
                        closest = min(corr_points, key=lambda p2: math.dist(p1, p2))
                        plt.plot([p1[0], closest[0]], [p1[1], closest[1]], 
                                'purple', linewidth=0.5, alpha=0.3)
                
                # Draw lines between closest points (sameT to corr)
                if same_points and corr_points:
                    for p1 in same_points:
                        closest = min(corr_points, key=lambda p2: math.dist(p1, p2))
                        plt.plot([p1[0], closest[0]], [p1[1], closest[1]], 
                                'orange', linewidth=0.5, alpha=0.3)
                
                title = f'Item {item}: Stroke Paths'
                if dist_corr_diff is not None or dist_corr_same is not None:
                    dist_diff_str = f"{dist_corr_diff:.2f}" if dist_corr_diff is not None else "N/A"
                    dist_same_str = f"{dist_corr_same:.2f}" if dist_corr_same is not None else "N/A"
                    title += f'\nDist Corr-DiffT: {dist_diff_str}, Corr-SameT: {dist_same_str}'
                
                plt.title(title)
                plt.legend()
                plt.axis('equal')
                plt.gca().invert_yaxis()  # Invert Y axis to match character orientation
                plt.tight_layout()
                plt.show()

# Save results to CSV
if results:
    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    print(f"\n{'='*80}")
    print(f"Results saved to: {OUTPUT_FILE}")
    print(f"Total items processed: {len(results)}")
    print(f"{'='*80}")
