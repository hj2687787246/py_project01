# 读写取文件
# 打开文件
f = open("./resource/翻译.txt", "r", encoding="utf-8")
# 读取文件
print(f.read())
# 关闭文件
f.close()

# 打开文件，不存在就创建，存在就覆盖
f = open("./resource/静夜思.txt", "w", encoding="utf-8")
# 写入文件
f.write("静夜思(李白)\n\n")
f.write("窗前明月光，\n")
f.write("疑是地上霜。\n")
f.write("举头望明月，\n")
f.write("低头思故乡。")
# 关闭文件
f.close()

# 打开文件，不存在就创建，存在就覆盖
f = open("./resource/草.txt", "w", encoding="utf-8")
# 繁琐
try:
    # 写入文件
    f.write("草(王维)\n\n")
    f.write("长风破浪会有时，直挂云帆济沧海。\n")
    f.write("此时无路可退，何曾见人满地。\n")
    f.write("此时无路可退，何曾见人满地。\n")
    f.write("此时无路可退，何曾见人满地。")
finally:
    # 关闭文件
    f.close()

# 简洁 with方法 在with语句块中执行代码，执行结束后自动销毁上下文
with open("./resource/草.txt", "w", encoding="utf-8") as f:
    # 写入文件
    f.write("草(王维)\n\n")
    f.write("长风破浪会有时，直挂云帆济沧海。\n")
    f.write("此时无路可退，何曾见人满地。\n")
    f.write("此时无路可退，何曾见人满地。\n")
    f.write("此时无路可退，何曾见人满地。")
    # 关闭文件
    f.close()


