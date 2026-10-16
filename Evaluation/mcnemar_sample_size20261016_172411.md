# McNemar Sample Size Calculation Report

รายงานการวิเคราะห์และคำนวณขนาดตัวอย่างขั้นต่ำสำหรับแต่ละ Label จากข้อมูล Pilot Data

---

_ผลวิเคราะห์จากไฟล์: gemini3.1-flash.csv เมื่อ 20261016_172411_## Label: Administration Error

### 1. Crosstab Table (2x2 Matrix)
ตารางแสดงความถี่เปรียบเทียบระหว่าง Ground Truth (แถว) และ Model Prediction (คอลัมน์):

|   True |   0 |   1 |
|--------|-----|-----|
|      0 |  26 |   1 |
|      1 |   0 |   8 |

### 2. สัดส่วนความผิดพลาด ($p_{10}$ และ $p_{01}$)
- **False Negative Proportion ($p_{10}$):** 0.0000 (คำนวณจาก $FN = 0 / 35$)
- **False Positive Proportion ($p_{01}$):** 0.0286 (คำนวณจาก $FP = 1 / 35$)

### 3. รายละเอียดการแทนค่าในสูตร
- **สูตร:** $$n = \frac{(z_\alpha + z_\beta)^2 (p_{10} + p_{01})}{(p_{10} - p_{01})^2}$$
- **ค่าพารามิเตอร์ที่ใช้:**
  - Adjusted Alpha ($lpha_{adj}$): `0.00833`
  - $z_\alpha$ (Critical value): `2.6383`
  - $z_\beta$ (Power 80%): `0.8416`
  - $p_{10}$ (False Negative): `0.0000`
  - $p_{01}$ (False Positive): `0.0286`
- **ผลการคำนวณ:**
  $$n = \frac{(2.6383 + 0.8416)^2 (0.0000 + 0.0286)}{(0.0000 - 0.0286)^2} = 423.83$$
- **ขนาดตัวอย่างขั้นต่ำที่ต้องการสำหรับ Label นี้:** **424 ตัวอย่าง**

---

## Label: Dispensing Error

### 1. Crosstab Table (2x2 Matrix)
ตารางแสดงความถี่เปรียบเทียบระหว่าง Ground Truth (แถว) และ Model Prediction (คอลัมน์):

|   True |   0 |   1 |
|--------|-----|-----|
|      0 |  15 |   7 |
|      1 |   1 |  12 |

### 2. สัดส่วนความผิดพลาด ($p_{10}$ และ $p_{01}$)
- **False Negative Proportion ($p_{10}$):** 0.0286 (คำนวณจาก $FN = 1 / 35$)
- **False Positive Proportion ($p_{01}$):** 0.2000 (คำนวณจาก $FP = 7 / 35$)

### 3. รายละเอียดการแทนค่าในสูตร
- **สูตร:** $$n = \frac{(z_\alpha + z_\beta)^2 (p_{10} + p_{01})}{(p_{10} - p_{01})^2}$$
- **ค่าพารามิเตอร์ที่ใช้:**
  - Adjusted Alpha ($lpha_{adj}$): `0.00833`
  - $z_\alpha$ (Critical value): `2.6383`
  - $z_\beta$ (Power 80%): `0.8416`
  - $p_{10}$ (False Negative): `0.0286`
  - $p_{01}$ (False Positive): `0.2000`
- **ผลการคำนวณ:**
  $$n = \frac{(2.6383 + 0.8416)^2 (0.0286 + 0.2000)}{(0.0286 - 0.2000)^2} = 94.19$$
- **ขนาดตัวอย่างขั้นต่ำที่ต้องการสำหรับ Label นี้:** **95 ตัวอย่าง**

---

## Label: Predispensing Error

### 1. Crosstab Table (2x2 Matrix)
ตารางแสดงความถี่เปรียบเทียบระหว่าง Ground Truth (แถว) และ Model Prediction (คอลัมน์):

|   True |   0 |   1 |
|--------|-----|-----|
|      0 |  25 |   5 |
|      1 |   0 |   5 |

### 2. สัดส่วนความผิดพลาด ($p_{10}$ และ $p_{01}$)
- **False Negative Proportion ($p_{10}$):** 0.0000 (คำนวณจาก $FN = 0 / 35$)
- **False Positive Proportion ($p_{01}$):** 0.1429 (คำนวณจาก $FP = 5 / 35$)

### 3. รายละเอียดการแทนค่าในสูตร
- **สูตร:** $$n = \frac{(z_\alpha + z_\beta)^2 (p_{10} + p_{01})}{(p_{10} - p_{01})^2}$$
- **ค่าพารามิเตอร์ที่ใช้:**
  - Adjusted Alpha ($lpha_{adj}$): `0.00833`
  - $z_\alpha$ (Critical value): `2.6383`
  - $z_\beta$ (Power 80%): `0.8416`
  - $p_{10}$ (False Negative): `0.0000`
  - $p_{01}$ (False Positive): `0.1429`
- **ผลการคำนวณ:**
  $$n = \frac{(2.6383 + 0.8416)^2 (0.0000 + 0.1429)}{(0.0000 - 0.1429)^2} = 84.77$$
- **ขนาดตัวอย่างขั้นต่ำที่ต้องการสำหรับ Label นี้:** **85 ตัวอย่าง**

