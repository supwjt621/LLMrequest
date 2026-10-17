import argparse
import os
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.preprocessing import MultiLabelBinarizer

# ref: https://www.medcalc.org/en/manual/sample-size-mcnemar-test.php


# ---------------------------------------------------------------------------
# 1. โหลดและแปลงข้อมูล
# ---------------------------------------------------------------------------
def load_binary_matrices(file_name, true_col='result', pred_col='model'):
    df = pd.read_csv(file_name)

    def split(x):
        return [i.strip() for i in str(x).split(',') if i.strip()]

    y_true_lists = df[true_col].apply(split)
    y_pred_lists = df[pred_col].apply(split)

    all_labels = sorted(set(y_true_lists.explode().dropna()) | set(y_pred_lists.explode().dropna()))
    mlb = MultiLabelBinarizer(classes=all_labels)
    mlb.fit([all_labels])

    return mlb.transform(y_true_lists), mlb.transform(y_pred_lists), list(mlb.classes_)


# ---------------------------------------------------------------------------
# 2. คำนวณ sample size แบบรวมทุก label (pooled / micro-level)
# ---------------------------------------------------------------------------
def mcnemar_n(p10, p01, alpha=0.05, power=0.8):
    """สูตร McNemar sample size ตาม MedCalc (Connor, 1987)
    n = [ z_a*sqrt(p10+p01) + z_b*sqrt(p10+p01-(p10-p01)^2) ]^2 / (p10-p01)^2
    คืนค่าเป็นจำนวนคู่ (paired observations) ที่ต้องการ
    """
    if p10 == p01:
        return np.inf  # ไม่มีความแตกต่าง -> ตรวจจับไม่ได้ไม่ว่า n เท่าไร
    z_a = norm.ppf(1 - alpha / 2)
    z_b = norm.ppf(power)
    psi = p10 + p01
    diff = p10 - p01
    return (z_a * np.sqrt(psi) + z_b * np.sqrt(psi - diff ** 2)) ** 2 / diff ** 2


def pooled_sample_size(y_true, y_pred, alpha=0.05, power=0.8):
    """รวมทุก label เป็นตาราง 2x2 เดียว (flatten ทุกเซลล์ sample x label)"""
    n_samp, n_lab = y_true.shape
    t = y_true.ravel()
    p = y_pred.ravel()
    n_total = t.size  # = n_samp * n_lab

    tp = int(((t == 1) & (p == 1)).sum())
    tn = int(((t == 0) & (p == 0)).sum())
    fp = int(((t == 0) & (p == 1)).sum())
    fn = int(((t == 1) & (p == 0)).sum())

    p10 = fn / n_total  # True=1, Pred=0
    p01 = fp / n_total  # True=0, Pred=1

    n_decisions = mcnemar_n(p10, p01, alpha, power)
    if np.isfinite(n_decisions):
        n_decisions = int(np.ceil(n_decisions))
        # แปลงเป็นจำนวน "ตัวอย่าง (แถว)" โดยแต่ละตัวอย่างให้ n_lab การตัดสินใจ
        n_samples = int(np.ceil(n_decisions / n_lab))
    else:
        n_samples = np.inf

    return {
        'n_samp': n_samp, 'n_lab': n_lab, 'n_total': n_total,
        'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn,
        'p10': p10, 'p01': p01,
        'alpha': alpha, 'power': power,
        'z_alpha': norm.ppf(1 - alpha / 2), 'z_beta': norm.ppf(power),
        'n_decisions': n_decisions, 'n_samples': n_samples,
    }


