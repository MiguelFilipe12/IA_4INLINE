import ast
import csv
import re

# Colunas do CSV
header = [f"cell_{r}_{c}" for r in range(6) for c in range(7)] + ["action", "col"]

with open("dataset.txt", "r") as f_in, open("dataset.csv", "w", newline="") as f_out:
    writer = csv.DictWriter(f_out, fieldnames=header)
    writer.writeheader()

    skipped = 0
    written = 0

    for line in f_in:
        line = line.strip()
        if not line:
            continue

        match = re.match(r"^(\[.*\]);\s*(\(.*\))$", line)
        if not match:
            skipped += 1
            continue

        try:
            matrix       = ast.literal_eval(match.group(1))
            action, col  = ast.literal_eval(match.group(2))
        except Exception as e:
            skipped += 1
            continue

        row = {}
        for r in range(6):
            for c in range(7):
                row[f"cell_{r}_{c}"] = matrix[r][c]
        row["action"] = action
        row["col"]    = col

        writer.writerow(row)
        written += 1

print(f"Concluído: {written} linhas escritas, {skipped} ignoradas → dataset.csv")