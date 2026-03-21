# 面向对象练习
# 定义类
class Person:
    # 初始化方法
    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender

    # 字符串表示方法
    def __str__(self):
        return f"姓名：{self.name}，年龄：{self.age}，性别：{self.gender}"


# 定义类
class Cat:
    # 初始化方法
    def __init__(self, name, color):
        self.name = name
        self.color = color

    # 字符串表示方法
    def __str__(self):
        return f"猫的名字：{self.name}，颜色：{self.color}"


# 定义类 领养猫狗系统
class AdoptionSystem:
    system_version = "1.0"
    system_name = "领养猫狗系统"

    # 初始化方法
    def __init__(self):
        # 定义一个列表用来存储人的信息
        self.person_list = []
        # 定义一个列表用来存储猫的信息
        self.cat_list = []

    # 添加领养人信息
    def add_person(self):
        # 输入信息
        name = input("请输入领养人姓名：")
        age = int(input("请输入领养人年龄："))
        gender = input("请输入领养人性别：")

        # 领养人条件年纪需要大于18岁
        if age < 18:
            print("领养人年龄需要大于18岁,添加失败！")
            return

        # 创建Persond对象
        person = Person(name, age, gender)

        # 将人添加到列表中
        self.person_list.append(person)
        print("添加成功")

    # 添加猫的信息
    def add_cat(self):
        # 输入信息
        name = input("请输入猫的名字：")
        color = input("请输入猫的颜色：")

        # 创建Cat对象
        cat = Cat(name, color)

        # 将猫添加到列表中
        self.cat_list.append(cat)
        print("添加成功！")

    # 删除人的信息
    def delete_person(self):
        name = input("请输入要删除的领养人的名字：")
        for p in self.person_list:
            if p.name == name:
                self.person_list.remove(p)
                print("删除成功！")
                return
        print("没有找到该领养人，删除失败！")

    # 删除猫的信息
    def delete_cat(self):
        name = input("请输入要删除的猫的名字：")
        for c in self.cat_list:
            if c.name == name:
                self.cat_list.remove(c)
                print("删除成功！")
                return
        print("没有找到该猫，删除失败！")

    # 修改人的信息
    def update_person(self):
        name = input("请输入要修改的领养人的名字：")
        for p in self.person_list:
            if p.name == name:
                print(f"当前信息：{p}")
                age = int(input("请输入领养人年龄："))
                gender = input("请输入领养人性别：")
                # 更新人信息
                p.age = age
                p.gender = gender
                print("修改成功！")
                return
        print("没有找到该领养人，修改失败！")

    # 修改猫的信息
    def update_cat(self):
        name = input("请输入要修改的猫的名字：")
        for c in self.cat_list:
            if c.name == name:
                print(f"当前信息：{c}")
                color = input("请输入猫的颜色：")
                # 更新猫信息
                c.color = color
                print("修改成功！")
                return
        print("没有找到该猫，修改失败！")

    # 查询指定领养人的信息
    def query_person(self):
        name = input("请输入要查询的领养人的名字：")
        for p in self.person_list:
            if p.name == name:
                print(f"查询结果：{p}")
                return
        print("没有找到该领养人，查询失败！")

    # 查询指定猫的信息
    def query_cat(self):
        name = input("请输入要查询的猫的名字：")
        for c in self.cat_list:
            if c.name == name:
                print(f"查询结果：{c}")
                return
        print("没有找到该猫，查询失败！")

    # 查询所有领养人的信息
    def query_all_person(self):
        if not self.person_list:
            print("没有领养人信息！")
            return
        print("所有领养人信息：")
        for p in self.person_list:
            print(p)

    # 查询所有猫的信息
    def query_all_cat(self):
        if not self.cat_list:
            print("没有猫信息！")
            return
        print("所有猫信息：")
        for c in self.cat_list:
            print(c)

    # 运行系统
    def run(self):
        print(f"欢迎使用{self.system_name}，版本号：{self.system_version}")
        while True:
            print()
            print("1.添加领养人信息")
            print("2.添加猫的信息")
            print("3.删除领养人信息")
            print("4.删除猫的信息")
            print("5.修改领养人信息")
            print("6.修改猫的信息")
            print("7.查询指定领养人信息")
            print("8.查询指定猫的信息")
            print("9.查询所有领养人信息")
            print("10.查询所有猫的信息")
            print("0.退出系统")

            choice = input("请输入操作编号：")

            if choice == "1":
                self.add_person()
            elif choice == "2":
                self.add_cat()
            elif choice == "3":
                self.delete_person()
            elif choice == "4":
                self.delete_cat()
            elif choice == "5":
                self.update_person()
            elif choice == "6":
                self.update_cat()
            elif choice == "7":
                self.query_person()
            elif choice == "8":
                self.query_cat()
            elif choice == "9":
                self.query_all_person()
            elif choice == "10":
                self.query_all_cat()
            elif choice == "0":
                print("感谢使用，再见！")
                break
            else:
                print("输入有误，请重新输入！")


# 测试
if __name__ == "__main__":
    system = AdoptionSystem()
    system.run()