# 集合 set 无序的、不可重复、可修改
# 定义
s1 = {1,546,87,5,6,12,4}
print(s1)
print(type(s1))

s1 = {}
print(type(s1))

s1 = set()
print(type(s1))
# 选修足球学生名单
football_set = {"王林", "曾牛", "徐立国", "遁天", "天运子", "韩立", "厉飞雨", "乌丑", "紫灵"}
# 选修篮球学生名单
basketball_set = {"张铁", "墨居仁", "王林", "姜老道", "曾牛", "王蝉", "韩立", "天运子", "李化元", "厉飞雨", "云露"}
# 选修法语学生名单
french_set = {"许木", "王卓", "十三", "虎咆", "姜老道", "天运子", "红蝶", "厉飞雨", "韩立", "曾牛"}
# 选修艺术学生名单
art_set = {"遁天", "天运子", "韩立", "虎咆", "姜老道", "紫灵"}

# 1，找出同时选修了法语和艺术的学生
# fa_set = french_set.intersection(art_set)
# & 为并集运算符
fa_set = french_set &art_set
print("同时选修了法语和艺术的学生：",fa_set)

# 2，找出同时选修了所有四门课程的学生
# all_set = football_set.intersection(basketball_set).intersection(french_set).intersection(art_set)

all_set = football_set &basketball_set & french_set & art_set
print("同时选修了所有四门课程的学生：",all_set)

# 3.找出选修了足球，但是没有选修篮球的学生
fn_set = football_set.difference(basketball_set)
print("选修了足球，没有选修篮球的学生",fn_set)

# - 为差集运算符
fn_set = football_set - basketball_set
print("选修了足球，没有选修篮球的学生",fn_set)

# 方式3：集合推导式
fn_set = {i for i in football_set if i not in basketball_set}
print("选修了足球，没有选修篮球的学生",fn_set)
# 4．统计每一个学生选修的课程数量
# 4.1 统计所有学生 使用并集
all_set = football_set.union(basketball_set).union(french_set).union(fa_set)
print(all_set)
# | 为并集运算符
all_set = football_set | basketball_set | french_set | art_set
# 4.2 统计每个学生的课程数量 使用解包
all_list = [*football_set,*basketball_set,*french_set,*all_set]
for item in all_set:
    print(f"{item}参加的课程数量为：",all_list.count(item))

