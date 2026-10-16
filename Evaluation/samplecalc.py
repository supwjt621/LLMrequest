import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from scipy.stats import norm
import os
from datetime import datetime
#ref: https://www.medcalc.org/en/manual/sample-size-mcnemar-test.php?utm_source=chatgpt.com

# 1. โหลดข้อมูลจากไฟล์ CSV
fileName = 'qwen3.8-max_test.csv'
df = pd.read_csv(fileName)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# 2. แปลงข้อความ Multilabel ที่คั่นด้วยคอมมา ให้เป็น List ของ String
y_true_lists = df['result'].apply(lambda x: [item.strip() for item in str(x).split(',') if item.strip()])
y_pred_lists = df['model'].apply(lambda x: [item.strip() for item in str(x).split(',') if item.strip()])

# 3. ใช้ MultiLabelBinarizer แปลงเป็น Binary Matrix (One-hot encoding)
mlb = MultiLabelBinarizer()
all_labels = sorted(list(set(y_true_lists.explode().unique()) | set(y_pred_lists.explode().unique())))
mlb.fit([all_labels])

y_true_bin = mlb.transform(y_true_lists)
y_pred_bin = mlb.transform(y_pred_lists)

n_samples, n_labels = y_true_bin.shape
print(f"จำนวนตัวอย่างใน Pilot Data: {n_samples}, จำนวน Labels: {n_labels}")
print(f"รายชื่อ Labels: {mlb.classes_}\n")

