import ollama
import json
from tools import TOOLS as BASE_TOOLS
from tools_legacy import (
    summarize_document,
    send_email,
    rename_files,
    generate_daily_report
)

# ===== 合并所有工具 =====
TOOLS = {
    **BASE_TOOLS,  # 原有工具（计算器、时间、Excel筛选、文件扫描）
    "summarize_document": {
        "func": summarize_document,
        "description": "生成文档摘要。参数：filepath(文档路径)"
    },
    "send_email": {
        "func": send_email,
        "description": "发送邮件。参数：to_email(收件人), subject(主题), body(正文)"
    },
    "rename_files": {
        "func": rename_files,
        "description": "批量重命名文件。参数：directory(目录), old_text(旧文本), new_text(新文本)"
    },
    "generate_daily_report": {
        "func": generate_daily_report,
        "description": "生成今日日报。无需参数"
    }
}

def run_agent(user_goal):
    """Agent 核心逻辑（和之前一样，但工具更多了）"""
    tools_desc = "\n".join([
        f"- {name}: {info['description']}"
        for name, info in TOOLS.items()
    ])
    
    prompt = f"""
你是一个智能助手，用户的目标是：{user_goal}

你可以使用以下工具：
{tools_desc}

请只回答一个JSON，格式为：
{{"tool": "工具名称", "params": {{"参数名1": "值1", "参数名2": "值2"}}}}

如果不需要工具，回答：
{{"tool": "none"}}
"""
    
    response = ollama.chat(
        model='llama3.2:3b',
        messages=[{'role': 'user', 'content': prompt}]
    )
    
    try:
        text = response['message']['content']
        if '```' in text:
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
        decision = json.loads(text.strip())
    except Exception as e:
        return f"AI无法理解：{e}"
    
    if decision['tool'] == 'none':
        return "已完成，无需使用工具"
    
    if decision['tool'] in TOOLS:
        tool = TOOLS[decision['tool']]
        params = decision.get('params', {})
        if isinstance(params, dict):
            try:
                result = tool['func'](**params)
                return f"✅ 使用 {decision['tool']}，{result}"
            except TypeError as e:
                return f"❌ 参数错误：{e}"
        else:
            return "❌ 参数格式错误"
    else:
        return f"❌ 工具 '{decision['tool']}' 不存在"

# ===== 测试 =====
if __name__ == "__main__":
    print("🤖 完整 Agent 系统（7个工具）")
    print("="*50)
    
    # 测试1：文档摘要
    print("\n【测试1】用户：总结 article.txt")
    print(run_agent("总结 article.txt"))
    
    # 测试2：生成日报
    print("\n【测试2】用户：生成今天的日报")
    print(run_agent("生成今天的日报"))
    
    # 测试3：Excel筛选
    print("\n【测试3】用户：筛选 data.xlsx 中 部门 等于 销售 的行")
    print(run_agent("筛选 data.xlsx 中 部门 等于 销售 的行"))