"""
厦门大学毕业生去向仿真数据生成脚本
基于 XMU 2024届毕业生就业质量年度报告 统计数据作为约束条件
数据来源: https://gk.xmu.edu.cn/xxgkml/jxzlxx/gxbysjyzlndbg.htm

生成约22,500条学生记录 (2022-2024三届，每届约7,500人)
"""

import numpy as np
import pandas as pd
from faker import Faker
import random
from pathlib import Path

np.random.seed(42)
random.seed(42)
fake = Faker("zh_CN")
Faker.seed(42)

OUTPUT_DIR = Path(__file__).parent / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 常量定义 —— 厦门大学专属
# ============================================================

XMU_COLLEGES = {
    "信息学院":        {"type": "理工", "campus": "翔安", "abbr": "信息"},
    "电子科学与技术学院": {"type": "理工", "campus": "翔安", "abbr": "电子"},
    "航空航天学院":     {"type": "理工", "campus": "翔安", "abbr": "航院"},
    "数学科学学院":     {"type": "理工", "campus": "思明", "abbr": "数学"},
    "化学化工学院":     {"type": "理工", "campus": "思明", "abbr": "化院"},
    "材料学院":        {"type": "理工", "campus": "思明", "abbr": "材料"},
    "生命科学学院":     {"type": "理工", "campus": "翔安", "abbr": "生科"},
    "海洋与地球学院":   {"type": "理工", "campus": "翔安", "abbr": "海洋"},
    "环境与生态学院":   {"type": "理工", "campus": "翔安", "abbr": "环生"},
    "能源学院":        {"type": "理工", "campus": "翔安", "abbr": "能源"},
    "建筑与土木工程学院": {"type": "理工", "campus": "思明", "abbr": "建筑"},
    "经济学院":        {"type": "经管", "campus": "思明", "abbr": "经院"},
    "管理学院":        {"type": "经管", "campus": "思明", "abbr": "管院"},
    "王亚南经济研究院":  {"type": "经管", "campus": "思明", "abbr": "WISE"},
    "财务管理与会计研究院": {"type": "经管", "campus": "思明", "abbr": "财会院"},
    "法学院":          {"type": "人文", "campus": "思明", "abbr": "法学"},
    "外文学院":        {"type": "人文", "campus": "思明", "abbr": "外文"},
    "人文学院":        {"type": "人文", "campus": "思明", "abbr": "人文"},
    "新闻传播学院":     {"type": "人文", "campus": "思明", "abbr": "新传"},
    "公共事务学院":     {"type": "人文", "campus": "思明", "abbr": "公事"},
    "国际关系学院":     {"type": "人文", "campus": "思明", "abbr": "国关"},
    "马克思主义学院":   {"type": "人文", "campus": "思明", "abbr": "马院"},
    "南洋研究院":      {"type": "人文", "campus": "思明", "abbr": "南洋"},
    "教育研究院":      {"type": "人文", "campus": "思明", "abbr": "教研院"},
    "艺术学院":        {"type": "艺术", "campus": "思明", "abbr": "艺术"},
    "医学院":          {"type": "医学", "campus": "翔安", "abbr": "医学"},
    "药学院":          {"type": "医学", "campus": "翔安", "abbr": "药学"},
    "公共卫生学院":     {"type": "医学", "campus": "翔安", "abbr": "公卫"},
    "物理科学与技术学院": {"type": "理工", "campus": "思明", "abbr": "物理"},
}

