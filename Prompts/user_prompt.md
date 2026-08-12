# Prompt_1
Extract core medication error details from the incident text below following this JSON schema:
Schema:
{
  "reasoning": "Brief step-by-step extraction logic",
  "intended_drug": "string or 'unknown'",
  "actual_drug": "string or 'unknown'",
  "error_stage": "prescribing | transcribing | pre_dispensing | dispensing | administration | unknown",
  "patient_received_drug": true | false | "unknown"
}

### Example 1:
Incident Text: "แพทย์สั่งจ่ายยา KCl 20 mEq แต่เภสัชกรหยิบยาผิดเป็น KCl 40 mEq ตรวจพบขณะจัดยาที่ห้องยา ยังไม่ได้ส่งมอบให้ผู้ป่วย"
Output:
{
  "reasoning": "Intended was KCl 20 mEq. Actual picked was KCl 40 mEq. Error caught during pre-dispensing at pharmacy. Patient did not receive the drug.",
  "intended_drug": "KCl 20 mEq",
  "actual_drug": "KCl 40 mEq",
  "error_stage": "pre_dispensing",
  "patient_received_drug": false
}

### Example 2:
Incident Text: "พยาบาลฉีดยา Morphine 10 mg ให้ผู้ป่วยผิดคน เนื่องจากไม่ได้เช็กชื่อผู้ป่วยก่อนฉีด"
Output:
{
  "reasoning": "Nurse administered Morphine to the wrong patient. Error stage is administration. Patient actually received the drug.",
  "intended_drug": "unknown",
  "actual_drug": "Morphine 10 mg",
  "error_stage": "administration",
  "patient_received_drug": true
}

### Input Incident Text: 

# End

# Prompt_2
Analyze the incident text and core facts below, then extract the outcome and context details following this JSON schema:
Schema:
{
  "reasoning": "Brief evaluation of harm, HAD status, DDI, and Med Rec context",
  "is_high_alert_drug": true | false | "unknown",
  "is_product_selection_error": true | false | "unknown",
  "med_rec_involved": true | false | "unknown",
  "med_rec_failure": true | false | "unknown",
  "med_rec_omission": true | false | "unknown",
  "med_rec_interaction": true | false | "unknown",
  "ddi_present": true | false | "unknown",
  "harm_occurred": true | false | "unknown"
}

### Example 1:
Incident Text: "ผู้ป่วยแรกรับนอนโรงพยาบาล แพทย์ไม่ได้ลงรายการยาเดิม (Amlodipine 5 mg) ทำให้ผู้ป่วยไม่ได้รับยาเดิม 3 วัน"
Core Facts:
{
  "intended_drug": "Amlodipine 5 mg",
  "actual_drug": "unknown",
  "error_stage": "prescribing",
  "patient_received_drug": false
}
Output:
{
  "reasoning": "Involves admission home med omission. This is a Medication Reconciliation failure resulting in drug omission.",
  "is_high_alert_drug": false,
  "is_product_selection_error": false,
  "med_rec_involved": true,
  "med_rec_failure": true,
  "med_rec_omission": true,
  "med_rec_interaction": false,
  "ddi_present": false,
  "harm_occurred": "unknown"
}

### Example 2:
Incident Text: "แพทย์สั่งจ่ายยา [TAG: HAD] KCl 20 mEq แต่เภสัชกรหยิบยาผิดเป็น KCl 40 mEq ตรวจพบขณะจัดยาที่ห้องยา ยังไม่ได้ส่งมอบให้ผู้ป่วย"
Core Facts:
{
  "intended_drug": "KCl 20 mEq",
  "actual_drug": "KCl 40 mEq",
  "error_stage": "pre_dispensing",
  "patient_received_drug": false
}
Output:
{
  "reasoning": "KCl is tagged as HAD. Error is picking wrong strength/product. Caught before reaching patient, no harm occurred.",
  "is_high_alert_drug": true,
  "is_product_selection_error": true,
  "med_rec_involved": false,
  "med_rec_failure": false,
  "med_rec_omission": false,
  "med_rec_interaction": false,
  "ddi_present": false,
  "harm_occurred": false
}

# End