---

## Label: Prescribing Error

### 1. Crosstab Table (2x2 Matrix)
ตารางแสดงความถี่เปรียบเทียบระหว่าง Ground Truth (แถว) และ Model Prediction (คอลัมน์):

|   True |   0 |   1 |
|--------|-----|-----|
|      0 |  19 |   4 |
|      1 |   2 |  10 |

### 2. สัดส่วนความผิดพลาด ($p_{10}$ และ $p_{01}$)
- **False Negative Proportion ($p_{10}$):** 0.0571 (คำนวณจาก $FN = 2 / 35$)
- **False Positive Proportion ($p_{01}$):** 0.1143 (คำนวณจาก $FP = 4 / 35$)

### 3. รายละเอียดการแทนค่าในสูตร
- **สูตร:** $$n = \frac{(z_\alpha + z_\beta)^2 (p_{10} + p_{01})}{(p_{10} - p_{01})^2}$$
- **ค่าพารามิเตอร์ที่ใช้:**
  - Adjusted Alpha ($lpha_{adj}$): `0.00833`
  - $z_\alpha$ (Critical value): `2.6383`
  - $z_\beta$ (Power 80%): `0.8416`
  - $p_{10}$ (False Negative): `0.0571`
  - $p_{01}$ (False Positive): `0.1143`
- **ผลการคำนวณ:**
  $$n = \frac{(2.6383 + 0.8416)^2 (0.0571 + 0.1143)}{(0.0571 - 0.1143)^2} = 635.75$$
- **ขนาดตัวอย่างขั้นต่ำที่ต้องการสำหรับ Label นี้:** **636 ตัวอย่าง**

---

## Label: Transcribing Error

### 1. Crosstab Table (2x2 Matrix)
ตารางแสดงความถี่เปรียบเทียบระหว่าง Ground Truth (แถว) และ Model Prediction (คอลัมน์):

|   True |   0 |   1 |
|--------|-----|-----|
|      0 |  23 |   8 |
|      1 |   0 |   4 |

### 2. สัดส่วนความผิดพลาด ($p_{10}$ และ $p_{01}$)
- **False Negative Proportion ($p_{10}$):** 0.0000 (คำนวณจาก $FN = 0 / 35$)
- **False Positive Proportion ($p_{01}$):** 0.2286 (คำนวณจาก $FP = 8 / 35$)

### 3. รายละเอียดการแทนค่าในสูตร
- **สูตร:** $$n = \frac{(z_\alpha + z_\beta)^2 (p_{10} + p_{01})}{(p_{10} - p_{01})^2}$$
- **ค่าพารามิเตอร์ที่ใช้:**
  - Adjusted Alpha ($lpha_{adj}$): `0.00833`
  - $z_\alpha$ (Critical value): `2.6383`
  - $z_\beta$ (Power 80%): `0.8416`
  - $p_{10}$ (False Negative): `0.0000`
  - $p_{01}$ (False Positive): `0.2286`
- **ผลการคำนวณ:**
  $$n = \frac{(2.6383 + 0.8416)^2 (0.0000 + 0.2286)}{(0.0000 - 0.2286)^2} = 52.98$$
- **ขนาดตัวอย่างขั้นต่ำที่ต้องการสำหรับ Label นี้:** **53 ตัวอย่าง**

---

## Label: Unclassified

### 1. Crosstab Table (2x2 Matrix)
ตารางแสดงความถี่เปรียบเทียบระหว่าง Ground Truth (แถว) และ Model Prediction (คอลัมน์):

|   True |   0 |   1 |
|--------|-----|-----|
|      0 |  34 |   0 |
|      1 |   1 |   0 |

### 2. สัดส่วนความผิดพลาด ($p_{10}$ และ $p_{01}$)
- **False Negative Proportion ($p_{10}$):** 0.0286 (คำนวณจาก $FN = 1 / 35$)
- **False Positive Proportion ($p_{01}$):** 0.0000 (คำนวณจาก $FP = 0 / 35$)

### 3. รายละเอียดการแทนค่าในสูตร
- **สูตร:** $$n = \frac{(z_\alpha + z_\beta)^2 (p_{10} + p_{01})}{(p_{10} - p_{01})^2}$$
- **ค่าพารามิเตอร์ที่ใช้:**
  - Adjusted Alpha ($lpha_{adj}$): `0.00833`
  - $z_\alpha$ (Critical value): `2.6383`
  - $z_\beta$ (Power 80%): `0.8416`
  - $p_{10}$ (False Negative): `0.0286`
  - $p_{01}$ (False Positive): `0.0000`
- **ผลการคำนวณ:**
  $$n = \frac{(2.6383 + 0.8416)^2 (0.0286 + 0.0000)}{(0.0286 - 0.0000)^2} = 423.83$$
- **ขนาดตัวอย่างขั้นต่ำที่ต้องการสำหรับ Label นี้:** **424 ตัวอย่าง**

---

# Summary: Required Sample Sizes per Label

ตารางสรุปขนาดตัวอย่างขั้นต่ำ ($n$) ที่ต้องใช้ในการทดสอบของแต่ละ Label:

               Label  Required_Sample_Size
Administration Error                   424
    Dispensing Error                    95
 Predispensing Error                    85
   Prescribing Error                   636
  Transcribing Error                    53
        Unclassified                   424