XMU_MAJORS = {
    "信息学院":        ["计算机科学与技术", "软件工程", "人工智能", "网络空间安全", "通信工程"],
    "电子科学与技术学院": ["电子信息工程", "电子科学与技术", "微电子科学与工程", "集成电路设计"],
    "航空航天学院":     ["飞行器设计与工程", "自动化", "机械工程", "测控技术与仪器"],
    "数学科学学院":     ["数学与应用数学", "信息与计算科学", "统计学"],
    "化学化工学院":     ["化学", "化学工程与工艺", "应用化学", "能源化学"],
    "材料学院":        ["材料科学与工程", "高分子材料与工程"],
    "生命科学学院":     ["生物科学", "生物技术", "生物信息学"],
    "海洋与地球学院":   ["海洋科学", "海洋技术"],
    "环境与生态学院":   ["环境科学", "环境工程", "生态学"],
    "能源学院":        ["新能源科学与工程", "核工程与核技术"],
    "建筑与土木工程学院": ["建筑学", "土木工程", "城乡规划"],
    "经济学院":        ["经济学", "金融学", "国际贸易", "财政学", "经济统计学"],
    "管理学院":        ["工商管理", "会计学", "旅游管理", "市场营销", "人力资源管理"],
    "王亚南经济研究院":  ["数量经济学", "金融学(学硕)"],
    "财务管理与会计研究院": ["财务管理", "会计学(硕博)"],
    "法学院":          ["法学", "知识产权法", "国际法"],
    "外文学院":        ["英语", "日语", "法语", "德语", "俄语"],
    "人文学院":        ["汉语言文学", "历史学", "哲学", "考古学"],
    "新闻传播学院":     ["新闻学", "广告学", "传播学", "广播电视学"],
    "公共事务学院":     ["公共管理", "政治学", "社会学"],
    "国际关系学院":     ["国际政治", "外交学"],
    "马克思主义学院":   ["马克思主义理论", "思想政治教育"],
    "南洋研究院":      ["国际关系", "世界经济"],
    "教育研究院":      ["教育学", "高等教育学"],
    "艺术学院":        ["音乐学", "美术学", "设计学"],
    "医学院":          ["临床医学", "基础医学", "护理学"],
    "药学院":          ["药学", "制药工程"],
    "公共卫生学院":     ["预防医学", "公共卫生"],
    "物理科学与技术学院": ["物理学", "应用物理学", "光电信息科学与工程"],
}

# 重点用人单位 (来自XMU 2024就业报告)
TOP_EMPLOYERS = [
    ("华为技术有限公司",         "民企", "IT/互联网",  143),
    ("比亚迪股份有限公司",       "民企", "制造业",     75),
    ("宁德时代新能源科技",       "民企", "制造业",     74),
    ("中国建筑集团有限公司",     "国企", "建筑",       69),
    ("国家电网有限公司",        "国企", "能源",       52),
    ("腾讯科技有限公司",        "民企", "IT/互联网",  45),
    ("招商银行股份有限公司",     "国企", "金融",       40),
    ("中国农业银行",           "国企", "金融",       40),
    ("中国移动通信集团",        "国企", "通信",       38),
    ("中国电信集团有限公司",     "国企", "通信",       34),
    ("中国烟草总公司",         "国企", "烟草",       33),
    ("兴业银行股份有限公司",     "国企", "金融",       29),
    ("阿里巴巴集团",           "民企", "IT/互联网",  25),
    ("字节跳动有限公司",        "民企", "IT/互联网",  22),
    ("小米科技有限责任公司",     "民企", "IT/互联网",  21),
    ("美团",                 "民企", "IT/互联网",  19),
    ("中国建设银行",           "国企", "金融",       35),
    ("中国工商银行",           "国企", "金融",       32),
    ("厦门大学",              "高校科研", "教育",    30),
    ("中国科学院",            "高校科研", "科研",    28),
    ("中建三局",              "国企", "建筑",       25),
    ("南方电网",              "国企", "能源",       22),
    ("宝洁(中国)",            "外企", "快消",       18),
    ("普华永道",              "外企", "咨询",       15),
    ("德勤",                "外企", "咨询",       14),
    ("安永",                "外企", "咨询",       12),
    ("毕马威",               "外企", "咨询",       10),
]

