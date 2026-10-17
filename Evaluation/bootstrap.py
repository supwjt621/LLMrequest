import numpy as np
import pandas as pd
from datetime import datetime
from scipy.stats import bootstrap
from sklearn.metrics import multilabel_confusion_matrix, precision_recall_fscore_support
from statsmodels.stats.contingency_tables import mcnemar
from sklearn.preprocessing import MultiLabelBinarizer

# ---------------------------------------------------------------
# Config
# ---------------------------------------------------------------
LABELS = [
    'Prescribing Error',
    'Transcribing Error',
    'Predispensing Error',
    'Dispensing Error',
    'Administration Error',
    'Unclassified',
]
CANON = {l.lower(): l for l in LABELS}  # ใช้ normalize ตัวพิมพ์เล็ก/ใหญ่

N_BOOTSTRAP = 1000
CONFIDENCE = 0.95
SEED = 42

input_name = 'gemini3.1-flash'

# ---------------------------------------------------------------
# 1. Read CSV
# ---------------------------------------------------------------
df = pd.read_csv(input_name + '.csv')


# ---------------------------------------------------------------
# 2. แปลงข้อความ (คั่นด้วย comma) เป็น list ของ label
# ---------------------------------------------------------------
def to_labels(x):
    if pd.isna(x):
        return []
    out = []
    for s in str(x).split(','):
        s = s.strip()
        if not s:
            continue
        if s.lower() not in CANON:
            print(f"[WARNING] พบ label ที่ไม่รู้จัก: '{s}' (จะถูกข้าม)")
            continue
        out.append(CANON[s.lower()])
    return out


y_true_lists = df['result'].apply(to_labels)
y_pred_lists = df['model'].apply(to_labels)

# ---------------------------------------------------------------
# 3. Binarize โดยกำหนด classes ตายตัว 6 label
#    (ไม่ fit จากข้อมูล เพื่อให้คอลัมน์คงที่ แม้บาง class จะไม่เจอใน ground truth)
# ---------------------------------------------------------------
mlb = MultiLabelBinarizer(classes=LABELS)
y_true = mlb.fit_transform(y_true_lists)
y_pred = mlb.transform(y_pred_lists)

# ---------------------------------------------------------------
# 4. Metrics รายแถว (per-sample)
# ---------------------------------------------------------------
row_scores = np.array([
    precision_recall_fscore_support(
        y_true[i:i + 1], y_pred[i:i + 1],
        average='samples', zero_division=0
    )[:3]
    for i in range(len(y_true))
])  # shape (n_samples, 3)

# TP / FP / FN รายแถว (นับรวมทุก label ในแถวนั้น)
# samplewise=True -> ได้ confusion matrix 2x2 ต่อแถว: [[TN, FP], [FN, TP]]
cm = multilabel_confusion_matrix(y_true, y_pred, samplewise=True)
df['true positive'] = cm[:, 1, 1]
df['false positive'] = cm[:, 0, 1]
df['false negative'] = cm[:, 1, 0]
df['true negative'] = cm[:, 0, 0]

df['precision'] = row_scores[:, 0]
df['recall'] = row_scores[:, 1]
df['f1-score'] = row_scores[:, 2]

df_export = df[[
    'รหัสรายงาน', 'result', 'model',
    'true positive', 'false positive', 'false negative', 'true negative',
    'precision', 'recall', 'f1-score',
]].copy()

# ---------------------------------------------------------------
# 5. Sample-average metrics ทั้งชุดข้อมูล
# ---------------------------------------------------------------
overall_p, overall_r, overall_f, _ = precision_recall_fscore_support(
    y_true, y_pred, average='samples', zero_division=0
)

# sample-average = ค่าเฉลี่ยของ metric รายแถว -> ตรวจสอบความสอดคล้อง
assert np.isclose(overall_f, row_scores[:, 2].mean())

# ---------------------------------------------------------------
# 6. Bootstrap 95% CI (percentile) ด้วย scipy.stats.bootstrap
#    resample "แถว" แล้วหาค่าเฉลี่ยของ metric รายแถว
#    ซึ่งเท่ากับการคำนวณ sample-average ใหม่ในแต่ละรอบ แต่เร็วกว่ามาก
# ---------------------------------------------------------------
def boot_ci(values):
    res = bootstrap(
        (values,), np.mean,
        n_resamples=N_BOOTSTRAP,
        confidence_level=CONFIDENCE,
        method='percentile',
        random_state=SEED,
    )
    return res.confidence_interval.low, res.confidence_interval.high


p_low, p_high = boot_ci(row_scores[:, 0])
r_low, r_high = boot_ci(row_scores[:, 1])
f1_low, f1_high = boot_ci(row_scores[:, 2])

