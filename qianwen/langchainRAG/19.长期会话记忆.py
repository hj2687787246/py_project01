import json, os
from typing import Sequence

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict

from langchain_community.chat_models import ChatTongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory

# message_to_dict: 单个消息对象（BaseMessage类实例） —> 字典
# messages_from_dict：[字典，字典...] -> [消息，消息...]
# AIMessage、HumanMessages、SystemMessage 都是BaseMessage的子类
class FileChatMessageHistory(BaseChatMessageHistory):

    def __init__(self, session_id, storage_path):
        self.session_id = session_id # 会话id
        self.storage_path = storage_path #不同会话记忆id的存储文件，所在的文件夹路径
        # 完整的文件路径
        self.file_path = os.path.join(self.storage_path, self.session_id)

        # 确保文件夹是存在的
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        # Sequence序列 类似list，tuple messages为继承的已有的消息列表
        all_messages = list(self.messages) # 已有的消息列表
        all_messages.extend(messages) # 新的和已有的融合成一个list

        # 将数据同步写入本地文件中
        # 类对象写入文件是二进制
        # new_message = []
        # for message in all_messages:
        #     d = messages_to_dict(message)
        #     new_message.append(d)

        # 为了方便，可以将BaseMessage消息转换为字典，借用json模块以json字符串写入文件
        # 官方message_to_dict：单个消息对象 BaseMessage类实例转换为字典
        new_message = [message_to_dict(message) for message in all_messages]
        # 将数据写入文件
        with open(self.file_path,"w",encoding="utf-8") as f:
            json.dump(new_message, f)

    @property      # @property装饰器将messages方法变成成员属性用
    def messages(self) -> list[BaseMessage]:
        # 当前文件内： list[字典]
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                messages_data = json.load(f)
                # messages_from_dict将[字典，字典...] -> [消息，消息...]
                return messages_from_dict(messages_data)
        except FileNotFoundError:
            return []

    def clear(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([], f)


model = ChatTongyi(model="qwen3-max")

# prompt = PromptTemplate.from_template(
#     "你需要根据会话历史回应用户问题，对话记录：{chat_history},用户提问：{input},请回答"
# )
prompt = ChatPromptTemplate.from_messages(
    [
        ("system","你需要根据会话记录回应用户问题，对话历史："),
        MessagesPlaceholder("chat_history"),
        ("human","请回答如下问题：{input}")
    ]
)
# 创建一个字符串解析器
str_parser = StrOutputParser()

def print_prompt(full_prompt):
    print("-"*20, full_prompt.to_string(), "-"*20)
    return full_prompt

# 创建一个链，将prompt和模型串起来，将结果解析成字符串
base_chain = prompt | print_prompt | model | str_parser

 # key就是session，value就是InMemoryChatMessageHistory类对象
# 实现通过会话id获取InMemoryChatMessageHistory
def get_history(session_id):
    return FileChatMessageHistory(session_id,"./chat_history")

# 创建一个新的链，对原有链增强功能，自动附加历史消息
conversation_chain = RunnableWithMessageHistory(
    base_chain, # 被增强的原有chain
    get_history, # 通过会话id获取InMemoryChatMessageHistory类对象
    input_messages_key="input", # 表示用户输入在模板中的占位符
    history_messages_key="chat_history" # 表示用户输入在模板中的占位符
)

if __name__ == '__main__':
    # 固定格式，添加langchain的配置，为当前程序配置所属的session_id
    session_config = {
        "configurable": {
            "session_id" : "user_001"
        }
    }
    res = conversation_chain.invoke({"input": "小明有2个猫"}, session_config)
    print("第一次执行:", res)

    res = conversation_chain.invoke({"input": "小明有1个狗"}, session_config)
    print("第二次执行:", res)

    res = conversation_chain.invoke({"input": "总共几个宠物 "}, session_config)
    print("第三次执行:", res)