EMPLOYERS = [e[:3] for e in TOP_EMPLOYERS]
EMPLOYER_WEIGHTS = [e[3] for e in TOP_EMPLOYERS]
COMPANY_TYPES = ["国企", "民企", "外企", "机关事业", "高校科研"]
INDUSTRIES = {
    "IT/互联网": ["北京", "上海", "深圳", "杭州", "广州", "成都"],
    "金融":      ["北京", "上海", "深圳", "广州", "厦门"],
    "教育":      ["厦门", "福州", "泉州", "北京", "上海", "广州", "深圳"],
    "制造业":    ["深圳", "上海", "苏州", "东莞", "宁德", "武汉"],
    "建筑":      ["北京", "上海", "广州", "深圳", "武汉", "成都"],
    "能源":      ["北京", "上海", "广州", "深圳", "福州"],
    "通信":      ["北京", "上海", "深圳", "广州", "福州"],
    "政府":      ["厦门", "福州", "泉州", "漳州", "北京"],
    "医疗":      ["厦门", "福州", "上海", "北京", "广州"],
    "咨询":      ["上海", "北京", "深圳", "广州"],
    "快消":      ["上海", "广州", "北京", "深圳"],
    "烟草":      ["厦门", "福州", "昆明", "北京"],
    "科研":      ["北京", "上海", "厦门", "合肥", "南京"],
}

DOMESTIC_TOP_UNIVERSITIES = [
    ("厦门大学", "985"), ("复旦大学", "985"), ("北京大学", "985"),
    ("上海交通大学", "985"), ("清华大学", "985"), ("浙江大学", "985"),
    ("南京大学", "985"), ("中国人民大学", "985"), ("中山大学", "985"),
    ("武汉大学", "985"), ("华中科技大学", "985"), ("中国科学技术大学", "985"),
    ("同济大学", "985"), ("北京航空航天大学", "985"), ("南开大学", "985"),
    ("中国科学院大学", "双一流"), ("上海财经大学", "211"), ("中央财经大学", "211"),
    ("对外经济贸易大学", "211"), ("北京邮电大学", "211"), ("华东政法大学", "其他"),
]

ABROAD_UNIVERSITIES = [
    ("香港中文大学", "中国香港", 36), ("香港大学", "中国香港", 26),
    ("香港城市大学", "中国香港", 54), ("新加坡国立大学", "新加坡", 8),
    ("南洋理工大学", "新加坡", 26), ("伦敦大学学院", "英国", 9),
    ("悉尼大学", "澳大利亚", 41), ("墨尔本大学", "澳大利亚", 33),
    ("帝国理工学院", "英国", 6), ("爱丁堡大学", "英国", 22),
    ("曼彻斯特大学", "英国", 28), ("哥伦比亚大学", "美国", 22),
    ("纽约大学", "美国", 35), ("约翰霍普金斯大学", "美国", 24),
    ("卡内基梅隆大学", "美国", 52), ("东京大学", "日本", 28),
    ("京都大学", "日本", 46), ("慕尼黑工业大学", "德国", 38),
    ("苏黎世联邦理工学院", "瑞士", 7), ("多伦多大学", "加拿大", 21),
    ("首尔国立大学", "韩国", 36), ("阿姆斯特丹大学", "荷兰", 58),
]

PROVINCES = [
    "福建", "广东", "浙江", "江苏", "上海", "北京", "山东", "湖北",
    "湖南", "四川", "河南", "河北", "安徽", "江西", "重庆", "辽宁",
    "陕西", "山西", "云南", "贵州", "广西", "甘肃", "吉林", "黑龙江",
    "海南", "内蒙古", "新疆", "西藏", "青海", "宁夏", "天津",
]
PROVINCE_WEIGHTS = [
    18, 8, 7, 5, 3, 3, 4, 3, 3, 3, 4, 3, 3, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
    1, 1, 1, 1, 1, 1, 1
]

# ============================================================
# 统计约束条件 (来自XMU 2024届就业质量报告)
# ============================================================
UNDERGRAD_CONSTRAINTS = {
    "升学率": 0.582,
    "保研率": 0.25,
    "考研成功率": 0.35,
    "留学率": 0.13,
    "就业率": 0.29,
    "其他率": 0.128,
    "avg_gpa": 3.2, "gpa_std": 0.45,
    "avg_salary": 10200, "salary_std": 3500,
}

MASTER_CONSTRAINTS = {
    "就业率": 0.75,
    "升学率": 0.08,
    "留学率": 0.04,
    "其他率": 0.13,
    "avg_gpa": 3.45, "gpa_std": 0.35,
    "avg_salary": 14800, "salary_std": 5000,
}

