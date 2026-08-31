# 🤖 AI Agent 系统

基于 Ollama 构建的 AI Agent，能自主调用工具完成复杂任务。

## ✨ 功能

- 🧠 AI 自主决策：理解用户目标，选择最合适的工具
- 🛠️ 8 个内置工具：计算器、Excel筛选、文档摘要、发送邮件、文件扫描、批量重命名、日报生成、获取时间、整理桌面、撤销整理、扫描无用文件
- 🔌 可扩展：注册新工具只需 3 行代码
- 🔒 完全本地运行，数据不上传

## 🛠️ 技术栈

| 工具 | 用途 |
|------|------|
| Ollama | 本地 LLM |
| Python | 核心逻辑 |
| Pandas | Excel 处理 |

## 🛠️ 内置工具

| 工具名称 | 功能 |
|---------|------|
| calculator | 数学计算 |
| get_current_time | 获取当前时间 |
| filter_excel | Excel 数据筛选 |
| scan_files | 文件扫描 |
| summarize_document | 文档摘要 |
| send_email | 发送邮件 |
| rename_files | 批量重命名 |
| generate_daily_report | 生成日报 |
| ask_document | RAG 问答（基于文档内容回答问题） |
| organize_desktop | 整理桌面 |
| undo_organize_desktop | 撤销整理 |
| find_useless_files | 扫描无用文件 |

## 🧹 桌面管家功能

| 功能 | 触发指令 |
|------|---------|
| 整理桌面（预览/执行） | "预览整理桌面" / "整理桌面" |
| 撤销整理 | "撤销整理桌面" |
| 扫描无用文件 | "扫描无用文件" |
| 监控新增文件 | "新增了什么文件" |
| 快速查找文件 | "找 关键词" / "搜索 关键词" |

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install ollama pandas openpyxl

# 2. 启动 Ollama
ollama serve

# 3. 运行 Agent
python agent_with_tools.py
```

## 🎯 核心流程

用户输入 → AI 理解目标 → 选择工具 → 执行工具 → 返回结果

## 📁 项目结构

├── agent_with_tools.py   # Agent 主程序
├── tools.py              # 基础工具（计算器、时间）
└── tools_legacy.py       # 扩展工具（Excel、文档、邮件等）

## 📸 演示

[插入演示视频链接]