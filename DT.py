import ast
import math
import json
from collections import Counter
 
ROWS = 6
COLS = 7

# 1. PARSE DATASET
# ─────────────────────────────────────────────────────────────
 
def parse_dataset(filepath):
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split('; ')
            if len(parts) != 2:
                continue
            try:
                board = ast.literal_eval(parts[0])
                move = ast.literal_eval(parts[1])
                data.append((board, move))
            except Exception:
                continue
    return data
 
 
# ─────────────────────────────────────────────────────────────
# 2. FEATURE EXTRACTION
# ─────────────────────────────────────────────────────────────
 
def check_four(board, player):
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c+i] == player for i in range(4)):
                return True
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r+i][c] == player for i in range(4)):
                return True
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r+i][c+i] == player for i in range(4)):
                return True
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r-i][c+i] == player for i in range(4)):
                return True
    return False
 
def winning_drop_col(board, player):
    """Return first winning drop column or -1."""
    for c in range(COLS):
        if board[0][c] != 0:
            continue
        for r in range(ROWS-1, -1, -1):
            if board[r][c] == 0:
                board[r][c] = player
                win = check_four(board, player)
                board[r][c] = 0
                if win:
                    return c
                break
    return -1
 
def threat_count(board, player):
    """Count windows of 4 with 3 of player and 1 empty."""
    count = 0
    opp = 3 - player
    def gen_windows():
        for r in range(ROWS):
            for c in range(COLS-3):
                yield [board[r][c+i] for i in range(4)]
        for c in range(COLS):
            for r in range(ROWS-3):
                yield [board[r+i][c] for i in range(4)]
        for r in range(ROWS-3):
            for c in range(COLS-3):
                yield [board[r+i][c+i] for i in range(4)]
        for r in range(3, ROWS):
            for c in range(COLS-3):
                yield [board[r-i][c+i] for i in range(4)]
    for w in gen_windows():
        if w.count(player) == 3 and w.count(opp) == 0:
            count += 1
    return count
 
def count_pairs(board, player):
    """Count unblocked pairs (2-in-a-row) in windows of 4."""
    count = 0
    opp = 3 - player
    def gen_windows():
        for r in range(ROWS):
            for c in range(COLS-3):
                yield [board[r][c+i] for i in range(4)]
        for c in range(COLS):
            for r in range(ROWS-3):
                yield [board[r+i][c] for i in range(4)]
        for r in range(ROWS-3):
            for c in range(COLS-3):
                yield [board[r+i][c+i] for i in range(4)]
        for r in range(3, ROWS):
            for c in range(COLS-3):
                yield [board[r-i][c+i] for i in range(4)]
    for w in gen_windows():
        if w.count(player) == 2 and w.count(opp) == 0:
            count += 1
    return count
 
def col_height(board, col):
    return sum(1 for r in range(ROWS) if board[r][col] != 0)
 
def infer_player(board):
    ones = sum(board[r][c] == 1 for r in range(ROWS) for c in range(COLS))
    twos = sum(board[r][c] == 2 for r in range(ROWS) for c in range(COLS))
    return 1 if ones <= twos else 2
 
def bin3(x):
    if x == 0: return "0"
    if x <= 2: return "1-2"
    return "3+"
 