PHD_CONSTRAINTS = {
    "就业率": 0.85,
    "升学率": 0.0,
    "留学率": 0.0,
    "其他率": 0.15,
    "avg_gpa": 3.7, "gpa_std": 0.25,
    "avg_salary": 22000, "salary_std": 6000,
}

# ============================================================
# 数据生成逻辑
# ============================================================

def generate_colleges_df():
    """生成学院字典表"""
    rows = []
    for i, (name, info) in enumerate(XMU_COLLEGES.items(), 1):
        rows.append({
            "college_id": i,
            "college_name": name,
            "college_type": info["type"],
            "campus": info["campus"],
            "abbreviation": info["abbr"],
        })
    return pd.DataFrame(rows)


def assign_college_major(degree_level="本科"):
    """分配学院和专业（本硕博专业分布略有差异）"""
    colleges = list(XMU_COLLEGES.keys())
    if degree_level == "本科":
        weights = [5, 3, 2, 3, 5, 2, 3, 2, 2, 1, 2, 8, 7, 2, 2, 4, 4, 3, 3, 3, 2, 2, 1, 1, 2, 3, 2, 2, 3]
    elif degree_level == "硕士":
        weights = [6, 3, 3, 3, 5, 3, 3, 2, 2, 1, 2, 8, 7, 3, 2, 3, 3, 3, 3, 3, 2, 2, 1, 1, 2, 4, 2, 2, 3]
    else:
        weights = [4, 2, 2, 2, 6, 2, 4, 3, 2, 1, 1, 5, 4, 3, 1, 2, 1, 3, 1, 2, 1, 1, 1, 1, 1, 5, 2, 2, 3]
    weights = weights[:len(colleges)]
    w_sum = sum(weights)
    weights = [w / w_sum for w in weights]
    college = np.random.choice(colleges, p=weights)
    major = np.random.choice(XMU_MAJORS[college])
    return college, major, XMU_COLLEGES[college]["campus"]


def assign_destination(degree, gpa_rank_pct):
    """根据学历和成绩排名分配毕业去向"""
    if degree == "本科":
        c = UNDERGRAD_CONSTRAINTS
        rand = np.random.random()
        prob_baoyan = c["保研率"] * (1.5 if gpa_rank_pct < 20 else 1.0 if gpa_rank_pct < 40 else 0.3 if gpa_rank_pct < 60 else 0.05)
        prob_liuxue = c["留学率"] * (1.3 if gpa_rank_pct < 40 else 1.0 if gpa_rank_pct < 70 else 0.5)
        prob_kaoyan = (1 - c["就业率"] - c["其他率"]) - prob_baoyan - prob_liuxue
        prob_jiuye = c["就业率"]
        prob_other = c["其他率"]

        # 归一化
        total = prob_baoyan + prob_liuxue + prob_kaoyan + prob_jiuye + prob_other
        dests = ["保研", "留学", "考研", "就业", "其他"]
        probs = [prob_baoyan / total, prob_liuxue / total, prob_kaoyan / total, prob_jiuye / total, prob_other / total]
    elif degree == "硕士":
        c = MASTER_CONSTRAINTS
        prob_zhibo = 0.04          # 硕博连读/直博
        prob_liuxue = c["留学率"]
        prob_kaobo = 0.04          # 考博
        prob_jiuye = c["就业率"]
        prob_other = c["其他率"]
        total = prob_zhibo + prob_liuxue + prob_kaobo + prob_jiuye + prob_other
        dests = ["直博/硕博连读", "留学", "考博", "就业", "其他"]
        probs = [prob_zhibo / total, prob_liuxue / total, prob_kaobo / total, prob_jiuye / total, prob_other / total]
    else:
        c = PHD_CONSTRAINTS
        prob_jiuye = c["就业率"]
        prob_other = c["其他率"]
        total = prob_jiuye + prob_other
        dests = ["就业", "其他"]
        probs = [prob_jiuye / total, prob_other / total]

    return np.random.choice(dests, p=probs)


