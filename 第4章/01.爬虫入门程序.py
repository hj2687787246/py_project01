import requests
from lxml import html
# 定义目标url
target_url = 'https://www.tiobe.com/tiobe-index/'
# 发送请求
response = requests.get(target_url)
# 打印请求结果
# print(response.text)

document = html.fromstring(response.text)
th_list = document.xpath("//table[@id='top20']/thead/tr/th/text()")
print(th_list)

tr_list = document.xpath("//table[@id='top20']/tbody/tr")
print(tr_list)
for tr in tr_list:
    # 获取td tr.xpath("./td/text()")
    td_list = tr.xpath("./td/text()")
    print(td_list)