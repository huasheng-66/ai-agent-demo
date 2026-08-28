import ollama
import json
from tools import TOOLS as BASE_TOOLS
from tools import filter_excel, scan_files, get_current_time, calculator  # 新增
from tools_legacy import (
    summarize_document,
    send_email,
    rename_files,
    generate_daily_report,
    organize_desktop,
    find_useless_files,
    undo_organize_desktop,
    scan_desktop_changes
)
from rag_tool import ask_document

# ===== 合并所有工具 =====
TOOLS = {
    **BASE_TOOLS,
    "ask_document": {
        "func": ask_document,
        "description": "基于文档回答问题（RAG检索增强生成）。当用户问某个文档里的内容时使用。参数：query(问题), doc_path(文档路径，可选)"
    },
    "summarize_document": {
        "func": summarize_document,
        "description": "读取并总结文档内容。当用户要求'总结'、'摘要'、'概括'某个文件时使用。参数：filepath(文件路径，如'article.txt')"
    },
    "generate_daily_report": {
        "func": generate_daily_report,
        "description": "生成今日工作报告。当用户要求'生成日报'、'写日报'、'今日报告'时使用。无需参数"
    },
    "send_email": {
        "func": send_email,
        "description": "发送邮件。参数：to_email(收件人地址), subject(邮件主题), body(邮件正文)"
    },
    "rename_files": {
        "func": rename_files,
        "description": "批量重命名文件。参数：directory(目录路径), old_text(要替换的文本), new_text(新文本)"
    },
    "organize_desktop": {
        "func": organize_desktop,
        "description": "按文件类型整理桌面。先预览效果，再执行。参数：dry_run(True=预览，False=执行)"
    },
    "find_useless_files": {
        "func": find_useless_files,
        "description": "扫描无用文件、临时文件、缓存文件和空文件。当用户要求'清理'、'无用文件'、'缓存'、'临时文件'时使用。参数：directory(目录路径，可选)"
    },
    "undo_organize_desktop": {
        "func": undo_organize_desktop,
        "description": "撤销桌面整理，把刚才整理到各文件夹的文件全部移回桌面。当用户要求'撤销整理'、'恢复文件'时使用。无需参数"
    },
    "scan_desktop_changes": {
        "func": scan_desktop_changes,
        "description": "监控桌面文件变化，显示新增、修改、删除的文件。当用户询问'新增了哪些文件'、'今天加了什么'、'桌面有什么变化'时使用。无需参数"
    }
}