# 4. ฟังก์ชันคำนวณขนาดตัวอย่างขั้นต่ำสำหรับ McNemar's Test พร้อมจัดทำรายงาน Markdown
def calculate_mcnemar_sample_size(y_true, y_pred, label_names, alpha=0.05, power=0.8):
    n_samp, n_lab = y_true.shape
    # ปรับแก้ alpha ด้วย Bonferroni Correction ตามจำนวน Label
    adjusted_alpha = alpha / n_lab
    
    z_alpha = norm.ppf(1 - adjusted_alpha / 2)
    z_beta = norm.ppf(power)
    
    results = []
    markdown_sections = []
    
    for i in range(n_lab):
        true_i = y_true[:, i]
        pred_i = y_pred[:, i]
        
        # สร้าง 2x2 Crosstab (Confusion Matrix) ระหว่าง Ground Truth กับ Model Prediction
        # Index = True (0, 1), Columns = Pred (0, 1)
        crosstab = pd.crosstab(
            pd.Series(true_i, name='True'), 
            pd.Series(pred_i, name='Pred')
        ).reindex(index=[0, 1], columns=[0, 1], fill_value=0)
        
        tn = crosstab.loc[0, 0]
        fp = crosstab.loc[0, 1] # False Positive (True=0, Pred=1)
        fn = crosstab.loc[1, 0] # False Negative (True=1, Pred=0)
        tp = crosstab.loc[1, 1] # True Positive (True=1, Pred=1)
        
        # คำนวณสัดส่วนจาก Crosstab และจับคู่ตามความหมาย
        p_false_negative = fn / n_samp  # ทำหน้าที่เป็น p10
        p_false_positive = fp / n_samp  # ทำหน้าที่เป็น p01
        
        p10 = p_false_negative
        p01 = p_false_positive
        
        # ป้องกันส่วนแบ่งเป็นศูนย์หรือผลต่างเป็นศูนย์
        if (p10 + p01) == 0:
            p10 = 0.05
            p01 = 0.05
            
        if (p10 - p01) ** 2 == 0:
            p10 = 0.3
            p01 = 0.1
            
        # สูตรคำนวณขนาดตัวอย่าง McNemar
        n_req = ((z_alpha + z_beta) ** 2 * (p10 + p01)) / ((p10 - p01) ** 2)
        req_sample_size = int(np.ceil(n_req))
        
        results.append({
            'Label': label_names[i],
            'Required_Sample_Size': req_sample_size
        })
        
        # แปลง Crosstab เป็น Markdown table
        ct_md = crosstab.to_markdown()
        
        # จัดเตรียมเนื้อหา Markdown สำหรับแต่ละ Label
        sec = f"## Label: {label_names[i]}\n\n"
        sec += f"### 1. Crosstab Table (2x2 Matrix)\n"
        sec += f"ตารางแสดงความถี่เปรียบเทียบระหว่าง Ground Truth (แถว) และ Model Prediction (คอลัมน์):\n\n"
        sec += f"{ct_md}\n\n"
        sec += f"### 2. สัดส่วนความผิดพลาด ($p_{{10}}$ และ $p_{{01}}$)\n"
        sec += f"- **False Negative Proportion ($p_{{{10}}}$):** {p_false_negative:.4f} (คำนวณจาก $FN = {fn} / {n_samp}$)\n"
        sec += f"- **False Positive Proportion ($p_{{01}}$):** {p_false_positive:.4f} (คำนวณจาก $FP = {fp} / {n_samp}$)\n\n"
        sec += f"### 3. รายละเอียดการแทนค่าในสูตร\n"
        sec += f"- **สูตร:** $$n = \\frac{{(z_\\alpha + z_\\beta)^2 (p_{{10}} + p_{{01}})}}{{(p_{{10}} - p_{{01}})^2}}$$\n"
        sec += f"- **ค่าพารามิเตอร์ที่ใช้:**\n"
        sec += f"  - Adjusted Alpha ($\\alpha_{{adj}}$): `{adjusted_alpha:.5f}`\n"
        sec += f"  - $z_\\alpha$ (Critical value): `{z_alpha:.4f}`\n"
        sec += f"  - $z_\\beta$ (Power 80%): `{z_beta:.4f}`\n"
        sec += f"  - $p_{{10}}$ (False Negative): `{p10:.4f}`\n"
        sec += f"  - $p_{{01}}$ (False Positive): `{p01:.4f}`\n"
        sec += f"- **ผลการคำนวณ:**\n"
        sec += f"  $$n = \\frac{{({z_alpha:.4f} + {z_beta:.4f})^2 ({p10:.4f} + {p01:.4f})}}{{({p10:.4f} - {p01:.4f})^2}} = {n_req:.2f}$$\n"
        sec += f"- **ขนาดตัวอย่างขั้นต่ำที่ต้องการสำหรับ Label นี้:** **{req_sample_size} ตัวอย่าง**\n\n"
        sec += "---\n\n"
        markdown_sections.append(sec)
        
    return pd.DataFrame(results), markdown_sections

# รันการคำนวณ
df_sample_size, md_sections = calculate_mcnemar_sample_size(y_true_bin, y_pred_bin, mlb.classes_)
print(df_sample_size)


# Export results to markdown file in the same directory as the script
script_dir = os.path.dirname(os.path.abspath(__file__))
md_path = os.path.join(script_dir, 'mcnemar_sample_size'+ timestamp +'.md')

with open(md_path, 'w', encoding='utf-8') as f:
    f.write('# McNemar Sample Size Calculation Report\n\n')
    f.write('รายงานการวิเคราะห์และคำนวณขนาดตัวอย่างขั้นต่ำสำหรับแต่ละ Label จากข้อมูล Pilot Data\n')
    f.write(f'_ผลวิเคราะห์จากไฟล์: {fileName} เมื่อ {timestamp}_\n\n---\n\n')
    
    
    # เขียนรายละเอียดของแต่ละ Label
    for sec in md_sections:
        f.write(sec)
        
    # สรุปค่า n ไว้ที่ท้ายสุดของไฟล์ตามคำขอ
    f.write('# Summary: Required Sample Sizes per Label\n\n')
    f.write('ตารางสรุปขนาดตัวอย่างขั้นต่ำ ($n$) ที่ต้องใช้ในการทดสอบของแต่ละ Label:\n\n')
    f.write(df_sample_size.to_string(index=False))
    f.write('\n')

print(f'Results exported to {md_path}')