def generate_gpa(degree):
    """生成GPA"""
    if degree == "本科":
        avg, std = UNDERGRAD_CONSTRAINTS["avg_gpa"], UNDERGRAD_CONSTRAINTS["gpa_std"]
    elif degree == "硕士":
        avg, std = MASTER_CONSTRAINTS["avg_gpa"], MASTER_CONSTRAINTS["gpa_std"]
    else:
        avg, std = PHD_CONSTRAINTS["avg_gpa"], PHD_CONSTRAINTS["gpa_std"]
    return round(np.clip(np.random.normal(avg, std), 1.5, 4.0), 2)


def generate_students(n_undergrad=3500, n_master=3500, n_phd=500, year=2024):
    """生成一届学生数据"""
    records = []
    student_id_start = year * 100000

    for degree, n in [("本科", n_undergrad), ("硕士", n_master), ("博士", n_phd)]:
        for i in range(n):
            sid = student_id_start + len(records) + 1
            gender = np.random.choice(["男", "女"], p=[0.474, 0.526])
            age = {"本科": 22, "硕士": 25, "博士": 28}[degree] + np.random.choice([-1, 0, 1, 2])
            college, major, campus = assign_college_major(degree)
            province = np.random.choice(PROVINCES, p=[w / sum(PROVINCE_WEIGHTS) for w in PROVINCE_WEIGHTS])
            city = fake.city_name() if province != "福建" else np.random.choice(["厦门", "福州", "泉州", "漳州", "龙岩", "三明", "南平", "莆田", "宁德"])
            gpa = generate_gpa(degree)
            gpa_rank_pct = np.clip(np.random.normal(50, 28), 1, 99)
            destination = assign_destination(degree, gpa_rank_pct)

            records.append({
                "student_id": sid, "gender": gender, "age": age,
                "home_province": province, "home_city": city,
                "campus": campus, "college": college, "major_name": major,
                "degree_level": degree, "graduation_year": year,
                "destination": destination, "is_xmu_undergrad": 1,
            })

    return pd.DataFrame(records)


def generate_academic_records(students_df):
    """生成学业表现数据"""
    records = []
    for _, s in students_df.iterrows():
        gpa = generate_gpa(s["degree_level"]) if s["degree_level"] != "本科" else np.round(np.clip(
            np.random.normal(UNDERGRAD_CONSTRAINTS["avg_gpa"], UNDERGRAD_CONSTRAINTS["gpa_std"]), 1.5, 4.0), 2)

        gpa_rank_pct = round(100 - (gpa - 1.5) / 2.5 * 100 + np.random.normal(0, 8), 1)
        gpa_rank_pct = np.clip(gpa_rank_pct, 1, 99)

        cet4 = int(np.clip(np.random.normal(500, 60), 300, 700)) if s["degree_level"] == "本科" else int(np.clip(np.random.normal(520, 50), 350, 700))
        cet6 = int(np.clip(np.random.normal(470, 65), 300, 700)) if s["degree_level"] != "博士" else int(np.clip(np.random.normal(490, 55), 350, 700))

        has_paper = np.random.random() < (0.05 if s["degree_level"] == "本科" else 0.4 if s["degree_level"] == "硕士" else 0.85)
        paper_level = None
        if has_paper:
            paper_level = np.random.choice(["SCI", "EI", "核心", "普刊"], p=[0.15, 0.2, 0.35, 0.3])
        has_competition = np.random.random() < (0.25 if s["degree_level"] == "本科" else 0.2)
        has_internship = np.random.random() < (0.5 if s["degree_level"] == "本科" else 0.7 if s["degree_level"] == "硕士" else 0.3)
        internship_count = int(np.clip(np.random.poisson(1), 0, 5)) if has_internship else 0
        volunteer_hours = int(np.clip(np.random.exponential(40), 0, 300))

        # 根据去向调整：保研/留学学生通常GPA更高
        if s["destination"] in ["保研", "留学"]:
            gpa = round(np.clip(gpa + np.random.uniform(0.1, 0.5), 2.5, 4.0), 2)
            gpa_rank_pct = round(np.clip(gpa_rank_pct - np.random.uniform(10, 25), 1, 99), 1)
        elif s["destination"] == "考研":
            cet6 = int(np.clip(cet6 + np.random.randint(-10, 30), 350, 700))

        records.append({
            "record_id": len(records) + 1,
            "student_id": s["student_id"],
            "gpa": gpa, "gpa_rank_pct": gpa_rank_pct,
            "cet4_score": cet4, "cet6_score": cet6,
            "has_paper": int(has_paper), "paper_level": paper_level,
            "has_competition": int(has_competition), "has_internship": int(has_internship),
            "internship_count": internship_count, "volunteer_hours": volunteer_hours,
        })
    return pd.DataFrame(records)


