import pandas as pd
import streamlit as st

# 页面配置
st.set_page_config(
    # 网页标题
    page_title="狸花猫介绍",
    # 网页图标
    page_icon="🧊",
    # 布局 wide：沾满整个区域
    layout="wide",
    # 控制侧边栏的状态
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.codefather.cn/",
        'About': "# 这是一个streamlit的入门程序!"
    }
)

# 大标题
st.title("狸花猫介绍")
st.title("狸花猫是中国本土原生的纯种猫，也是中华田园猫中最具代表性的品类，拥有超千年的繁育历史，是历经自然筛选留存的优良本土猫种，也是首个获得国际爱猫联合会（CFA）认证的中国本土猫品种。")
st.title("它标志性的被毛以黑棕相间的虎斑纹为主，常见鱼骨纹、蝴蝶纹两种经典纹路，短毛浓密顺滑、光泽感强；体型矫健匀称，肌肉线条紧实，面部呈利落的楔形，杏核状的眼睛多为黄绿、棕黄等色调，眼神灵动锐利，自带英气。")
st.title("狸花猫天生具备极强的捕猎天赋，自古便是农户护粮防鼠的好帮手。如今作为伴侣宠物，它性格独立清醒，不娇气粘人，却对主人极度忠诚，认主后温顺亲人。同时它环境适应力、抗病能力远超多数外来品种猫，体质强健易饲养，是兼具颜值与实用性的国民伴侣猫。")
# 图片
st.image("./resource/狸花猫.png")
# 音频

# 视频

# 表格
table_matrix = pd.DataFrame({
    "姓名" : ["何杰","李知玉","潘科","段小坤"],
    "语文" : [96,66,77,66],
    "数学" : [85,84,47,68],
    "英语" : [95,77,75,76],
},index=[1,2,3,4])
st.table(table_matrix)

# 输入框

title = st.text_input("请输入信息:","不知道")
st.write("这是刚刚输入的信息：",title)
