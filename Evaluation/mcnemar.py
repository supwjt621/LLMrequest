import pandas as pd
from datetime import datetime
from statsmodels.stats.contingency_tables import mcnemar

# 1. อ่านไฟล์ CSV
fileName = 'qwen3.8-max_test.csv'
df = pd.read_csv(fileName)

# กำหนดรายชื่อ Label ทั้งหมดตามโจทย์
labels = [
    'Prescribing Error', 
    'Transcribing Error', 
    'Predispensing Error', 
    'Dispensing Error', 
    'Administration Error', 
    'Unclassified'
]

results_list = []

# 2. วนลูปคำนวณ McNemar Test ทีละ Label
for label in labels:
    # แปลงข้อมูลแบบ Multi-label (comma-separated) ให้เป็น Binary vector (True/False)
    gt = df['result'].apply(lambda x: label in [l.strip() for l in str(x).split(',')])
    pred = df['model'].apply(lambda x: label in [l.strip() for l in str(x).split(',')])
    
    # สร้าง 2x2 Contingency Table (Ground Truth vs Model Prediction)
    # index=[False, True] (Ground Truth), columns=[False, True] (Model Prediction)
    table = pd.crosstab(gt, pred).reindex(index=[False, True], columns=[False, True], fill_value=0)
    
    # ดึงค่าความถี่ในตาราง
    # TN: Ground Truth=False, Model=False
    # FP: Ground Truth=False, Model=True (Model ทำนายเกินมา)
    # FN: Ground Truth=True, Model=False (Model ทำนายตกหล่น)
    # TP: Ground Truth=True, Model=True
    tn = table.loc[False, False]
    fp = table.loc[False, True]
    fn = table.loc[True, False]
    tp = table.loc[True, True]
    
    # รัน McNemar Test (ใช้ exact=True เหมาะกับกลุ่มตัวอย่างขนาดเล็ก)
    res = mcnemar(table.values, exact=True)
    
    results_list.append({
        'Label': label,
        'TN': tn,
        'FP': fp,
        'FN': fn,
        'TP': tp,
        'p-value': res.pvalue,
        'statistic [min(FP,FN)]': res.statistic
    })

# 3. สร้าง DataFrame สรุปผล
res_df = pd.DataFrame(results_list)

# แสดงผลลัพธ์ทางหน้าจอ
print(res_df.to_markdown(index=False))

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# 4. Export ผลลัพธ์ออกเป็นไฟล์ Markdown (.md)
markdown_text = res_df.to_markdown(index=False)
with open('mcnemar_test_'+ fileName + '_' + timestamp +'.md', 'w', encoding='utf-8') as f:
    f.write("# McNemar Test Summary Results\n")
    f.write("fileName: " + fileName + "\n\n")
    f.write(markdown_text)


print("\nบันทึกไฟล์สรุปผลเป็น 'mcnemar_test_"+ timestamp +".md' เรียบร้อยแล้ว")