def generate_employment(students_df):
    """生成就业去向数据"""
    employed = students_df[students_df["destination"] == "就业"]
    records = []
    for _, s in employed.iterrows():
        if np.random.random() < 0.3:
            emp = EMPLOYERS[np.random.choice(len(EMPLOYERS), p=[w / sum(EMPLOYER_WEIGHTS) for w in EMPLOYER_WEIGHTS])]
            company_name, company_type, industry = emp
        else:
            industry = np.random.choice(list(INDUSTRIES.keys()))
            company_type = np.random.choice(COMPANY_TYPES, p=[0.24, 0.30, 0.08, 0.20, 0.18])
            company_name = fake.company()

        city_choices = INDUSTRIES.get(industry, ["厦门", "福州"])
        job_city = np.random.choice(city_choices)
        province_map = {"北京": "北京", "上海": "上海", "深圳": "广东", "广州": "广东",
                        "杭州": "浙江", "成都": "四川", "厦门": "福建", "福州": "福建",
                        "泉州": "福建", "苏州": "江苏", "东莞": "广东", "宁德": "福建",
                        "武汉": "湖北", "合肥": "安徽", "南京": "江苏", "昆明": "云南"}
        job_province = province_map.get(job_city, job_city)

        is_first_tier = int(job_city in ["北京", "上海", "广州", "深圳"])

        if s["degree_level"] == "本科":
            salary = np.clip(np.random.lognormal(np.log(10200), 0.3), 4000, 30000)
        elif s["degree_level"] == "硕士":
            salary = np.clip(np.random.lognormal(np.log(14800), 0.3), 6000, 45000)
        else:
            salary = np.clip(np.random.lognormal(np.log(22000), 0.25), 10000, 60000)

        # 一线城市上浮
        if is_first_tier:
            salary *= np.random.uniform(1.1, 1.5)
        salary = round(salary, 2)

        records.append({
            "employment_id": len(records) + 1,
            "student_id": s["student_id"],
            "company_name": company_name, "company_type": company_type,
            "industry": industry, "job_city": job_city, "job_province": job_province,
            "is_first_tier": is_first_tier, "monthly_salary": salary,
            "annual_salary": round(salary * (13 + np.random.choice([0, 1, 2, 3])), 2),
            "signing_bonus": round(np.random.choice([0, 0, 0, 5000, 10000, 20000, 30000]), 2),
            "job_satisfaction": int(np.clip(np.random.normal(3.5, 0.8), 1, 5)),
            "is_major_match": int(np.random.random() < 0.65),
            "offer_count": int(np.clip(np.random.poisson(2), 1, 8)),
        })
    return pd.DataFrame(records)


