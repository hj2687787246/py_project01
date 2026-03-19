# NP16 发送offer
# 描述
# 某公司在面试结束后，创建了一个依次包含字符串 'Allen' 和 'Tom' 的列表offer_list，作为通过面试的名单。
# 请你依次对列表中的名字发送类似 'Allen, you have passed our interview and will soon become a member of our company.' 的句子。
# 但由于Tom有了其他的选择，没有确认这个offer，HR选择了正好能够确认这个offer的Andy，所以请把列表offer_list中 'Tom' 的名字换成 'Andy' ，
# 再依次发送类似 'Andy, welcome to join us!' 的句子。
# 输出描述：
# 按题目描述进行输出即可。Allen, you have passed our interview and will soon become a member of our company.
# Tom, you have passed our interview and will soon become a member of our company.
# Allen, welcome to join us!
# Andy, welcome to join us!
# 错误原因：
#     1.没有仔细看题目，忽略了需要把列表offer_list中 'Tom' 的名字换成 'Andy'
#     2.没有注意替换位置，导致输出不符合
#     3.获取列表元素写成了offer_list["Tom"] = "Andy"

offer_list = ["Allen","Tom"]
for offer in offer_list:
    print(f"{offer}, you have passed our interview and will soon become a member of our company.")
offer_list[1] = "Andy"
for offer in offer_list:
    print(f"{offer}, welcome to join us!")

