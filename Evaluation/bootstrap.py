import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.preprocessing import MultiLabelBinarizer

# 1. Read the CSV file
filename = 'qwen3.8-max_test'
df = pd.read_csv(filename + '.csv')

# 2. Preprocess comma-separated text into lists of labels
y_true_lists = df['result'].apply(lambda x: [s.strip() for s in str(x).split(',')])
y_pred_lists = df['model'].apply(lambda x: [s.strip() for s in str(x).split(',')])

# 3. Binarize labels into a multilabel indicator matrix
mlb = MultiLabelBinarizer()
y_true = mlb.fit_transform(y_true_lists)
y_pred = mlb.transform(y_pred_lists)

# 4. Calculate row-wise (per-sample) metrics for the dataframe export
row_precisions = []
row_recalls = []
row_f1s = []

for i in range(len(y_true)):
    p = precision_score(y_true[i:i+1], y_pred[i:i+1], average="samples", zero_division=0)
    r = recall_score(y_true[i:i+1], y_pred[i:i+1], average="samples", zero_division=0)
    f = f1_score(y_true[i:i+1], y_pred[i:i+1], average="samples", zero_division=0)
    row_precisions.append(p)
    row_recalls.append(r)
    row_f1s.append(f)

df['precision'] = row_precisions
df['recall'] = row_recalls
df['f1-score'] = row_f1s

# Keep only the requested columns
df_export = df[['รหัสรายงาน', 'result', 'model', 'precision', 'recall', 'f1-score']].copy()

# 5. Calculate overall sample-average dataset metrics
overall_p = precision_score(y_true, y_pred, average="samples", zero_division=0)
overall_r = recall_score(y_true, y_pred, average="samples", zero_division=0)
overall_f = f1_score(y_true, y_pred, average="samples", zero_division=0)

# 6. Perform Bootstrapping to get 95% Confidence Intervals
n_bootstrap = 1000
n_samples = len(y_true)
bootstrap_f1 = []
bootstrap_p = []
bootstrap_r = []

np.random.seed(42) # Set seed for reproducibility
for _ in range(n_bootstrap):
    idx = np.random.choice(n_samples, size=n_samples, replace=True)
    
    bootstrap_f1.append(f1_score(y_true[idx], y_pred[idx], average="samples", zero_division=0))
    bootstrap_p.append(precision_score(y_true[idx], y_pred[idx], average="samples", zero_division=0))
    bootstrap_r.append(recall_score(y_true[idx], y_pred[idx], average="samples", zero_division=0))

bootstrap_f1 = np.array(bootstrap_f1)
bootstrap_p = np.array(bootstrap_p)
bootstrap_r = np.array(bootstrap_r)

# Percentile Confidence Intervals (95%)
f1_low, f1_high = np.percentile(bootstrap_f1, [2.5, 97.5])
p_low, p_high = np.percentile(bootstrap_p, [2.5, 97.5])
r_low, r_high = np.percentile(bootstrap_r, [2.5, 97.5])

# Print stats to console
print(f"Observed Sample-average F1: {overall_f:.4f}")
print(f"95% Bootstrap CI: [{f1_low:.4f}, {f1_high:.4f}]\n")

# 7. Format summary rows to include at the bottom of the CSV
summary_row = {
    'รหัสรายงาน': 'Overall (Observed)',
    'result': '',
    'model': '',
    'precision': overall_p,
    'recall': overall_r,
    'f1-score': overall_f
}

ci_row = {
    'รหัสรายงาน': '95% Bootstrap CI',
    'result': '',
    'model': '',
    'precision': f"[{p_low:.4f}, {p_high:.4f}]",
    'recall': f"[{r_low:.4f}, {r_high:.4f}]",
    'f1-score': f"[{f1_low:.4f}, {f1_high:.4f}]"
}

# Append summary rows to export dataframe
df_export = pd.concat([df_export, pd.DataFrame([summary_row, ci_row])], ignore_index=True)

# 8. Export to timestamped CSV file
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'Evaluate_{filename}_{timestamp}.csv'
df_export.to_csv(filename, index=False, encoding='utf-8-sig')

print(f"Successfully exported evaluation results with bootstrap stats to: {filename}")