def run_agent(user_goal):

    """Agent：先用规则判断意图，再调用对应工具"""
    
    # ===== 意图识别层（100%准确，不依赖AI） =====
    goal_lower = user_goal.lower()

    # ===== 规则1：RAG（放在扫描前面） =====
    if "说了什么" in goal_lower or "内容" in goal_lower or "讲" in goal_lower or "是什么" in goal_lower:
        import re
        # 提取文件名
        match = re.search(r'(\w+\.\w+)\s*里', user_goal)
        if match:
            filename = match.group(1)
            result = ask_document(user_goal, filename)
            return f"✅ 使用 ask_document，{result}"
        else:
            # 没有指定文件，尝试用默认的 article.txt
            result = ask_document(user_goal)
            return f"✅ 使用 ask_document，{result}"

    # 规则2：监控新增
    if "新增" in goal_lower or "变化" in goal_lower or "加了" in goal_lower or "新文件" in goal_lower:
        result = scan_desktop_changes()
        return f"✅ 使用 scan_desktop_changes，{result}"
    
    # 规则3：整理桌面
    if "整理桌面" in goal_lower or "整理文件" in goal_lower:
        if "预览" in goal_lower:
            result = organize_desktop(dry_run=True)
        else:
            result = organize_desktop(dry_run=False)
        return f"✅ 使用 organize_desktop，{result}"
    
    # 规则4：撤销整理桌面
    if "撤销" in goal_lower or "恢复" in goal_lower:
        result = undo_organize_desktop()
        return f"✅ 使用 undo_organize_desktop，{result}"
    
    # 规则5：显示无用文件/缓存文件
    if "无用" in goal_lower or "缓存" in goal_lower or "临时" in goal_lower or "清理" in goal_lower:
        result = find_useless_files()
        return f"✅ 使用 find_useless_files，{result}"

    # 规则6：总结文档
    if "总结" in goal_lower or "摘要" in goal_lower or "概括" in goal_lower:
        import re
        # 提取文件名
        match = re.search(r'(\w+\.\w+)', user_goal)
        filename = match.group(1) if match else "article.txt"
        result = summarize_document(filename)
        return f"✅ 使用 summarize_document，{result}"
    
    # 规则7：生成日报
    if "日报" in goal_lower or "今日报告" in goal_lower or "今天的日报" in goal_lower:
        result = generate_daily_report()
        return f"✅ 使用 generate_daily_report，{result}"
    
    # 规则8：Excel筛选
    if "筛选" in goal_lower and ".xlsx" in goal_lower:
        # 提取文件名、列名、值
        import re
        # 匹配：筛选 data.xlsx 中 部门 等于 销售 的行
        match = re.search(r'筛选\s+(\S+\.xlsx)\s+中\s+(\S+)\s+等于\s+(\S+)', user_goal)
        if match:
            filename, column, value = match.groups()
            result = filter_excel(filename, column, value)
            return f"✅ 使用 filter_excel，{result}"
        else:
            return "无法解析筛选条件，请使用格式：筛选 文件名.xlsx 中 列名 等于 值"
    
    # 规则9：计算
    if "计算" in goal_lower:
        import re
        match = re.search(r'计算\s+(.+)', user_goal)
        if match:
            result = calculator(match.group(1))
            return f"✅ 使用 calculator，{result}"
    
    # 规则10：时间
    if "时间" in goal_lower or "几点" in goal_lower:
        result = get_current_time()
        return f"✅ 使用 get_current_time，{result}"
    
    # 规则11：文件扫描
    if "扫描" in goal_lower or "文件" in goal_lower:
        import re
        match = re.search(r'扫描\s+(\S+)', user_goal)
        directory = match.group(1) if match else "."
        result = scan_files(directory)
        return f"✅ 使用 scan_files，{result}"
   
    # ===== 如果规则匹配不到，才交给AI =====
    # ... 原有的 AI 决策逻辑（作为备用）
    """Agent 核心逻辑（和之前一样，但工具更多了）"""
    tools_desc = "\n".join([
        f"- {name}: {info['description']}"
        for name, info in TOOLS.items()
    ])
    
    prompt = f"""
你是一个智能助手，用户的目标是：{user_goal}

可用工具列表：
{tools_desc}

**决策规则：**
1. 如果用户明确要求"总结"、"摘要"某个文件 → 使用 summarize_document
2. 如果用户要求"生成日报"、"写日报" → 使用 generate_daily_report
3. 如果用户要求"筛选"Excel数据 → 使用 filter_excel
4. 如果用户要求"计算" → 使用 calculator
5. 如果用户要求"时间" → 使用 get_current_time
6. 如果用户只是打招呼或不需要工具 → 返回 {{"tool": "none"}}

**返回格式（纯JSON）：**
{{"tool": "工具名称", "params": {{"参数名": "参数值"}}}}

如果不需要工具：
{{"tool": "none"}}
"""
    
    response = ollama.chat(
        model='llama3.2:3b',
        messages=[{'role': 'user', 'content': prompt}]
    )
    
    # ===== 更健壮的 JSON 解析 =====
    try:
        text = response['message']['content']
        
        # 方法1：尝试直接解析
        try:
            decision = json.loads(text.strip())
        except:
            # 方法2：如果包含```，提取中间的
            if '```' in text:
                parts = text.split('```')
                for part in parts:
                    part = part.strip()
                    if part.startswith('json'):
                        part = part[4:].strip()
                    try:
                        decision = json.loads(part)
                        break
                    except:
                        continue
            else:
                # 方法3：用正则提取 JSON 对象
                import re
                json_match = re.search(r'\{[^{}]*\}', text)
                if json_match:
                    try:
                        decision = json.loads(json_match.group())
                    except:
                        raise
                else:
                    raise ValueError("未找到有效的 JSON")
    except Exception as e:
        return f"AI无法理解：{e}\n原始回复：{text[:200]}..."
    
    if 'tool' not in decision or decision['tool'] == 'none':
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

# ===== 交互模式 =====
if __name__ == "__main__":
    print("=" * 50)
    print("🤖 桌面管家 Agent 已启动")
    print("=" * 50)
    print("支持的功能：")
    print("  📁 整理桌面")
    print("  🔍 扫描无用文件")
    print("  ↩️  撤销整理")
    print("  📄 总结文档")
    print("  📊 生成日报")
    print("  📂 筛选 Excel")
    print("  ❓ 基于文档提问")
    print("-" * 50)
    print("输入 'exit' 或 'quit' 退出")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n🧑 你：")
            if user_input.lower() in ['exit', 'quit']:
                print("👋 再见！")
                break
            if not user_input.strip():
                continue
            
            response = run_agent(user_input)
            print(f"🤖 Agent：{response}")
            
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 出错：{e}")