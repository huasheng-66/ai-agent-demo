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

# ===== 工具5：整理桌面 =====
def organize_desktop(dry_run=False):
    """
    按文件类型整理桌面文件（支持预览模式）
    
    参数：
        dry_run: True=仅预览不执行，False=真正执行整理
    
    返回：
        整理计划或执行结果报告
    """
    desktop = Path.home() / "Desktop"
    
    # 文件类型分类规则
    folders = {
        "📄 文档": [".docx", ".doc", ".pdf", ".txt", ".xlsx", ".xls", ".pptx", ".ppt", ".md"],
        "🖼️ 图片": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".ico"],
        "📦 压缩包": [".zip", ".rar", ".7z", ".gz", ".tar", ".bz2"],
        "⚙️ 安装包": [".exe", ".msi", ".dmg", ".pkg"],
        "💻 代码": [".py", ".js", ".html", ".css", ".json", ".xml", ".yaml", ".toml"],
        "🎮 快捷方式": [".lnk", ".url"],
    }
    
    # ===== 第一步：收集所有需要整理的文件 =====
    plan = []  # 存放 (文件名, 源路径, 目标文件夹)
    unmatched = []  # 未分类的文件
    
    for file in desktop.iterdir():
        if not file.is_file():
            continue
        if file.name.startswith("desktop.ini"):
            continue
        
        moved = False
        for folder_name, exts in folders.items():
            if file.suffix.lower() in exts:
                plan.append((file.name, file, folder_name))
                moved = True
                break
        
        if not moved:
            plan.append((file.name, file, "📂 其他"))
    
    # ===== 第二步：生成预览报告 =====
    if not plan:
        return "✅ 桌面已经很整洁，没有需要整理的文件"
    
    report = []
    report.append("=" * 50)
    report.append(f"📋 整理计划（共 {len(plan)} 个文件）")
    report.append("=" * 50)
    
    # 按目标文件夹分组
    grouped = {}
    for name, path, folder in plan:
        grouped.setdefault(folder, []).append(name)
    
    for folder, files in grouped.items():
        report.append(f"\n📁 {folder}（{len(files)} 个文件）")
        for f in files[:10]:
            report.append(f"  - {f}")
        if len(files) > 10:
            report.append(f"  ... 还有 {len(files)-10} 个文件")
    
    # ===== 第三步：预览模式 =====
    if dry_run:
        report.append("\n" + "=" * 50)
        report.append("⚠️ 当前为【预览模式】，文件未被移动")
        report.append("💡 确认无误后，调用 organize_desktop(dry_run=False) 执行整理")
        return "\n".join(report)
    
    # ===== 第四步：真正执行整理 =====
    moved_count = 0
    moved_details = []
    errors = []
    
    for name, file, folder_name in plan:
        target = desktop / folder_name
        target.mkdir(exist_ok=True)
        try:
            # 如果目标已存在同名文件，加后缀
            target_path = target / name
            if target_path.exists():
                stem = file.stem
                suffix = file.suffix
                counter = 1
                while target_path.exists():
                    new_name = f"{stem}_{counter}{suffix}"
                    target_path = target / new_name
                    counter += 1
            file.rename(target_path)
            moved_count += 1
            moved_details.append(f"  {name} → {folder_name}")
        except Exception as e:
            errors.append(f"  {name} 移动失败：{e}")
    
    # ===== 第五步：生成执行报告 =====
    result = []
    result.append("=" * 50)
    result.append(f"✅ 整理完成！共移动 {moved_count} 个文件")
    result.append("=" * 50)
    result.append("\n".join(moved_details[:20]))
    if len(moved_details) > 20:
        result.append(f"... 还有 {len(moved_details)-20} 个文件")
    
    if errors:
        result.append("\n❌ 以下文件移动失败：")
        result.append("\n".join(errors))
    
    return "\n".join(result)

# ===== 工具6：显示无用文件/缓存文件 =====
def find_useless_files(directory=None):
    """
    扫描无用文件：临时文件、缓存文件、空文件、重复文件（按大小）
    """
    if directory is None:
        directory = str(Path.home() / "Desktop")
    
    target = Path(directory)
    useless = []
    warnings = []
    
    # 1. 按扩展名识别临时/缓存文件
    temp_exts = {'.tmp', '.cache', '.log', '.bak', '.old', '.swp', '.~'}
    
    # 2. 按文件名模式识别
    temp_patterns = ['~$', 'desktop.ini', 'thumbs.db', '.DS_Store']
    
    # 3. 扫描
    for file in target.rglob('*'):
        if not file.is_file():
            continue
        
        # 检查扩展名
        if file.suffix.lower() in temp_exts:
            useless.append(f"临时文件: {file.name} ({file.stat().st_size} bytes)")
            continue
        
        # 检查模式
        if any(p in file.name for p in temp_patterns):
            useless.append(f"系统缓存: {file.name}")
            continue
        
        # 检查空文件（小于 10 字节）
        if file.stat().st_size < 10:
            useless.append(f"空文件: {file.name} ({file.stat().st_size} bytes)")
            continue
    
    # 结果汇总
    if not useless:
        return "🎉 未发现明显的无用文件或缓存文件，桌面很干净！"
    
    report = f"发现 {len(useless)} 个无用/缓存文件：\n"
    report += "\n".join(useless[:20])
    if len(useless) > 20:
        report += f"\n... 还有 {len(useless)-20} 个"
    report += "\n\n💡 提示：可以手动删除，或使用清理工具移除"
    
    return report

# ===== 工具7：批量撤回 =====
def undo_organize_desktop():
    """
    撤销桌面整理：把所有分类文件夹里的文件移回桌面
    """
    desktop = Path.home() / "Desktop"
    moved_back = []
    
    # 整理时创建的那些文件夹（如果你改过名字，这里要同步）
    folders_to_undo = [
        "📄 文档", "🖼️ 图片", "📦 压缩包", 
        "⚙️ 安装包", "💻 代码", "🎮 快捷方式", "📂 其他"
    ]
    
    for folder_name in folders_to_undo:
        folder = desktop / folder_name
        if not folder.exists():
            continue
        
        for file in folder.iterdir():
            if file.is_file():
                target = desktop / file.name
                # 如果桌面已存在同名文件，加个后缀避免覆盖
                if target.exists():
                    counter = 1
                    new_name = f"{file.stem}_恢复{counter}{file.suffix}"
                    target = desktop / new_name
                    while target.exists():
                        counter += 1
                        new_name = f"{file.stem}_恢复{counter}{file.suffix}"
                        target = desktop / new_name
                file.rename(target)
                moved_back.append(f"{file.name} → 桌面")
        
        # 文件夹清空后删除
        if not any(folder.iterdir()):
            folder.rmdir()
    
    if not moved_back:
        return "没有找到需要撤销的文件，可能已经撤销过了"
    
    return f"✅ 已撤销 {len(moved_back)} 个文件：\n" + "\n".join(moved_back[:20])