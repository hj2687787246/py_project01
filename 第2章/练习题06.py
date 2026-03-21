#请你编写一个游戏角色移动控制系统，根据玩家输入的不同指令，控制游戏角色执行相应的动作（输出控制台）。
# 玩家输入 对应动作
instruction = input("请输入指令：")
match instruction:
    case "w" | "W":
        print("角色向上移动")
    case "s" | "S":
        print("角色向下移动")
    case "a" | "A":
        print("角色向左移动")
    case "d" | "D":
        print("角色向右移动")
    case " " | "空格":
        print("角色跳跃")
    case "j" | "J":
        print("角色攻击模板")
    case "esc" | "ESC":
        print("角色退出游戏")
    case _:
        print("无效操作")