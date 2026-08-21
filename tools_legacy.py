import pandas as pd
from pathlib import Path
from datetime import datetime
import ollama
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ===== 工具1：文档摘要（来自 doc_summarizer.py） =====
def summarize_document(filepath):
    """读取文档并用 AI 生成摘要"""
    try:
        # 读取文件
        path = Path(filepath)
        if not path.exists():
            return f"文件不存在：{filepath}"
        
        content = path.read_text(encoding='utf-8')
        if not content.strip():
            return "文件为空"
        
        # 调用 AI 生成摘要
        prompt = "请用简洁的中文总结以下内容的核心要点：\n\n" + content[:3000]  # 限制长度
        
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response['message']['content'].strip()
    except Exception as e:
        return f"摘要生成失败：{e}"

# ===== 工具2：发送邮件（来自 email_reminder.py） =====
def send_email(to_email, subject, body):
    """发送邮件提醒（需要配置邮箱）"""
    try:
        # 这里需要配置你的邮箱信息
        # 注意：实际使用需要替换为真实配置
        smtp_server = "smtp.qq.com"  # 示例：QQ邮箱
        smtp_port = 587
        sender_email = "2166217672@qq.com"
        password = "jqfkgqyxcmwtdigg"
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        
        return f"邮件已发送至 {to_email}"
    except Exception as e:
        return f"邮件发送失败：{e}"

# ===== 工具3：文件批量重命名（来自 file_scanner.py 的扩展） =====
def rename_files(directory, old_text, new_text):
    """批量重命名文件"""
    try:
        path = Path(directory)
        count = 0
        for file in path.glob("*"):
            if old_text in file.name:
                new_name = file.name.replace(old_text, new_text)
                new_path = file.parent / new_name
                file.rename(new_path)
                count += 1
        return f"已重命名 {count} 个文件"
    except Exception as e:
        return f"重命名失败：{e}"

# ===== 工具4：生成日报（来自 daily_reporter.py） =====
def generate_daily_report():
    """生成当天的日报摘要"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        # 模拟生成日报内容
        report = f"""
📊 每日报告 - {today}
================================
✅ 今日完成事项：
  1. 运行 AI Agent 系统测试
  2. 处理 Excel 数据筛选
  3. 文档摘要生成

📈 当前状态：
  - Agent 工具数量：7 个
  - 系统运行正常

📅 明日计划：
  1. 继续扩展 Agent 工具集
  2. 优化工具调用准确性
"""
        return report
    except Exception as e:
        return f"日报生成失败：{e}"