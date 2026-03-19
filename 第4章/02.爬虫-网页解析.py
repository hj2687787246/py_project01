from lxml import html
# 读取html文件

with open('resources/table_practice.html', 'r', encoding='utf-8') as f:
    html_text = f.read()
    # 解析html文本，将其转换为一个文档对象
    document = html.fromstring(html_text)

    # 解析表头th - xpath语法
    th_list = document.xpath('//table/thead/tr/th/text()')
    print(th_list)

    # 解析表体tr - xpath语法
    tr_list = document.xpath('//table/tbody/tr/td/text()')
    print(tr_list)

    # 解析td - xpath语法
    tr_list = document.xpath('//table/tbody/tr')
    # 遍历tr
    for tr in tr_list:
        # 获取td
        #  // 从任意节点查找元素 . 当前节点 / 从根节点查找元素 ./ 当前节点
        td_list = tr.xpath('./td/text()')
        print(td_list)
