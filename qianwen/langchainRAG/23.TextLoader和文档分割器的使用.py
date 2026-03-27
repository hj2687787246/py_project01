from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

base_dir = Path(__file__).resolve().parent
text_path = base_dir / "data" / "practice_text.txt"

loader = TextLoader(
    file_path=str(text_path),
    encoding="utf-8",
)
documents = loader.load()
print(documents)
splitter = RecursiveCharacterTextSplitter(
    chunk_size= 500, # 分段最大的字符数
    chunk_overlap=50, # 分段之间允许重叠的字符数
    # 文本自然段落分割的依据符号
    separators=[
        "\n\n",  # 1. 段落（空行）
        "\n",  # 2. 换行
        "。", "！", "？",  # 3. 句子结束
        "；", "，",  # 4. 句内停顿
        " ",  # 5. 空格
        ""  # 6. 单字符（兜底）
    ],
    length_function=len # 统计字符的依据函数
)
split_docs = splitter.split_documents(documents)
print(len(split_docs))
for doc in split_docs:
    print(doc)