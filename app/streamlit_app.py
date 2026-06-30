"""
厦门大学毕业生去向数据分析智能体 — Streamlit 主应用
"""

import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(
    page_title="厦大毕业生去向分析智能体",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = str(Path(__file__).parent.parent / "database" / "xmu_graduate.db")

# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.title("🎓 厦大毕业生去向分析")
    st.caption("Database System Principles — Final Project")
    st.divider()

    page = st.radio(
        "导航",
        ["📊 数据概览", "💼 就业分析", "📝 考研分析", "🎯 保研与留学", "🤖 AI 智能问答"],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("数据来源: XMU 2022-2024届毕业生就业质量报告")
    st.caption("厦门大学信息公开网 gk.xmu.edu.cn")

# ============================================================
# 数据库连接
# ============================================================

@st.cache_resource
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

conn = get_connection()

# ============================================================
# 通用查询函数
# ============================================================

def run_query(sql, params=None):
    try:
        if params:
            return pd.read_sql_query(sql, conn, params=params)
        return pd.read_sql_query(sql, conn)
    except Exception as e:
        st.error(f"查询失败: {e}")
        return pd.DataFrame()

# ============================================================
# 数据概览页
# ============================================================

if page == "📊 数据概览":
    st.title("📊 厦大毕业生去向数据概览")

    # 总体指标
    col1, col2, col3, col4, col5 = st.columns(5)
    total = run_query("SELECT COUNT(*) as cnt FROM students")["cnt"].iloc[0]
    col1.metric("毕业生总记录", f"{total:,}")

    baoyan_cnt = int(run_query("SELECT COUNT(*) as cnt FROM postgraduate_recommend")["cnt"].iloc[0])
    col2.metric("保研人数", f"{baoyan_cnt:,}")

    avg_salary = run_query("SELECT ROUND(AVG(monthly_salary), 0) as avg FROM employment")["avg"].iloc[0]
    col3.metric("平均月薪(元)", f"{avg_salary:,.0f}")

    employment_rate = run_query(
        "SELECT ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM students),1) as r FROM students WHERE destination='就业'"
    )["r"].iloc[0]
    col4.metric("就业比例", f"{employment_rate}%")

    further_rate = run_query(
        "SELECT ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM students),1) as r FROM students WHERE destination IN ('考研','保研','留学','考博','直博/硕博连读')"
    )["r"].iloc[0]
    col5.metric("升学比例", f"{further_rate}%")

    st.divider()

    # 去向分布
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("毕业去向分布")
        dest_df = run_query("""
            SELECT destination, COUNT(*) as cnt
            FROM students GROUP BY destination
            ORDER BY cnt DESC
        """)
        fig = px.pie(dest_df, values="cnt", names="destination",
                      color_discrete_sequence=px.colors.qualitative.Set2,
                      hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("各学历层次去向分布")
        degree_dest = run_query("""
            SELECT degree_level, destination, COUNT(*) as cnt
            FROM students
            GROUP BY degree_level, destination
            ORDER BY degree_level, cnt DESC
        """)
        fig = px.bar(degree_dest, x="degree_level", y="cnt", color="destination",
                      barmode="stack", color_discrete_sequence=px.colors.qualitative.Set2,
                      labels={"degree_level": "学历层次", "cnt": "人数", "destination": "去向"})
        st.plotly_chart(fig, use_container_width=True)

    # 年份趋势
    st.subheader("2022-2024 去向趋势")
    year_dest = run_query("""
        SELECT graduation_year, destination, COUNT(*) as cnt
        FROM students
        GROUP BY graduation_year, destination
        ORDER BY graduation_year
    """)
    fig = px.line(year_dest, x="graduation_year", y="cnt", color="destination",
                   markers=True, labels={"graduation_year": "毕业年份", "cnt": "人数", "destination": "去向"})
    st.plotly_chart(fig, use_container_width=True)

    # 学院去向
    st.subheader("各学院毕业去向分布 (Top 15)")
    college_dest = run_query("""
        SELECT college, destination, COUNT(*) as cnt
        FROM students
        GROUP BY college, destination
    """)
    college_total = college_dest.groupby("college")["cnt"].sum().nlargest(15).index
    college_dest_top = college_dest[college_dest["college"].isin(college_total)]
    fig = px.bar(college_dest_top, x="college", y="cnt", color="destination",
                  barmode="stack", labels={"college": "学院", "cnt": "人数"})
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 就业分析页
# ============================================================

elif page == "💼 就业分析":
    st.title("💼 就业分析")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("各行业平均月薪")
        industry_salary = run_query("""
            SELECT industry, ROUND(AVG(monthly_salary), 0) as avg_salary, COUNT(*) as cnt
            FROM employment
            GROUP BY industry HAVING cnt >= 10
            ORDER BY avg_salary DESC
        """)
        fig = px.bar(industry_salary, x="industry", y="avg_salary",
                      labels={"industry": "行业", "avg_salary": "平均月薪(元)"},
                      color="avg_salary", color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("主要雇主录用人数 TOP 15")
        employer = run_query("""
            SELECT company_name, COUNT(*) as cnt, ROUND(AVG(monthly_salary), 0) as avg_sal
            FROM employment
            GROUP BY company_name
            ORDER BY cnt DESC LIMIT 15
        """)
        fig = px.bar(employer, x="cnt", y="company_name", orientation="h",
                      labels={"cnt": "录用人数", "company_name": "企业"},
                      color="avg_sal", color_continuous_scale="Reds")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("一线城市 vs 非一线城市薪资")
        city_salary = run_query("""
            SELECT
              CASE WHEN is_first_tier=1 THEN '一线城市' ELSE '非一线城市' END as city_type,
              ROUND(AVG(monthly_salary), 0) as avg_salary,
              COUNT(*) as cnt
            FROM employment
            GROUP BY is_first_tier
        """)
        fig = px.bar(city_salary, x="city_type", y="avg_salary", color="city_type",
                      labels={"city_type": "城市类型", "avg_salary": "平均月薪(元)"},
                      text="avg_salary")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("单位性质分布")
        company_type = run_query("""
            SELECT company_type, COUNT(*) as cnt
            FROM employment GROUP BY company_type
            ORDER BY cnt DESC
        """)
        fig = px.pie(company_type, values="cnt", names="company_type",
                      hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("GPA与就业薪资关系")
    gpa_salary = run_query("""
        SELECT a.gpa, e.monthly_salary, s.college
        FROM academic_records a
        JOIN employment e ON a.student_id = e.student_id
        JOIN students s ON s.student_id = a.student_id
        WHERE a.gpa > 1.5 AND e.monthly_salary < 50000
        LIMIT 2000
    """)
    fig = px.scatter(gpa_salary, x="gpa", y="monthly_salary", color="college",
                      opacity=0.6, labels={"gpa": "GPA", "monthly_salary": "月薪(元)"})
    st.plotly_chart(fig, use_container_width=True)

    # 专业对口率
    st.subheader("各行业专业对口率")
    match_rate = run_query("""
        SELECT industry,
               ROUND(SUM(CASE WHEN is_major_match=1 THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) as match_rate,
               COUNT(*) as cnt
        FROM employment
        GROUP BY industry HAVING cnt >= 10
        ORDER BY match_rate DESC
    """)
    fig = px.bar(match_rate, x="industry", y="match_rate",
                  labels={"industry": "行业", "match_rate": "专业对口率(%)"},
                  color="match_rate", color_continuous_scale="Greens")
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 考研分析页
# ============================================================

elif page == "📝 考研分析":
    st.title("📝 考研分析")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("各学院考研上岸率")
        exam_college = run_query("""
            SELECT s.college,
                   ROUND(AVG(p.is_admitted)*100, 1) as admit_rate,
                   COUNT(*) as total
            FROM students s
            JOIN postgraduate_exam p ON s.student_id = p.student_id
            GROUP BY s.college HAVING total >= 15
            ORDER BY admit_rate DESC LIMIT 15
        """)
        fig = px.bar(exam_college, x="admit_rate", y="college", orientation="h",
                      labels={"admit_rate": "上岸率(%)", "college": "学院"},
                      color="admit_rate", color_continuous_scale="Greens")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("本专业 vs 跨专业考研上岸率")
        cross_rate = run_query("""
            SELECT
              CASE WHEN is_cross_major=1 THEN '跨专业' ELSE '本专业' END as type,
              ROUND(AVG(is_admitted)*100, 1) as admit_rate,
              COUNT(*) as cnt
            FROM postgraduate_exam
            GROUP BY is_cross_major
        """)
        fig = px.bar(cross_rate, x="type", y="admit_rate", color="type",
                      labels={"type": "", "admit_rate": "上岸率(%)"},
                      text="admit_rate")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("考研目标院校流向 (本科学院 -> 目标院校)")
    target_flow = run_query("""
        SELECT s.college as source_college, p.target_university,
               SUM(CASE WHEN p.is_admitted=1 THEN 1 ELSE 0 END) as admitted,
               COUNT(*) as total
        FROM students s
        JOIN postgraduate_exam p ON s.student_id = p.student_id
        GROUP BY s.college, p.target_university
        HAVING total >= 5
        ORDER BY total DESC
        LIMIT 30
    """)
    fig = px.treemap(target_flow, path=["source_college", "target_university"],
                      values="total", color="admitted",
                      color_continuous_scale="RdYlGn",
                      labels={"source_college": "本科", "target_university": "目标"})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("考研总分分布 (录取 vs 未录取)")
    score_df = run_query("""
        SELECT exam_total_score,
               CASE WHEN is_admitted=1 THEN '录取' ELSE '未录取' END as status
        FROM postgraduate_exam
        WHERE exam_total_score > 0
    """)
    fig = px.histogram(score_df, x="exam_total_score", color="status",
                        nbins=40, barmode="overlay", opacity=0.7,
                        labels={"exam_total_score": "考研总分", "count": "人数"})
    st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("备考时长 vs 考研分数")
        prep_score = run_query("""
            SELECT prep_months, exam_total_score, is_admitted
            FROM postgraduate_exam
            WHERE exam_total_score > 0 AND prep_months BETWEEN 1 AND 18
            LIMIT 2000
        """)
        fig = px.scatter(prep_score, x="prep_months", y="exam_total_score",
                          color="is_admitted", opacity=0.6,
                          labels={"prep_months": "备考时长(月)", "exam_total_score": "总分"})
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("目标院校层次分布")
        tier_df = run_query("""
            SELECT target_tier, COUNT(*) as cnt,
                   SUM(CASE WHEN is_admitted=1 THEN 1 ELSE 0 END) as admitted
            FROM postgraduate_exam
            GROUP BY target_tier
        """)
        fig = px.bar(tier_df, x="target_tier", y=["cnt", "admitted"],
                      barmode="group", labels={"target_tier": "院校层次", "value": "人数"})
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 保研与留学分析页
# ============================================================

elif page == "🎯 保研与留学":
    st.title("🎯 保研与留学分析")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("保研类型分布")
        recommend_type = run_query("""
            SELECT recommend_type, COUNT(*) as cnt
            FROM postgraduate_recommend
            GROUP BY recommend_type
            ORDER BY cnt DESC
        """)
        fig = px.pie(recommend_type, values="cnt", names="recommend_type",
                      hole=0.5, color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("本校保研 vs 外校保研")
        internal = run_query("""
            SELECT
              CASE WHEN is_xmu_internal=1 THEN '本校' ELSE '外校' END as type,
              COUNT(*) as cnt
            FROM postgraduate_recommend
            GROUP BY is_xmu_internal
        """)
        fig = px.pie(internal, values="cnt", names="type",
                      hole=0.5, color_discrete_sequence=["#1f77b4", "#ff7f0e"])
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("留学目的国家分布")
    country_df = run_query("""
        SELECT target_country, COUNT(*) as cnt,
               ROUND(AVG(qs_rank), 0) as avg_qs
        FROM study_abroad
        GROUP BY target_country
        ORDER BY cnt DESC
    """)
    col3, col4 = st.columns([3, 2])
    with col3:
        fig = px.bar(country_df, x="target_country", y="cnt", color="avg_qs",
                      labels={"target_country": "国家/地区", "cnt": "人数", "avg_qs": "平均QS排名"},
                      color_continuous_scale="Viridis_r")
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        st.dataframe(country_df, use_container_width=True, hide_index=True)

    st.divider()
    col5, col6 = st.columns(2)

    with col5:
        st.subheader("奖学金获取率 (按国家)")
        scholarship = run_query("""
            SELECT target_country,
                   ROUND(AVG(has_scholarship)*100, 1) as scholarship_rate,
                   COUNT(*) as cnt
            FROM study_abroad
            GROUP BY target_country HAVING cnt >= 5
            ORDER BY scholarship_rate DESC
        """)
        fig = px.bar(scholarship, x="target_country", y="scholarship_rate",
                      labels={"target_country": "国家", "scholarship_rate": "获奖率(%)"},
                      color="scholarship_rate", color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)

    with col6:
        st.subheader("各学院保研率排名")
        recommend_college = run_query("""
            SELECT s.college,
                   COUNT(r.recommend_id) as recommend_cnt,
                   ROUND(COUNT(r.recommend_id)*100.0 /
                     (SELECT COUNT(*) FROM students s2 WHERE s2.college=s.college AND s2.degree_level='本科'), 1
                   ) as recommend_rate
            FROM students s
            JOIN postgraduate_recommend r ON s.student_id = r.student_id
            WHERE s.degree_level = '本科'
            GROUP BY s.college
            ORDER BY recommend_rate DESC LIMIT 15
        """)
        fig = px.bar(recommend_college, x="recommend_rate", y="college", orientation="h",
                      labels={"recommend_rate": "保研率(%)", "college": "学院"},
                      color="recommend_rate", color_continuous_scale="Oranges")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("QS排名 vs 语言成绩")
    lang_score = run_query("""
        SELECT qs_rank, toefl_score, ielts_score, target_country,
               has_scholarship
        FROM study_abroad
        WHERE toefl_score > 0 AND qs_rank > 0
        LIMIT 1000
    """)
    fig = px.scatter(lang_score, x="qs_rank", y="toefl_score",
                      color="has_scholarship", size=[8]*len(lang_score),
                      hover_data=["target_country"],
                      labels={"qs_rank": "QS排名", "toefl_score": "托福成绩", "has_scholarship": "有奖学金"})
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# AI 智能问答
# ============================================================

elif page == "🤖 AI 智能问答":
    st.title("🤖 AI 智能问答")

    # 初始化
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None

    st.markdown("向 Data Agent 提问，系统会自动理解问题、生成SQL、查询数据库并给出分析结论。")

    # 推荐问题 —— 点击直接提交
    st.markdown("**推荐问题（点击直接提问）:**")
    example_questions = [
        "2024届本科生各学院的就业率排名？",
        "信息学院硕士去华为的平均月薪是多少？",
        "保研学生中多少人留在了厦大本校？",
        "留学到香港的学生平均QS排名和奖学金比例？",
        "GPA 3.5以上的学生更倾向于就业还是升学？",
        "跨专业考研的上岸率比本专业低多少？",
        "经济学院和管理学院毕业生薪资对比？",
        "各学历层次毕业生的平均起薪差异？",
    ]

    cols = st.columns(2)
    for i, q in enumerate(example_questions):
        if cols[i % 2].button(q, key=f"rec_{i}", use_container_width=True):
            st.session_state.pending_question = q
            st.rerun()

    # 处理推荐问题点击
    if st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = None
        with st.spinner("Agent 思考中..."):
            try:
                from agent.sql_agent import get_agent, query_agent
                agent, _ = get_agent()
                result = query_agent(agent, question)
            except Exception as e:
                result = {"error": str(e), "sql": "", "result": "", "analysis": ""}
        st.session_state.chat_history.append({
            "question": question,
            "result": result,
        })
        st.rerun()

    # 手动输入
    st.divider()
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "输入你的问题",
            placeholder="例如: 2024届信息学院硕士毕业生的平均月薪是多少?",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("提 问", type="primary", use_container_width=True)

    if submitted and user_input:
        with st.spinner("Agent 思考中..."):
            try:
                from agent.sql_agent import get_agent, query_agent
                agent, _ = get_agent()
                result = query_agent(agent, user_input)
            except Exception as e:
                result = {"error": str(e), "sql": "", "result": "", "analysis": ""}
        st.session_state.chat_history.append({
            "question": user_input,
            "result": result,
        })
        st.rerun()

    # 显示聊天历史
    if not st.session_state.chat_history:
        st.info("上方点击推荐问题或输入问题开始分析")
    else:
        for chat in reversed(st.session_state.chat_history):
            with st.chat_message("user"):
                st.markdown(f"**{chat['question']}**")
            with st.chat_message("assistant"):
                if chat["result"]["error"]:
                    st.error(chat["result"]["error"])
                else:
                    if chat["result"]["sql"]:
                        with st.expander("SQL", expanded=False):
                            st.code(chat["result"]["sql"], language="sql")
                    st.markdown("#### 分析结果")
                    st.markdown(chat["result"]["analysis"])
