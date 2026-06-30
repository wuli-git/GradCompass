"""全流程集成测试"""
import sqlite3
import sys

DB_PATH = "database/xmu_graduate.db"

def test():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. 总人数
    cur.execute("SELECT COUNT(*) FROM students")
    total = cur.fetchone()[0]
    print(f"[1] 学生总数: {total}")
    assert total == 22500, f"Expected 22500, got {total}"

    # 2. 各学历人数
    cur.execute("SELECT degree_level, COUNT(*) FROM students GROUP BY degree_level")
    rows = cur.fetchall()
    print(f"[2] 各学历人数: {rows}")
    counts = {r[0]: r[1] for r in rows}
    assert counts["本科"] == 10500
    assert counts["硕士"] == 10500
    assert counts["博士"] == 1500

    # 3. 本科升学率
    cur.execute("""
        SELECT ROUND(SUM(CASE WHEN destination IN ('考研','保研','留学')
            THEN 1 ELSE 0 END)*100.0/COUNT(*),1)
        FROM students WHERE degree_level='本科'
    """)
    rate = cur.fetchone()[0]
    print(f"[3] 本科升学率: {rate}% (官方: 58.2%)")
    assert 53 < rate < 64, f"Rate {rate}% out of range"

    # 4. 各学历平均月薪
    cur.execute("""
        SELECT s.degree_level, ROUND(AVG(e.monthly_salary),0), COUNT(*)
        FROM employment e
        JOIN students s ON e.student_id = s.student_id
        GROUP BY s.degree_level
    """)
    rows = cur.fetchall()
    print(f"[4] 各学历平均月薪: {rows}")
    for r in rows:
        deg, sal, cnt = r
        if deg == "本科":
            assert 8000 < sal < 16000, f"UG salary {sal} out of range"
        elif deg == "硕士":
            assert 12000 < sal < 25000, f"MS salary {sal} out of range"

    # 5. 就业表记录数
    cur.execute("SELECT COUNT(*) FROM employment")
    emp_cnt = cur.fetchone()[0]
    print(f"[5] 就业记录数: {emp_cnt}")
    assert emp_cnt > 10000

    # 6. 考研上岸率
    cur.execute("""SELECT ROUND(AVG(is_admitted)*100,1) FROM postgraduate_exam""")
    admit_rate = cur.fetchone()[0]
    print(f"[6] 考研上岸率: {admit_rate}%")
    assert 30 < admit_rate < 70

    # 7. 保本校比例
    cur.execute("""SELECT ROUND(SUM(CASE WHEN is_xmu_internal=1 THEN 1 ELSE 0 END)*100.0/COUNT(*),1) FROM postgraduate_recommend""")
    internal_rate = cur.fetchone()[0]
    print(f"[7] 保本校比例: {internal_rate}%")
    assert internal_rate > 40

    # 8. 留学国家TOP 3
    cur.execute("""SELECT target_country, COUNT(*) FROM study_abroad GROUP BY target_country ORDER BY COUNT(*) DESC LIMIT 3""")
    top_countries = cur.fetchall()
    print(f"[8] 留学国家TOP3: {top_countries}")

    # 9. 就业行业TOP 3
    cur.execute("""SELECT industry, COUNT(*) FROM employment GROUP BY industry ORDER BY COUNT(*) DESC LIMIT 3""")
    top_industries = cur.fetchall()
    print(f"[9] 就业行业TOP3: {top_industries}")

    # 10. 7张表都存在
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    expected_tables = [
        "academic_records", "colleges", "employment",
        "postgraduate_exam", "postgraduate_recommend",
        "students", "study_abroad"
    ]
    print(f"[10] 数据库表: {tables}")
    for t in expected_tables:
        assert t in tables, f"Table {t} missing"

    conn.close()
    print("\n" + "=" * 50)
    print("ALL 10 TESTS PASSED")
    print("=" * 50)


if __name__ == "__main__":
    test()