def extract_features(board):
    player = infer_player(board)
    opp = 3 - player
 
    win_col = winning_drop_col(board, player)
    block_col = winning_drop_col(board, opp)  # col where opp would win
 
    heights = [col_height(board, c) for c in range(COLS)]
    total = sum(heights)
    emptiest = heights.index(min(heights))
 
    my_center = sum(1 for r in range(ROWS) if board[r][3] == player)
    opp_center = sum(1 for r in range(ROWS) if board[r][3] == opp)
    bottom_mine = sum(1 for c in range(COLS) if board[ROWS-1][c] == player)
    bottom_opp = sum(1 for c in range(COLS) if board[ROWS-1][c] == opp)
 
    my_threats = threat_count(board, player)
    opp_threats = threat_count(board, opp)
    my_pairs = count_pairs(board, player)
 
    # Encode phase
    if total <= 6:
        phase = "early"
    elif total <= 20:
        phase = "mid"
    else:
        phase = "late"
 
    # Which half is more occupied for player?
    left_mine = sum(board[r][c] == player for r in range(ROWS) for c in range(3))
    right_mine = sum(board[r][c] == player for r in range(ROWS) for c in range(4, 7))
    side_bias = "left" if left_mine > right_mine else ("right" if right_mine > left_mine else "center")
 
    return {
        "can_win": "yes" if win_col >= 0 else "no",
        "win_col": str(win_col),
        "must_block": "yes" if block_col >= 0 else "no",
        "block_col": str(block_col),
        "my_threats": bin3(my_threats),
        "opp_threats": bin3(opp_threats),
        "my_center": bin3(my_center),
        "opp_center": bin3(opp_center),
        "my_pairs": bin3(my_pairs),
        "phase": phase,
        "emptiest_col": str(emptiest),
        "can_pop": "yes" if bottom_mine > 0 else "no",
        "bottom_mine": bin3(bottom_mine),
        "bottom_opp": bin3(bottom_opp),
        "side_bias": side_bias,
    }
 
 
# ─────────────────────────────────────────────────────────────
# 3. ID3
# ─────────────────────────────────────────────────────────────
 
def entropy(labels):
    n = len(labels)
    if n == 0:
        return 0.0
    counts = Counter(labels)
    return -sum((c/n) * math.log2(c/n) for c in counts.values() if c > 0)
 
def information_gain(data, feature, labels):
    total_entropy = entropy(labels)
    n = len(data)
    values = set(d[feature] for d in data)
    weighted = 0.0
    for v in values:
        sub = [labels[i] for i, d in enumerate(data) if d[feature] == v]
        weighted += (len(sub) / n) * entropy(sub)
    return total_entropy - weighted
 
def id3(data, labels, features, depth=0, max_depth=15, min_samples=3):
    if not labels:
        return {"leaf": True, "label": "unknown", "support": 0}
 
    label_counts = Counter(labels)
    majority = label_counts.most_common(1)[0][0]
 
    if len(label_counts) == 1:
        return {"leaf": True, "label": labels[0], "support": len(labels)}
 
    if not features or depth >= max_depth or len(data) < min_samples:
        return {"leaf": True, "label": majority, "support": len(labels)}
 
    gains = {f: information_gain(data, f, labels) for f in features}
    best_feat = max(gains, key=gains.get)
 
    if gains[best_feat] <= 0:
        return {"leaf": True, "label": majority, "support": len(labels)}
 
    values = set(d[best_feat] for d in data)
    branches = {}
    remaining = [f for f in features if f != best_feat]
 
    for v in values:
        idx = [i for i, d in enumerate(data) if d[best_feat] == v]
        sub_data = [data[i] for i in idx]
        sub_labels = [labels[i] for i in idx]
        branches[v] = id3(sub_data, sub_labels, remaining, depth+1, max_depth, min_samples)
 
    return {
        "feature": best_feat,
        "branches": branches,
        "default": majority,
        "support": len(labels),
        "gain": round(gains[best_feat], 4)
    }
 
def predict(tree, feats):
    if tree.get("leaf"):
        return tree["label"]
    val = feats.get(tree["feature"])
    if val in tree["branches"]:
        return predict(tree["branches"][val], feats)
    return tree["default"]
 
def tree_depth(tree):
    if tree.get("leaf"):
        return 0
    return 1 + max(tree_depth(b) for b in tree["branches"].values())
 
def tree_size(tree):
    if tree.get("leaf"):
        return 1
    return 1 + sum(tree_size(b) for b in tree["branches"].values())
 
 
# ─────────────────────────────────────────────────────────────
# 4. EVALUATION
# ─────────────────────────────────────────────────────────────
 
def train_test_split(data, test_ratio=0.2, seed=42):
    import random
    random.seed(seed)
    d = data[:]
    random.shuffle(d)
    split = int(len(d) * (1 - test_ratio))
    return d[:split], d[split:]
 