print(f"Sample-average Precision: {overall_p:.4f}  95% CI [{p_low:.4f}, {p_high:.4f}]")
print(f"Sample-average Recall:    {overall_r:.4f}  95% CI [{r_low:.4f}, {r_high:.4f}]")
print(f"Sample-average F1:        {overall_f:.4f}  95% CI [{f1_low:.4f}, {f1_high:.4f}]\n")

# ---------------------------------------------------------------
# 7. สรุปท้ายตาราง CSV
# ---------------------------------------------------------------
summary_row = {
    'รหัสรายงาน': 'Overall (Observed)',
    'result': '', 'model': '',
    'true positive': int(cm[:, 1, 1].sum()),
    'false positive': int(cm[:, 0, 1].sum()),
    'false negative': int(cm[:, 1, 0].sum()),
    'true negative': int(cm[:, 0, 0].sum()),
    'precision': overall_p, 'recall': overall_r, 'f1-score': overall_f,
}
ci_row = {
    'รหัสรายงาน': '95% Bootstrap CI',
    'result': '', 'model': '',
    'true positive': '', 'false positive': '', 'false negative': '', 'true negative': '',
    'precision': f"[{p_low:.4f}, {p_high:.4f}]",
    'recall': f"[{r_low:.4f}, {r_high:.4f}]",
    'f1-score': f"[{f1_low:.4f}, {f1_high:.4f}]",
}
df_rows = df_export.copy()  # ตารางรายแถวล้วน (ไม่รวมแถวสรุป) ไว้ใช้ใน markdown
df_export = pd.concat([df_export, pd.DataFrame([summary_row, ci_row])], ignore_index=True)

# ---------------------------------------------------------------
# 8. Export CSV
# ---------------------------------------------------------------
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
base_name = f'Evaluate_{input_name}_{timestamp}'
"""
csv_filename = base_name + '.csv'
df_export.to_csv(csv_filename, index=False, encoding='utf-8-sig')
print(f"Exported CSV: {csv_filename}")
"""
# ---------------------------------------------------------------
# 9. Export Markdown
# ---------------------------------------------------------------
md_filename = base_name + '.md'
def to_md_table(d):
    cols = list(d.columns)
    lines = [
        '| ' + ' | '.join(cols) + ' |',
        '|' + '|'.join(['---'] * len(cols)) + '|',
    ]
    for _, r in d.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, (float, np.floating)):
                cells.append(f'{v:.4f}')
            else:
                cells.append(str(v).replace('|', '\\|'))
        lines.append('| ' + ' | '.join(cells) + ' |')
    return '\n'.join(lines)


rows_table_md = to_md_table(df_rows)

# McNemar Test รายละ label (Ground Truth vs Model Prediction)
# cm_label[j] = [[TN, FP], [FN, TP]] โดยแถว = Ground Truth, คอลัมน์ = Model Prediction
# (ตรงกับตาราง 2x2 จาก pd.crosstab ในโค้ด mcnemar.py เดิม)
cm_label = multilabel_confusion_matrix(y_true, y_pred)
mcnemar_lines = [
    '| Label | TP | FP | FN | TN | p-value | statistic [min(FP,FN)] |',
    '|---|---|---|---|---|---|---|',
]
print("McNemar Test (exact=True)")
for label, table in zip(LABELS, cm_label):
    res = mcnemar(table, exact=True)
    tn, fp, fn, tp = table.ravel()
    mcnemar_lines.append(
        f'| {label} | {tp} | {fp} | {fn} | {tn} | {res.pvalue:.4f} | {res.statistic:g} |'
    )
    print(f"  {label}: p-value={res.pvalue:.4f}, statistic={res.statistic:g}")
mcnemar_table_md = '\n'.join(mcnemar_lines)

markdown_content = f"""# Evaluation Results - {input_name}

## Per-report Results (n={len(df_rows)})
{rows_table_md}

## Sample-average Metrics
| Metric | Value |
|--------|-------|
| Precision | {overall_p:.4f} |
| Recall | {overall_r:.4f} |
| F1-score | {overall_f:.4f} |

## Bootstrap Confidence Intervals ({int(CONFIDENCE * 100)}%, n={N_BOOTSTRAP})
| Metric | Lower CI | Upper CI |
|--------|----------|----------|
| Precision | {p_low:.4f} | {p_high:.4f} |
| Recall | {r_low:.4f} | {r_high:.4f} |
| F1-score | {f1_low:.4f} | {f1_high:.4f} |

## McNemar Test Summary Results
fileName: {input_name}.csv

{mcnemar_table_md}
"""
with open(md_filename, 'w', encoding='utf-8') as f:
    f.write(markdown_content)
print(f"Exported Markdown: {md_filename}")