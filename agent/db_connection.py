"""
数据库连接管理
"""

from langchain_community.utilities import SQLDatabase
from agent.config import DB_URI


def get_database() -> SQLDatabase:
    """获取 LangChain SQLDatabase 实例"""
    return SQLDatabase.from_uri(DB_URI)


def get_db_info(db: SQLDatabase) -> str:
    """获取数据库表结构描述(用于注入Prompt)"""
    return db.get_table_info()


def run_query(db: SQLDatabase, sql: str) -> str:
    """执行查询并返回格式化结果"""
    SAFE_KEYWORDS = ["SELECT", "WITH", "PRAGMA", "EXPLAIN"]
    sql_upper = sql.strip().upper()
    if not any(sql_upper.startswith(kw) for kw in SAFE_KEYWORDS):
        return "错误: 仅允许只读查询(SELECT)"
    try:
        return db.run(sql)
    except Exception as e:
        return f"查询执行错误: {e}"