def accuracy(tree, data, labels):
    correct = sum(predict(tree, d) == l for d, l in zip(data, labels))
    return correct / len(labels)
 
def per_class_accuracy(tree, data, labels):
    from collections import defaultdict
    correct = defaultdict(int)
    total = defaultdict(int)
    for d, l in zip(data, labels):
        total[l] += 1
        if predict(tree, d) == l:
            correct[l] += 1
    return {k: correct[k]/total[k] for k in total}
 
 
# ─────────────────────────────────────────────────────────────
# 5. VISUALISATION
# ─────────────────────────────────────────────────────────────
 
def print_tree(tree, indent=0, branch_val=None, max_depth=4):
    prefix = "    " * indent
    if branch_val is not None:
        line_start = f"{prefix}[{branch_val}] → "
    else:
        line_start = prefix
 
    if tree.get("leaf"):
        print(f"{line_start}MOVE: {tree['label']}  (n={tree['support']})")
        return
 
    feat = tree["feature"]
    gain = tree.get("gain", "?")
    print(f"{line_start}Split on '{feat}'  (gain={gain}, n={tree.get('support','?')})")
 
    if indent >= max_depth:
        print(f"{prefix}    ...")
        return
 
    for val, subtree in sorted(tree["branches"].items()):
        print_tree(subtree, indent + 1, val, max_depth)
 
 
# ─────────────────────────────────────────────────────────────
# 6. MAIN
# ─────────────────────────────────────────────────────────────
 
def main():
    print("=" * 65)
    print("  Decision Tree (ID3) for PopOut  —  MCTS dataset")
    print("=" * 65)
 
    print("\n[1] Loading dataset...")
    raw = parse_dataset(r"C:\Users\Colégio do Ave\Documents\Universidade\Inteligência Artificial\Trabalho1_PopOut\recente\dataset.txt")
    print(f"    Loaded {len(raw)} samples")
 
    print("\n[2] Extracting features...")
    feat_dicts = []
    labels = []
    for board, move in raw:
        feat_dicts.append(extract_features(board))
        labels.append(f"{move[0]}_{move[1]}")
 
    dist = Counter(labels)
    print(f"    Unique moves: {len(dist)}")
    print(f"    Top 10: {dist.most_common(10)}")
 
    combined = list(zip(feat_dicts, labels))
    train, test = train_test_split(combined, test_ratio=0.2)
    train_data, train_labels = zip(*train)
    test_data, test_labels = zip(*test)
    print(f"\n[3] Train: {len(train_labels)} | Test: {len(test_labels)}")
 
    features = list(train_data[0].keys())
    print(f"\n[4] Features used: {features}")
 
    print("\n[5] Training ID3 tree (max_depth=12)...")
    tree = id3(list(train_data), list(train_labels), features,
               max_depth=12, min_samples=2)
 
    train_acc = accuracy(tree, list(train_data), list(train_labels))
    test_acc = accuracy(tree, list(test_data), list(test_labels))
 
    print(f"\n[6] Results:")
    print(f"    Train accuracy : {train_acc*100:.1f}%")
    print(f"    Test  accuracy : {test_acc*100:.1f}%")
    print(f"    Tree depth     : {tree_depth(tree)}")
    print(f"    Tree nodes     : {tree_size(tree)}")
 
    print("\n[7] Tree (top 4 levels):")
    print_tree(tree, max_depth=4)
 
    # Save
    with open("decision_tree.json", "w") as f:
        json.dump(tree, f, indent=2)
    print("\n[8] Tree saved → decision_tree.json")
 
    # Per-class accuracy (top 5 classes)
    print("\n[9] Per-class test accuracy (top 5 most common moves):")
    pca = per_class_accuracy(tree, list(test_data), list(test_labels))
    top5 = [m for m, _ in dist.most_common(5)]
    test_dist = Counter(test_labels)
    for m in top5:
        n = test_dist[m]
        a = pca.get(m, 0)
        print(f"    {m:12s}  acc={a*100:.0f}%  (n={n})")
 
    return tree
 
 
if __name__ == "__main__":
    main()
 