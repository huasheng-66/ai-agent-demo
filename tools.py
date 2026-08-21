import pandas as pd
from pathlib import Path

# ===== 工具1：Excel 筛选 =====
def filter_excel(filepath, column, value):
    """
    筛选 Excel 文件中指定列等于某个值的所有行
    
    参数：
        filepath: Excel 文件路径
        column: 要筛选的列名
        value: 筛选的值
    
    返回：
        筛选后的数据（字符串形式）
    """
    try:
        df = pd.read_excel(filepath)
        filtered = df[df[column].astype(str) == str(value)]
        if len(filtered) == 0:
            return f"未找到 {column}={value} 的记录"
        return f"找到 {len(filtered)} 条记录：\n{filtered.to_string()}"
    except Exception as e:
        return f"处理失败：{e}"

# ===== 工具2：文件扫描 =====
def scan_files(directory, extension=None):
    """
    扫描目录下的所有文件
    
    参数：
        directory: 目录路径
        extension: 文件扩展名过滤（如 '.txt'），可选
    
    返回：
        文件列表（字符串形式）
    """
    try:
        path = Path(directory)
        if extension:
            files = list(path.glob(f"*{extension}"))
        else:
            files = list(path.glob("*"))
        
        if len(files) == 0:
            return f"目录 {directory} 下没有文件"
        
        result = f"找到 {len(files)} 个文件：\n"
        for f in files[:10]:  # 最多显示10个
            result += f"  - {f.name}\n"
        if len(files) > 10:
            result += f"  ... 还有 {len(files)-10} 个文件"
        return result
    except Exception as e:
        return f"扫描失败：{e}"

# ===== 工具3：获取当前时间（之前的） =====
def get_current_time():
    from datetime import datetime
    return f"当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# ===== 工具4：简单计算器（之前的） =====
def calculator(expression):
    try:
        result = eval(expression)
        return f"计算结果：{result}"
    except:
        return "计算错误，请检查表达式"

# ===== 工具注册表（所有工具的统一入口） =====
TOOLS = {
    "filter_excel": {
        "func": filter_excel,
        "description": "筛选Excel文件中的数据。参数：filepath(文件路径), column(列名), value(筛选值)"
    },
    "scan_files": {
        "func": scan_files,
        "description": "扫描目录下的文件。参数：directory(目录路径), extension(文件扩展名，可选)"
    },
    "get_current_time": {
        "func": get_current_time,
        "description": "获取当前时间。无需参数"
    },
    "calculator": {
        "func": calculator,
        "description": "数学计算。参数：expression(数学表达式，如 '3+5*2')"
    }
}