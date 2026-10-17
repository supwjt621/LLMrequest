# McNemar Sample Size Calculation Report (Pooled across all labels)

_ผลวิเคราะห์จากไฟล์: qwen3.8-max_261017_135107.csv เมื่อ 20261017_135542_

---

**Labels (6):** Administration Error, Dispensing Error, Predispensing Error, Prescribing Error, Transcribing Error, Unclassified

**Pilot samples:** 35 | **Total label decisions:** 210

## 1. Crosstab รวมทุก Label (2x2)

| True \ Pred | 0 | 1 |
|---|---|---|
| 0 | 153 | 14 |
| 1 | 11 | 32 |

## 2. สัดส่วนที่ไม่สอดคล้อง (discordant proportions)

- $p_{10}$ (False Negative) = 11 / 210 = **0.0524**
- $p_{01}$ (False Positive) = 14 / 210 = **0.0667**

## 3. การคำนวณ

$$n = \frac{\left(z_{\alpha}\sqrt{p_{10}+p_{01}} + z_{\beta}\sqrt{p_{10}+p_{01}-(p_{10}-p_{01})^2}\right)^2}{(p_{10}-p_{01})^2}$$

- $\alpha$ = 0.05 (ทดสอบครั้งเดียว จึงไม่ต้องทำ Bonferroni)
- Power = 0.8
- $z_\alpha$ = 1.9600, $z_\beta$ = 0.8416

## 4. ผลลัพธ์

- จำนวน label decisions ขั้นต่ำ: **4577**
- จำนวนตัวอย่าง (แถว) ขั้นต่ำ: **763** (= ⌈4577 / 6⌉)

> หมายเหตุ: การแปลงเป็นจำนวนตัวอย่างสมมติว่าการตัดสินใจแต่ละ label ในตัวอย่างเดียวกัน เป็นอิสระต่อกัน ซึ่งมักไม่จริง (labels ในแถวเดียวกันสัมพันธ์กัน) จึงอาจประเมินต่ำกว่าความจริง ควรใช้เป็นค่าขั้นต่ำ