def generate_postgraduate_exam(students_df):
    """生成考研/考博数据"""
    exam_students = students_df[students_df["destination"].isin(["考研", "考博"])]
    records = []
    for _, s in exam_students.iterrows():
        target = DOMESTIC_TOP_UNIVERSITIES[np.random.choice(len(DOMESTIC_TOP_UNIVERSITIES))]
        target_uni, target_tier = target

        is_cross_col = int(np.random.random() < 0.35)
        is_cross_major = int(np.random.random() < 0.25)

        # 总分 500分制（考研）/ 300分制或500分制（考博，这里统一用500分制简化）
        if s["destination"] == "考博":
            # 博士入学考试通常更注重专业课
            base_score = np.random.normal(340, 40)
        else:
            base_score = np.random.normal(355, 45)
        if s["degree_level"] == "硕士":
            base_score = np.random.normal(340, 40)
        total = int(np.clip(base_score, 200, 450))
        politics = int(np.clip(np.random.normal(68, 10), 35, 95))
        english = int(np.clip(np.random.normal(65, 12), 30, 95))
        math = int(np.clip(np.random.normal(110, 25), 40, 148)) if np.random.random() < 0.7 else None
        major_course = int(np.clip(total - politics - english - (math or 0), 50, 148))

        # 上岸率
        if s["destination"] == "考博":
            admit_prob = 0.40  # 博士录取率略高
        elif s["degree_level"] == "本科":
            admit_prob = 0.35
        else:
            admit_prob = 0.40
        is_admitted = int(np.random.random() < admit_prob)
        is_transfer = int(not is_admitted and np.random.random() < 0.3)
        if is_transfer:
            is_admitted = 1

        records.append({
            "exam_id": len(records) + 1,
            "student_id": s["student_id"],
            "target_university": target_uni, "target_college": fake.company()[:20] + "学院",
            "target_major": np.random.choice(list(XMU_MAJORS.values())[0]),
            "target_tier": target_tier,
            "is_cross_college": is_cross_col, "is_cross_major": is_cross_major,
            "exam_total_score": total, "exam_politics": politics,
            "exam_english": english, "exam_math": math,
            "exam_major_course": major_course,
            "is_admitted": is_admitted, "is_first_choice": int(is_admitted and np.random.random() < 0.7),
            "is_transfer": is_transfer,
            "prep_months": int(np.clip(np.random.normal(8, 3), 2, 18)),
        })
    return pd.DataFrame(records)


def generate_postgraduate_recommend(students_df):
    """生成保研/硕博连读数据"""
    recommend_students = students_df[students_df["destination"].isin(["保研", "直博/硕博连读"])]
    records = []
    for _, s in recommend_students.iterrows():
        is_internal = int(np.random.random() < (0.55 if s["degree_level"] == "本科" else 0.7))

        if is_internal:
            target_uni, target_tier = "厦门大学", "985"
        else:
            target = DOMESTIC_TOP_UNIVERSITIES[np.random.choice(len(DOMESTIC_TOP_UNIVERSITIES))]
            target_uni, target_tier = target

        if s["destination"] == "直博/硕博连读":
            recommend_type = np.random.choice(
                ["硕博连读", "申请考核", "导师推荐"],
                p=[0.55, 0.30, 0.15]
            )
        else:
            recommend_type = np.random.choice(
                ["成绩保研", "竞赛保研", "学术专长", "支教保研", "辅导员保研"],
                p=[0.65, 0.12, 0.10, 0.08, 0.05]
            )

        records.append({
            "recommend_id": len(records) + 1,
            "student_id": s["student_id"],
            "target_university": target_uni, "target_college": np.random.choice(list(XMU_COLLEGES.keys())),
            "target_major": np.random.choice(list(XMU_MAJORS.values())[0]),
            "target_tier": target_tier,
            "is_cross_college": int(is_internal and np.random.random() < 0.2),
            "is_cross_major": int(np.random.random() < 0.10),
            "recommend_type": recommend_type,
            "is_accepted": 1,
            "is_xmu_internal": is_internal,
            "application_count": int(np.clip(np.random.poisson(2) + 1, 1, 6)),
        })
    return pd.DataFrame(records)


