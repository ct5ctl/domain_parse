import json
import os

from shutil import copyfile
import timeout_decorator
import socket
import Config

from_path = "template.json"     #模板文件路径

# # 限制域名解析的时间
# @timeout_decorator.timeout(seconds=1)
# def my_gethostbyname_ex(url):
#     return socket.gethostbyname_ex(url)


def create_result_file(url):
    to_path = os.path.join("Result", url + ".json")
    if not os.path.exists(to_path):
        copyfile(from_path, to_path)


def read_result_file(url):
    file_path = os.path.join("Result", url + ".json")
    with open(file_path, "r") as fp:
        result_json = json.load(fp)
        return result_json


def save_result_file(url, result_json):
    file_path = os.path.join("Result", url + ".json")
    with open(file_path, "w") as fp:
        json.dump(result_json, fp)


def delete_result(url_delete):
    file_name_list = os.listdir("Result")
    for file_name in file_name_list:
        if file_name.strip()[0:-5] == url_delete:
            file_name = os.path.join("Result", file_name)
            os.remove(file_name)
            return True
    return False


def delete_all_result():
    file_name_list = os.listdir("Result")
    if len(file_name_list) == 0:
        return False
    for file_name in file_name_list:
        file_name = os.path.join("Result", file_name)
        os.remove(file_name)
    return True

if __name__ == '__main__':
    # create_result_file("www.bi.com")
    # read_result_file("www.bi.com")
    # delete_result("www.baidu.com.json")
    # print("www.baidu.com.json"[0:-5])
    # delete_all_result()
    pass