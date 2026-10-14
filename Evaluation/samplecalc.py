import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from scipy.stats import norm

# 1. โหลดข้อมูลจากไฟล์ CSV
df = pd.read_csv('gemini3.1-flash.csv')

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

# 4. ฟังก์ชันคำนวณขนาดตัวอย่างขั้นต่ำสำหรับ McNemar's Test (แยกตามแต่ละ Label)
def calculate_mcnemar_sample_size(y_true, y_pred, label_names, alpha=0.05, power=0.8):
    n_samp, n_lab = y_true.shape
    # ปรับแก้ alpha ด้วย Bonferroni Correction ตามจำนวน Label
    adjusted_alpha = alpha / n_lab
    
    z_alpha = norm.ppf(1 - adjusted_alpha / 2)
    z_beta = norm.ppf(power)
    
    results = []
    for i in range(n_lab):
        true_i = y_true[:, i]
        pred_i = y_pred[:, i]
        
        # สมมติเปรียบเทียบโมเดลกับ Ground Truth หรือเทียบระหว่างโมเดล
        # ในที่นี้เทียบ model กับ true เพื่อดูสัดส่วนความผิดพลาด (Discordant pairs จาก Pilot)
        correct = (pred_i == true_i)
        
        # หากต้องการคำนวณเทียบระหว่าง 2 โมเดล ให้ใช้ y_pred_modelA และ y_pred_modelB แทน
        # แต่นี่ใช้ pilot data ประมาณสัดส่วนความต่าง (p10, p01)
        # ตัวอย่าง: สมมติสัดส่วนความต่างจาก pilot data
        # n10 = โมเดลทายถูกแต่จริงผิด (หรือสัดส่วนที่ต้องการตรวจจับ)
        
        # คำนวณสัดส่วนความต่างจากข้อมูลจริงในไฟล์
        # สมมติใช้สัดส่วนความคลาดเคลื่อนจริงเป็นฐานในการคำนวณ Effect Size
        errors = np.sum(~correct) / n_samp
        if errors == 0:
            errors = 0.05 # ป้องกัน division by zero กรณีข้อมูลน้อยเกินไป
            
        p10 = errors / 2
        p01 = errors / 2
        
        # ป้องกันส่วนแบ่งเป็นศูนย์
        if (p10 - p01) ** 2 == 0:
            p10 = 0.3
            p01 = 0.1
            
        # สูตรคำนวณขนาดตัวอย่าง McNemar
        n_req = ((z_alpha + z_beta) ** 2 * (p10 + p01)) / ((p10 - p01) ** 2)
        
        results.append({
            'Label': label_names[i],
            'Pilot_Error_Rate': errors,
            'Required_Sample_Size': int(np.ceil(n_req))
        })
        
    return pd.DataFrame(results)

# รันการคำนวณ
df_sample_size = calculate_mcnemar_sample_size(y_true_bin, y_pred_bin, mlb.classes_)
print(df_sample_size)