import os
def test_os():
    # os模块3个基础方法
    print(os.listdir("./test")) # 列出路径下的内容
    print(os.path.isdir("./test/a")) # 判断制定路径是否为文件夹
    print(os.path.exists("./test/b")) # 判断指定路径是否存在

#
def get_files_recursion_from_dir(path):
    """
    从制定文件夹中使用递归的方式：获取全部的文件列表
    :param path: 被判断的文件
    :return: 包含全部的文件，如果目录不存在或者没有文件返回一个空list
    """
    print(f"当前判断的文件夹是：{path}")
    # 定义一个列表，存放文件列表
    file_list = []
    # 判断传入的路径地址是否存在
    if os.path.exists(path):
        # 遍历指定路径下的所有文件列表
        for f in os.listdir(path):
            # 将文件列表中每一个元素补全路径
            new_path = path + "/" +f
            # 判断指定路径是否为文件夹
            if os.path.isdir(new_path):
                # 进入到这里表示这个路径是文件夹不是文件
                # 将新的文件夹路径再次传入函数方法，进行下一次的文件列表获取，并将返回的结果拼接到file_list 中
                file_list += get_files_recursion_from_dir(new_path)
            else:
                # 不是文件夹，就将文件路径添加到file_list中
                file_list.append(new_path)
    else:
        # 如果传入的路径不存在，就返回空列表
        print(f"指定的目录{path},不存在")
        return []

    return file_list
if __name__ == '__main__':
    print(get_files_recursion_from_dir("./test"))