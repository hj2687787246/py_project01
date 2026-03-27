from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader

base_dir = Path(__file__).resolve().parent
data_dir = base_dir / "data"

plain_pdf_path = data_dir / "practice_plain.pdf"
encrypted_pdf_path = data_dir / "practice_encrypted_123465.pdf"

# 1. 读取普通 PDF
plain_loader = PyPDFLoader(
    file_path=str(plain_pdf_path),
    mode="single", #single模式，不管多少页都只返回一个Documents对象
)
plain_documents = plain_loader.load()
print("普通 PDF 读取结果：")
print(plain_documents)

print("-" * 80)

# 2. 读取带密码的 PDF
encrypted_loader = PyPDFLoader(
    file_path=str(encrypted_pdf_path),
    mode="page", # 默认为page模式，每个页面形成一个Documents对象
    password="123465",
)

i = 0
for doc in encrypted_loader.lazy_load():
    i += 1
    print("加密 PDF 读取结果：",i)
    print(doc)
