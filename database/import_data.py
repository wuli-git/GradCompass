"""
数据导入脚本
将清洗后的CSV文件导入SQLite数据库
"""

import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
DB_PATH = BASE_DIR / "database" / "xmu_graduate.db"
SQL_PATH = BASE_DIR / "database" / "create_tables.sql"


def create_database():
    """执行建表SQL"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    with open(SQL_PATH, "r", encoding="utf-8") as f:
        sql_script = f.read()
    cursor.executescript(sql_script)
    conn.commit()
    print("数据库表结构创建完成")
    return conn


def import_csv_to_db(conn):
    """将CSV数据导入SQLite各个表"""
    file_table_map = {
        "students.csv":                "students",
        "academic_records.csv":        "academic_records",
        "employment.csv":              "employment",
        "postgraduate_exam.csv":       "postgraduate_exam",
        "postgraduate_recommend.csv":  "postgraduate_recommend",
        "study_abroad.csv":            "study_abroad",
        "colleges.csv":                "colleges",
    }

    for csv_file, table_name in file_table_map.items():
        csv_path = DATA_DIR / csv_file
        if not csv_path.exists():
            print(f"警告: {csv_file} 不存在，跳过")
            continue
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"导入 {table_name}: {len(df)} 条记录")


def verify_data(conn):
    """验证数据导入"""
    cursor = conn.cursor()
    queries = {
        "学生总数": "SELECT COUNT(*) FROM students",
        "各学历人数": "SELECT degree_level, COUNT(*) FROM students GROUP BY degree_level",
        "各去向分布": "SELECT destination, COUNT(*) FROM students GROUP BY destination",
        "就业平均薪资": "SELECT AVG(monthly_salary) FROM employment",
        "考研上岸率": """
            SELECT
              ROUND(SUM(CASE WHEN is_admitted=1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1)
              FROM postgraduate_exam
        """,
        "保本校比例": """
            SELECT
              ROUND(SUM(CASE WHEN is_xmu_internal=1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1)
              FROM postgraduate_recommend
        """,
        "留学主要国家TOP5": """
            SELECT target_country, COUNT(*) as cnt
            FROM study_abroad GROUP BY target_country
            ORDER BY cnt DESC LIMIT 5
        """,
        "就业行业TOP5": """
            SELECT industry, COUNT(*) as cnt
            FROM employment GROUP BY industry
            ORDER BY cnt DESC LIMIT 5
        """,
    }

    print("\n" + "=" * 60)
    print("数据验证结果:")
    for name, sql in queries.items():
        result = cursor.execute(sql).fetchall()
        print(f"\n[{name}]")
        for row in result:
            print(f"  {row}")


def main():
    # 检查 CSV 是否已生成
    students_csv = DATA_DIR / "students.csv"
    if not students_csv.exists():
        print("错误: 未找到数据文件，请先运行 data/synthetic_data_gen.py")
        return

    print("=" * 60)
    print("厦门大学毕业生去向数据导入")
    print("=" * 60)

    print("\n1. 创建数据库结构...")
    conn = create_database()

    print("\n2. 导入CSV数据...")
    import_csv_to_db(conn)
    conn.commit()

    print("\n3. 验证数据...")
    verify_data(conn)

    conn.close()
    print(f"\n数据库文件: {DB_PATH}")
    print("导入完成!")


if __name__ == "__main__":
    main()
