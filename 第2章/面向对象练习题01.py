# 采用面向对象的编程思想，完成教务管理系统的开发。教务管理系统可以管理在校学生的成绩信息，通过控制台菜单与用户交互，具体的功能如下：
# 1．添加学生成绩：根据输入的学生姓名、语文成绩、数学成绩、英语成绩，记录在系统中
# 2．修改学生成绩：根据输入的学生姓名，修改对应的学生成绩
# 3．删除学生成绩：根据输入的学生姓名，删除对应的学生成绩
# 4．查询指定学生成绩：根据输入的学生姓名，查找对应的学生成绩，并输出
# 5．展示全部学生成绩：展示出系统中所有学生的成绩

#学生类
class Student:
    #初始化
    def __init__(self, name,chinese,math,english):
        self.name = name
        self.chinese = chinese
        self.math = math
        self.english = english
    #转字符串
    def __str__(self):
        return f"姓名：{self.name}|语文：{self.chinese}|数学：{self.math}|英语：{self.english}"
    #修改学生成绩
    def update_score(self,chinese,math,english):
        #判断传入的参是否为空
        if chinese is not None:
            self.chinese = chinese
        if math is not None:
            self.math = math
        if english is not None:
            self.english = english

#教务系统
class EnuManagement:
    system_version = "1.0"
    system_name = "教务系统"

    #初始化
    def __init__(self):
        #定义一个列表
        self.student_list = []
    #添加学生成绩
    def add_student(self):
        name = input("请输入学生姓名：")
        #判断学生姓名是否存在，如果存在，则添加失败
        for s in self.student_list:
            if s.name == name:
                print("该学生已经存在，添加失败！")
                return
        chinese = int(input("请输入学生语文成绩："))
        math = int(input("请输入学生数学成绩："))
        english = int(input("请输入学生英语成绩："))

        #判断分数是否在0-100之间
        if 0<= chinese <=100 and 0<= math <=100 and 0<= english <= 100:
            #创建Student对象
            stu = Student(name,chinese,math,english)
            #添加到列表中去
            self.student_list.append(stu)
            print("添加成功！")
            return
        print("分数不在0-100之间")

    #修改学生成绩
    def update_student(self):
        name = input("请输入学生姓名：")
        #判断学生是否存在
        for s in self.student_list:
            if s.name == name:
                print(f"当前成绩：{s}")

                chinese = int(input("请输入学生语文成绩："))
                math = int(input("请输入学生数学成绩："))
                english = int(input("请输入学生英语成绩："))
                #判断分数是否在0-100之间
                if 0<= chinese <=100 and 0<= math <=100 and 0<= english <=100:
                    #调用update_score方法
                    s.update_score(chinese,math,english)
                    print("学生成绩修改成功！")
                    print("修改后的成绩：",s)
                    return
                else:
                    print("分数不在0-100之间")
                    return
        print("未找到学生，修改失败")

    #删除学生成绩
    def del_student(self):
        name = input("请输入学生姓名：")
        #判断学生是否存在
        for s in self.student_list:
            if s.name == name:
                self.student_list.remove(s)
                print("删除成功！")
                return
        print("学生不存在！")

    #查询制定学生成绩
    def query_student(self):
        name = input("请输入学生姓名：")
        # 判断学生是否存在
        for s in self.student_list:
            if s.name == name:
                #打印制定学生信息
                print(f"学生信息：{s}")
                return
        print("学生不存在！")

    #展示全部学生信息
    def show_student(self):
        for s in self.student_list:
            print(s)

    #运行系统
    def run(self):
        print(f"欢迎使用{self.system_name}{self.system_version}")

        while True:
            print()
            print("# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #")
            print("1.添加学生 2.修改学生 3.删除学生 4.查询学生 5.查询所有学生 6.退出系统")
            print("# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #")
            print()
            choice = int(input("请输入指令："))
            match choice:
                case 1: #添加学生
                    self.add_student()
                case 2:
                    self.update_student()
                case 3:
                    self.del_student()
                case 4:
                    self.query_student()
                case 5:
                    self.show_student()
                case 6:
                    print("bye~~~")
                    break
                case _:
                    print("错误指令")

#测试
if __name__ == '__main__':
    #创建对象
    edu_management = EnuManagement()
    edu_management.run()