# ---------------------------------------------------------------------------
# 3. สร้างรายงาน Markdown
# ---------------------------------------------------------------------------
def build_report(r, file_name, timestamp, label_names):
    md = '# McNemar Sample Size Calculation Report (Pooled across all labels)\n\n'
    md += f'_ผลวิเคราะห์จากไฟล์: {file_name} เมื่อ {timestamp}_\n\n---\n\n'
    md += f'**Labels ({r["n_lab"]}):** {", ".join(label_names)}\n\n'
    md += f'**Pilot samples:** {r["n_samp"]} | **Total label decisions:** {r["n_total"]}\n\n'

    md += '## 1. Crosstab รวมทุก Label (2x2)\n\n'
    md += '| True \\ Pred | 0 | 1 |\n|---|---|---|\n'
    md += f'| 0 | {r["tn"]} | {r["fp"]} |\n'
    md += f'| 1 | {r["fn"]} | {r["tp"]} |\n\n'

    md += '## 2. สัดส่วนที่ไม่สอดคล้อง (discordant proportions)\n\n'
    md += f'- $p_{{10}}$ (False Negative) = {r["fn"]} / {r["n_total"]} = **{r["p10"]:.4f}**\n'
    md += f'- $p_{{01}}$ (False Positive) = {r["fp"]} / {r["n_total"]} = **{r["p01"]:.4f}**\n\n'

    md += '## 3. การคำนวณ\n\n'
    md += '$$n = \\frac{\\left(z_{\\alpha}\\sqrt{p_{10}+p_{01}} + z_{\\beta}\\sqrt{p_{10}+p_{01}-(p_{10}-p_{01})^2}\\right)^2}{(p_{10}-p_{01})^2}$$\n\n'
    md += f'- $\\alpha$ = {r["alpha"]} (ทดสอบครั้งเดียว จึงไม่ต้องทำ Bonferroni)\n'
    md += f'- Power = {r["power"]}\n'
    md += f'- $z_\\alpha$ = {r["z_alpha"]:.4f}, $z_\\beta$ = {r["z_beta"]:.4f}\n\n'

    md += '## 4. ผลลัพธ์\n\n'
    if np.isfinite(r['n_samples']):
        md += f'- จำนวน label decisions ขั้นต่ำ: **{r["n_decisions"]}**\n'
        md += f'- จำนวนตัวอย่าง (แถว) ขั้นต่ำ: **{r["n_samples"]}** '
        md += f'(= ⌈{r["n_decisions"]} / {r["n_lab"]}⌉)\n\n'
    else:
        md += '- $p_{10} = p_{01}$ จึงคำนวณไม่ได้ (ไม่มีความแตกต่างให้ตรวจจับ) '
        md += 'ควรกำหนดค่า p10/p01 ที่ต้องการตรวจจับเองจากความรู้เชิงคลินิก/งานวิจัยอ้างอิง\n\n'

    md += ('> หมายเหตุ: การแปลงเป็นจำนวนตัวอย่างสมมติว่าการตัดสินใจแต่ละ label ในตัวอย่างเดียวกัน '
           'เป็นอิสระต่อกัน ซึ่งมักไม่จริง (labels ในแถวเดียวกันสัมพันธ์กัน) '
           'จึงอาจประเมินต่ำกว่าความจริง ควรใช้เป็นค่าขั้นต่ำ\n')
    return md


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', default='qwen3.8-max_test.csv')
    parser.add_argument('--true-col', default='result')
    parser.add_argument('--pred-col', default='model')
    parser.add_argument('--alpha', type=float, default=0.05)
    parser.add_argument('--power', type=float, default=0.8)
    args = parser.parse_args()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    y_true, y_pred, labels = load_binary_matrices(args.file, args.true_col, args.pred_col)
    print(f'จำนวนตัวอย่างใน Pilot Data: {y_true.shape[0]}, จำนวน Labels: {len(labels)}')
    print(f'รายชื่อ Labels: {labels}\n')

    res = pooled_sample_size(y_true, y_pred, args.alpha, args.power)
    print(f'p10 (FN) = {res["p10"]:.4f}, p01 (FP) = {res["p01"]:.4f}')
    print(f'Required label decisions: {res["n_decisions"]}')
    print(f'Required samples (rows):  {res["n_samples"]}')

    script_dir = os.path.dirname(os.path.abspath(__file__))
    md_path = os.path.join(script_dir, f'mcnemar_sample_size_pooled_{timestamp}.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(build_report(res, args.file, timestamp, labels))
    print(f'Results exported to {md_path}')