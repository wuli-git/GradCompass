-- ============================================
-- 厦门大学毕业生去向数据分析智能体
-- 数据库建表脚本 (SQLite)
-- ============================================

-- 1. 学生基本信息表
CREATE TABLE IF NOT EXISTS students (
    student_id       INTEGER PRIMARY KEY,
    gender           VARCHAR(2)     NOT NULL,
    age              INTEGER,
    home_province    VARCHAR(20),
    home_city        VARCHAR(20),
    campus           VARCHAR(10)    NOT NULL,
    college          VARCHAR(30)    NOT NULL,
    major_name       VARCHAR(50)    NOT NULL,
    degree_level     VARCHAR(10)    NOT NULL,
    graduation_year  INTEGER        NOT NULL,
    destination      VARCHAR(10)    NOT NULL,
    is_xmu_undergrad INTEGER        DEFAULT 1
);

-- 2. 学业表现表
CREATE TABLE IF NOT EXISTS academic_records (
    record_id        INTEGER PRIMARY KEY,
    student_id       INTEGER REFERENCES students(student_id),
    gpa              DECIMAL(3,2),
    gpa_rank_pct     DECIMAL(4,1),
    cet4_score       INTEGER,
    cet6_score       INTEGER,
    has_paper        INTEGER DEFAULT 0,
    paper_level      VARCHAR(10),
    has_competition  INTEGER DEFAULT 0,
    has_internship   INTEGER DEFAULT 0,
    internship_count INTEGER DEFAULT 0,
    volunteer_hours  INTEGER
);

-- 3. 就业信息表
CREATE TABLE IF NOT EXISTS employment (
    employment_id    INTEGER PRIMARY KEY,
    student_id       INTEGER REFERENCES students(student_id),
    company_name     VARCHAR(80),
    company_type     VARCHAR(20),
    industry         VARCHAR(30),
    job_city         VARCHAR(20),
    job_province     VARCHAR(20),
    is_first_tier    INTEGER DEFAULT 0,
    monthly_salary   DECIMAL(10,2),
    annual_salary    DECIMAL(12,2),
    signing_bonus    DECIMAL(10,2),
    job_satisfaction INTEGER,
    is_major_match   INTEGER DEFAULT 1,
    offer_count      INTEGER DEFAULT 1
);

-- 4. 考研信息表
CREATE TABLE IF NOT EXISTS postgraduate_exam (
    exam_id            INTEGER PRIMARY KEY,
    student_id         INTEGER REFERENCES students(student_id),
    target_university  VARCHAR(50),
    target_college     VARCHAR(30),
    target_major       VARCHAR(50),
    target_tier        VARCHAR(10),
    is_cross_college   INTEGER DEFAULT 0,
    is_cross_major     INTEGER DEFAULT 0,
    exam_total_score   INTEGER,
    exam_politics      INTEGER,
    exam_english       INTEGER,
    exam_math          INTEGER,
    exam_major_course  INTEGER,
    is_admitted        INTEGER DEFAULT 0,
    is_first_choice    INTEGER DEFAULT 1,
    is_transfer        INTEGER DEFAULT 0,
    prep_months        INTEGER
);

-- 5. 保研信息表
CREATE TABLE IF NOT EXISTS postgraduate_recommend (
    recommend_id       INTEGER PRIMARY KEY,
    student_id         INTEGER REFERENCES students(student_id),
    target_university  VARCHAR(50),
    target_college     VARCHAR(30),
    target_major       VARCHAR(50),
    target_tier        VARCHAR(10),
    is_cross_college   INTEGER DEFAULT 0,
    is_cross_major     INTEGER DEFAULT 0,
    recommend_type     VARCHAR(20),
    is_accepted        INTEGER DEFAULT 1,
    is_xmu_internal    INTEGER DEFAULT 1,
    application_count  INTEGER DEFAULT 1
);

-- 6. 留学信息表
CREATE TABLE IF NOT EXISTS study_abroad (
    abroad_id           INTEGER PRIMARY KEY,
    student_id          INTEGER REFERENCES students(student_id),
    target_country      VARCHAR(30),
    target_university   VARCHAR(80),
    target_major        VARCHAR(50),
    qs_rank             INTEGER,
    has_scholarship     INTEGER DEFAULT 0,
    scholarship_type    VARCHAR(20),
    scholarship_amount  DECIMAL(10,2),
    ielts_score         DECIMAL(3,1),
    toefl_score         INTEGER,
    gre_score           INTEGER,
    gmat_score          INTEGER,
    offer_count         INTEGER DEFAULT 1,
    agent_used          INTEGER DEFAULT 0
);

-- 7. 学院信息字典表
CREATE TABLE IF NOT EXISTS colleges (
    college_id    INTEGER PRIMARY KEY,
    college_name  VARCHAR(30),
    college_type  VARCHAR(10),
    campus        VARCHAR(10),
    abbreviation  VARCHAR(10)
);

-- ============================================
-- 索引
-- ============================================
CREATE INDEX IF NOT EXISTS idx_stu_dest       ON students(destination);
CREATE INDEX IF NOT EXISTS idx_stu_college    ON students(college);
CREATE INDEX IF NOT EXISTS idx_stu_degree     ON students(degree_level);
CREATE INDEX IF NOT EXISTS idx_stu_gradyear   ON students(graduation_year);
CREATE INDEX IF NOT EXISTS idx_stu_campus     ON students(campus);
CREATE INDEX IF NOT EXISTS idx_emp_salary     ON employment(monthly_salary);
CREATE INDEX IF NOT EXISTS idx_emp_industry   ON employment(industry);
CREATE INDEX IF NOT EXISTS idx_emp_city       ON employment(job_city);
CREATE INDEX IF NOT EXISTS idx_emp_company    ON employment(company_name);
CREATE INDEX IF NOT EXISTS idx_exam_admitted  ON postgraduate_exam(is_admitted);
CREATE INDEX IF NOT EXISTS idx_exam_target    ON postgraduate_exam(target_university);
CREATE INDEX IF NOT EXISTS idx_recom_type     ON postgraduate_recommend(recommend_type);
CREATE INDEX IF NOT EXISTS idx_recom_xmu      ON postgraduate_recommend(is_xmu_internal);
CREATE INDEX IF NOT EXISTS idx_abroad_country ON study_abroad(target_country);
CREATE INDEX IF NOT EXISTS idx_abroad_qs      ON study_abroad(qs_rank);
