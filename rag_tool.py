import chromadb
import ollama
import re
from pathlib import Path

# ===== RAG核心函数（供Agent调用） =====
def ask_document(query, doc_path=None):
    """
    基于文档回答问题（RAG）
    
    参数：
        query: 用户的问题
        doc_path: 文档路径（可选，如果不指定则使用已有索引）
    
    返回：
        基于文档的回答
    """
    try:
        # 1. 读取文档
        if doc_path:
            path = Path(doc_path)
            if not path.exists():
                return f"文件不存在：{doc_path}"
            content = path.read_text(encoding='utf-8')
        else:
            # 如果没有指定文档，尝试使用默认的 article.txt
            default_path = Path.home() / "Desktop" / "article.txt"
            if default_path.exists():
                content = default_path.read_text(encoding='utf-8')
            else:
                return "请指定文档路径，或确保 article.txt 在桌面上"
        
        # 2. 切分文档
        sentences = re.split(r'[。！？；\n]', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        chunks = []
        for i in range(0, len(sentences), 4):
            chunk = '。'.join(sentences[i:i+4])
            if chunk:
                chunks.append(chunk)
        
        if len(chunks) == 0:
            return "文档内容太少，无法回答问题"
        
        # 3. 建立临时向量索引
        client = chromadb.PersistentClient(path="./temp_rag_db")
        collection = client.get_or_create_collection(name="temp_collection")
        
        # 清空旧数据
        try:
            existing_ids = collection.get()['ids']
            if existing_ids:
                collection.delete(ids=existing_ids)
        except:
            pass
        
        for i, chunk in enumerate(chunks):
            response = ollama.embeddings(model='nomic-embed-text', prompt=chunk)
            embedding = response['embedding']
            collection.add(
                ids=[f"chunk_{i}"],
                documents=[chunk],
                embeddings=[embedding]
            )
        
        # 4. 检索相关段落
        query_response = ollama.embeddings(model='nomic-embed-text', prompt=query)
        query_embedding = query_response['embedding']
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        
        if len(results['documents'][0]) == 0:
            return "未找到相关内容，请换个问题"
        
        context = "\n\n---\n\n".join(results['documents'][0])
        
        # 5. 生成答案
        prompt = f"""基于以下信息回答用户的问题。

相关文档内容：
{context}

用户问题：{query}

请用简洁、准确的中文回答："""
        
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[{'role': 'user', 'content': prompt}]
        )
        
        return response['message']['content'].strip()
    
    except Exception as e:
        return f"RAG查询失败：{e}"