def generate_study_abroad(students_df):
    """生成留学数据"""
    abroad_students = students_df[students_df["destination"] == "留学"]
    records = []
    for _, s in abroad_students.iterrows():
        uni = ABROAD_UNIVERSITIES[np.random.choice(len(ABROAD_UNIVERSITIES))]
        uni_name, country, qs = uni

        toefl = int(np.clip(np.random.normal(100, 10), 70, 120))
        ielts = round(np.clip(np.random.normal(7.0, 0.7), 5.5, 9.0), 1)
        gre = int(np.clip(np.random.normal(322, 10), 295, 340)) if np.random.random() < 0.6 else None
        has_scholarship = int(np.random.random() < 0.2)

        records.append({
            "abroad_id": len(records) + 1,
            "student_id": s["student_id"],
            "target_country": country, "target_university": uni_name,
            "target_major": np.random.choice(list(XMU_MAJORS.values())[0]),
            "qs_rank": qs + np.random.randint(-5, 10),
            "has_scholarship": has_scholarship,
            "scholarship_type": np.random.choice(["全奖", "半奖", "CSC"]) if has_scholarship else None,
            "scholarship_amount": round(np.random.uniform(10000, 55000), 2) if has_scholarship else 0,
            "ielts_score": ielts, "toefl_score": toefl,
            "gre_score": gre, "gmat_score": int(np.clip(np.random.normal(680, 50), 500, 800)) if np.random.random() < 0.25 else None,
            "offer_count": int(np.clip(np.random.poisson(2), 1, 8)),
            "agent_used": int(np.random.random() < 0.55),
        })
    return pd.DataFrame(records)


# ============================================================
# 主流程
# ============================================================

def main():
    print("=" * 60)
    print("厦门大学毕业生去向仿真数据生成")
    print("数据约束来源: XMU 2024届毕业生就业质量年度报告")
    print("=" * 60)

    all_students = []
    years = [2022, 2023, 2024]

    for year in years:
        print(f"\n生成 {year} 届数据...")
        df_stu = generate_students(n_undergrad=3500, n_master=3500, n_phd=500, year=year)
        all_students.append(df_stu)
        print(f"  -> 学生: {len(df_stu)} 条 (本科{len(df_stu[df_stu.degree_level=='本科'])} 硕士{len(df_stu[df_stu.degree_level=='硕士'])} 博士{len(df_stu[df_stu.degree_level=='博士'])})")

    students_df = pd.concat(all_students, ignore_index=True)
    students_df["student_id"] = range(1, len(students_df) + 1)

    # 生成各维度数据
    print("\n生成学业记录...")
    academic_df = generate_academic_records(students_df)

    print("生成就业数据...")
    employment_df = generate_employment(students_df)

    print("生成考研数据...")
    exam_df = generate_postgraduate_exam(students_df)

    print("生成保研数据...")
    recommend_df = generate_postgraduate_recommend(students_df)

    print("生成留学数据...")
    abroad_df = generate_study_abroad(students_df)

    print("生成学院字典...")
    colleges_df = generate_colleges_df()

    # 保存
    print("\n保存CSV文件...")
    students_df.to_csv(OUTPUT_DIR / "students.csv", index=False, encoding="utf-8-sig")
    academic_df.to_csv(OUTPUT_DIR / "academic_records.csv", index=False, encoding="utf-8-sig")
    employment_df.to_csv(OUTPUT_DIR / "employment.csv", index=False, encoding="utf-8-sig")
    exam_df.to_csv(OUTPUT_DIR / "postgraduate_exam.csv", index=False, encoding="utf-8-sig")
    recommend_df.to_csv(OUTPUT_DIR / "postgraduate_recommend.csv", index=False, encoding="utf-8-sig")
    abroad_df.to_csv(OUTPUT_DIR / "study_abroad.csv", index=False, encoding="utf-8-sig")
    colleges_df.to_csv(OUTPUT_DIR / "colleges.csv", index=False, encoding="utf-8-sig")

    # 统计摘要
    print("\n" + "=" * 60)
    print("数据生成完成! 统计摘要:")
    print(f"  总学生记录:    {len(students_df)}")
    for dest in ["就业", "考研", "保研", "留学", "考博", "直博/硕博连读", "其他"]:
        cnt = len(students_df[students_df.destination == dest])
        print(f"  - {dest}: {cnt} ({cnt / len(students_df) * 100:.1f}%)")
    print(f"  就业记录:      {len(employment_df)}")
    print(f"  考研记录:      {len(exam_df)}")
    print(f"  保研记录:      {len(recommend_df)}")
    print(f"  留学记录:      {len(abroad_df)}")
    print(f"\n数据保存在: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
