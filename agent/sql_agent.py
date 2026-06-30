"""
厦门大学毕业生去向 Data Agent
基于 LangChain 1.3+ SQLDatabaseToolkit + create_agent 实现自然语言查询
"""

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from agent.config import LLM_CONFIG, AGENT_CONFIG, DB_URI
from agent.prompts import XMU_SYSTEM_PROMPT


def create_llm():
    return ChatOpenAI(
        model=LLM_CONFIG["model"],
        temperature=LLM_CONFIG["temperature"],
        max_tokens=LLM_CONFIG["max_tokens"],
        openai_api_key=LLM_CONFIG["api_key"],
        openai_api_base=LLM_CONFIG["base_url"],
    )


def create_agent_instance(llm=None, db=None):
    if llm is None:
        llm = create_llm()
    if db is None:
        db = SQLDatabase.from_uri(DB_URI)

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=XMU_SYSTEM_PROMPT,
    )

    return agent, db


def query_agent(agent, question: str) -> dict:
    dangerous = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE"]
    if any(kw in question.upper() for kw in dangerous):
        return {
            "sql": "",
            "result": "",
            "analysis": "不支持修改数据库操作。",
            "error": None,
        }

    try:
        response = agent.invoke({"messages": [{"role": "user", "content": question}]})

        # Extract the final AI response from messages
        messages = response.get("messages", [])
        output = ""
        for msg in reversed(messages):
            if hasattr(msg, "content") and msg.content:
                output = msg.content
                break
        if not output:
            output = str(response)

        # Try to extract SQL from output
        sql = ""
        if "```sql" in output:
            sql_start = output.index("```sql") + 6
            sql_end = output.index("```", sql_start)
            sql = output[sql_start:sql_end].strip()
        elif "SELECT" in output.upper():
            lines = output.split("\n")
            sql_lines = []
            for line in lines:
                if line.strip().upper().startswith("SELECT") or sql_lines:
                    sql_lines.append(line)
                    if ";" in line:
                        break
            sql = "\n".join(sql_lines)

        return {
            "sql": sql,
            "result": output,
            "analysis": output,
            "error": None,
        }

    except Exception as e:
        return {
            "sql": "",
            "result": "",
            "analysis": "",
            "error": f"查询出错: {str(e)}",
        }


# 单例
_agent_instance = None
_db_instance = None


def get_agent():
    global _agent_instance, _db_instance
    if _agent_instance is None:
        _agent_instance, _db_instance = create_agent_instance()
    return _agent_instance, _db_instance


if __name__ == "__main__":
    print("=" * 60)
    print("厦门大学毕业生去向 Data Agent 测试")
    print("=" * 60)

    agent, db = create_agent_instance()

    test_questions = [
        "2024届毕业生总共有多少人？各个去向分布如何？",
        "信息学院本科毕业生的平均月薪是多少？",
        "考研成功率最高的三个学院是哪些？",
    ]

    for q in test_questions:
        print(f"\n{'=' * 40}")
        print(f"Q: {q}")
        print("-" * 40)
        result = query_agent(agent, q)
        if result["error"]:
            print(f"错误: {result['error']}")
        else:
            print(result["result"][:800])
