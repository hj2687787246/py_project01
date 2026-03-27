from langchain_community.document_loaders import JSONLoader

loader = JSONLoader(
    file_path="./data/company_nested.json",
    jq_schema=".projects.[].name", #.代表根目录 .[]代表根目录下所有列表
    text_content=False # 告知JSONLoader 我抽取的内容不是字符串
)

document = loader.load()
print(document)