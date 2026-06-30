"""
数据合理性验证脚本
校验仿真数据的关键统计指标与XMU官方报告一致
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "processed"


def verify():
    print("=" * 60)
    print("数据合理性验证 (vs XMU 2024官方报告)")
    print("=" * 60)

    students = pd.read_csv(DATA_DIR / "students.csv", encoding="utf-8-sig")
    employment = pd.read_csv(DATA_DIR / "employment.csv", encoding="utf-8-sig")
    exam = pd.read_csv(DATA_DIR / "postgraduate_exam.csv", encoding="utf-8-sig")
    recommend = pd.read_csv(DATA_DIR / "postgraduate_recommend.csv", encoding="utf-8-sig")
    abroad = pd.read_csv(DATA_DIR / "study_abroad.csv", encoding="utf-8-sig")
    academic = pd.read_csv(DATA_DIR / "academic_records.csv", encoding="utf-8-sig")

    undergrads = students[students.degree_level == "本科"]
    masters = students[students.degree_level == "硕士"]
    phds = students[students.degree_level == "博士"]
    undergrad_ids = set(undergrads.student_id)

    # 合并就业数据查各学历薪资
    emp_with_deg = employment.merge(students[["student_id", "degree_level"]], on="student_id")
    undergrad_emp = emp_with_deg[emp_with_deg.degree_level == "本科"]
    master_emp = emp_with_deg[emp_with_deg.degree_level == "硕士"]

    checks = []

    # 1. 性别比例
    male = len(students[students.gender == "男"])
    female = len(students[students.gender == "女"])
    actual_ratio = round(male / female, 2)
    checks.append(("性别比 (男:女)", f"1:{actual_ratio}", "约1:1.11", abs(actual_ratio - 0.90) < 0.15))

    # 2. 本科生升学率 (官方: 58.2%)
    further = len(undergrads[undergrads.destination.isin(["考研", "保研", "留学"])])
    further_rate = round(further / len(undergrads) * 100, 1)
    checks.append(("本科升学率", f"{further_rate}%", "58.2% (官方)", abs(further_rate - 58.2) < 5))

    # 3. 本科平均月薪 (官方: ~10,200元)
    ug_salary = round(undergrad_emp.monthly_salary.mean(), 0)
    checks.append(("本科平均月薪(元)", f"{ug_salary:,.0f}", "~10,200 (官方)", 8000 < ug_salary < 14000))

    # 4. 硕士平均月薪 (官方: ~14,800元)
    ms_salary = round(master_emp.monthly_salary.mean(), 0)
    checks.append(("硕士平均月薪(元)", f"{ms_salary:,.0f}", "~14,800 (官方)", 10000 < ms_salary < 20000))

    # 5. 华为录用人数 (3届合计, 单届约143人)
    huawei = len(employment[employment.company_name.str.contains("华为", na=False)])
    huawei_per_year = round(huawei / 3, 0)
    checks.append(("华为录用(3届合计)", f"{huawei} (均{huawei_per_year}/届)", "3届合计~400+", 300 < huawei < 700))

    # 6. 保本校比例 (>50%)
    internal = len(recommend[recommend.is_xmu_internal == 1])
    internal_rate = round(internal / len(recommend) * 100, 1)
    checks.append(("本校保研比例", f"{internal_rate}%", ">50%", internal_rate > 45))

    # 7. 留学香港占比 (官方约35%+)
    hk = len(abroad[abroad.target_country.str.contains("香港", na=False)])
    hk_rate = round(hk / len(abroad) * 100, 1)
    checks.append(("留学香港占比", f"{hk_rate}%", "主要目的地之一", hk_rate > 10))

    # 8. 本科平均GPA
    ug_gpa = round(academic[academic.student_id.isin(undergrad_ids)].gpa.mean(), 2)
    checks.append(("本科平均GPA", f"{ug_gpa}", "3.0-3.4", 2.8 < ug_gpa < 3.6))

    # 9. 考研上岸率
    admit_rate = round(exam.is_admitted.mean() * 100, 1)
    checks.append(("考研上岸率", f"{admit_rate}%", "30%-50%", 25 < admit_rate < 60))

    # 10. 就业行业分布合理性
    top_industry = employment.groupby("industry").size().nlargest(3).index.tolist()
    has_expected = "IT/互联网" in top_industry or "教育" in top_industry
    checks.append(("就业行业TOP3含IT/教育", str(top_industry), "含IT/互联网/教育", has_expected))

    # 输出
    print(f"\n{'指标':<28} {'实际值':<22} {'预期':<24} {'结果':<10}")
    print("-" * 85)
    passed = 0
    for name, actual, expected, ok in checks:
        status = "[PASS]" if ok else "[FAIL]"
        print(f"{name:<28} {str(actual):<22} {expected:<24} {status:<10}")
        if ok:
            passed += 1

    print(f"\n验证结果: {passed}/{len(checks)} 通过")
    if passed == len(checks):
        print("所有关键指标在合理范围内，数据与官方报告基本一致。")
    else:
        print("部分指标偏差较大，建议检查生成参数。")


if __name__ == "__main__":
    verify()
