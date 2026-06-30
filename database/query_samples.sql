-- ============================================
-- 厦门大学毕业生去向分析 — 示例SQL查询
-- 用于验证数据导入和展示分析能力
-- ============================================

-- 1. 总体去向分布
SELECT destination, COUNT(*) as cnt, ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM students), 1) as pct
FROM students GROUP BY destination ORDER BY cnt DESC;

-- 2. 各学历层次去向分布
SELECT degree_level, destination, COUNT(*) as cnt
FROM students GROUP BY degree_level, destination
ORDER BY degree_level, cnt DESC;

-- 3. 各学院就业人数和平均薪资 (TOP 10)
SELECT s.college, COUNT(*) as employed, ROUND(AVG(e.monthly_salary), 0) as avg_salary
FROM students s
JOIN employment e ON s.student_id = e.student_id
GROUP BY s.college
ORDER BY employed DESC LIMIT 10;

-- 4. 主要雇主录用情况
SELECT company_name, company_type, industry, COUNT(*) as hires,
       ROUND(AVG(monthly_salary), 0) as avg_salary
FROM employment
GROUP BY company_name
ORDER BY hires DESC LIMIT 20;

-- 5. 考研上岸率 (按学院)
SELECT s.college, COUNT(*) as exam_takers,
       SUM(CASE WHEN p.is_admitted=1 THEN 1 ELSE 0 END) as admitted,
       ROUND(AVG(p.is_admitted)*100, 1) as admit_rate
FROM students s
JOIN postgraduate_exam p ON s.student_id = p.student_id
GROUP BY s.college
HAVING exam_takers >= 10
ORDER BY admit_rate DESC;

-- 6. 保研本校 vs 外校
SELECT CASE WHEN is_xmu_internal=1 THEN '本校' ELSE '外校' END as type,
       COUNT(*) as cnt,
       ROUND(AVG(application_count), 1) as avg_applications
FROM postgraduate_recommend
GROUP BY is_xmu_internal;

-- 7. 留学国家分布 (TOP 10)
SELECT target_country, COUNT(*) as cnt,
       ROUND(AVG(qs_rank), 0) as avg_qs,
       ROUND(AVG(has_scholarship)*100, 1) as scholarship_rate
FROM study_abroad
GROUP BY target_country
ORDER BY cnt DESC LIMIT 10;

-- 8. 行业薪资对比 (含学历)
SELECT e.industry, s.degree_level,
       COUNT(*) as cnt,
       ROUND(AVG(e.monthly_salary), 0) as avg_salary,
       ROUND(MIN(e.monthly_salary), 0) as min_salary,
       ROUND(MAX(e.monthly_salary), 0) as max_salary
FROM employment e
JOIN students s ON e.student_id = s.student_id
GROUP BY e.industry, s.degree_level
HAVING cnt >= 5
ORDER BY avg_salary DESC;

-- 9. GPA 与就业薪资的相关性
SELECT
  CASE
    WHEN a.gpa >= 3.7 THEN '3.7-4.0'
    WHEN a.gpa >= 3.3 THEN '3.3-3.7'
    WHEN a.gpa >= 3.0 THEN '3.0-3.3'
    WHEN a.gpa >= 2.5 THEN '2.5-3.0'
    ELSE '<2.5'
  END as gpa_range,
  COUNT(*) as cnt,
  ROUND(AVG(e.monthly_salary), 0) as avg_salary
FROM academic_records a
JOIN employment e ON a.student_id = e.student_id
GROUP BY gpa_range
ORDER BY gpa_range DESC;

-- 10. 交叉分析: 同一GPA水平不同去向的选择
SELECT
  CASE
    WHEN a.gpa >= 3.7 THEN '高分段(3.7+)'
    WHEN a.gpa >= 3.3 THEN '中高分段(3.3-3.7)'
    WHEN a.gpa >= 3.0 THEN '中分段(3.0-3.3)'
    WHEN a.gpa >= 2.5 THEN '中低分段(2.5-3.0)'
    ELSE '低分段(<2.5)'
  END as gpa_level,
  s.destination,
  COUNT(*) as cnt
FROM students s
JOIN academic_records a ON s.student_id = a.student_id
WHERE s.degree_level = '本科'
GROUP BY gpa_level, s.destination
ORDER BY gpa_level, cnt DESC;

-- 11. 跨专业考研分析
SELECT
  CASE WHEN is_cross_major=1 THEN '跨专业' ELSE '本专业' END as exam_type,
  COUNT(*) as cnt,
  ROUND(AVG(exam_total_score), 0) as avg_score,
  ROUND(AVG(is_admitted)*100, 1) as admit_rate
FROM postgraduate_exam
GROUP BY is_cross_major;

-- 12. 一线城市 vs 非一线薪资
SELECT
  CASE WHEN e.is_first_tier=1 THEN '一线(北上广深)' ELSE '其他城市' END as city_type,
  COUNT(*) as cnt,
  ROUND(AVG(e.monthly_salary), 0) as avg_salary,
  ROUND(AVG(e.annual_salary), 0) as avg_annual
FROM employment e
GROUP BY e.is_first_tier;

-- 13. 保研类型分析
SELECT recommend_type, COUNT(*) as cnt,
       ROUND(AVG(CASE WHEN is_xmu_internal=1 THEN 1 ELSE 0 END)*100, 1) as internal_rate
FROM postgraduate_recommend
GROUP BY recommend_type
ORDER BY cnt DESC;

-- 14. 论文发表对留学奖学金的影响
SELECT
  a.has_paper,
  COUNT(*) as cnt,
  ROUND(AVG(sa.has_scholarship)*100, 1) as scholarship_rate,
  ROUND(AVG(sa.scholarship_amount), 0) as avg_amount
FROM study_abroad sa
JOIN academic_records a ON sa.student_id = a.student_id
GROUP BY a.has_paper;

-- 15. 2022-2024去向趋势
SELECT graduation_year, destination, COUNT(*) as cnt
FROM students
GROUP BY graduation_year, destination
ORDER BY graduation_year, destination;
