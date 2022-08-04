from flask import jsonify

import Tools
from Config import file_url
import os
import json


def get_all_urls():
    url_json = {}
    with open(file_url, "r") as fp:
        url_list = fp.readlines()
    index = 0;
    for url in url_list:
        url = url.strip()
        i = "第%d个url" % index
        if url != "":
            url_json[i] = url
        index += 1
    return url_json


def get_all_info():
    info_json = {}
    file_name_list = os.listdir("Result")
    index = 1
    for file_name in file_name_list:
        if file_name.strip() == "":
            break
        file_name = os.path.join("Result", file_name.strip())
        index_str = "第%d个域名" % index
        index += 1
        info_json[index_str] = {}
        with open(file_name, "r") as fp:
            ret_json = json.load(fp)
        info_json[index_str]["Domain"] = ret_json["Domain"]
        info_json[index_str]["Parsability"] = ret_json["Parsability"]
        info_json[index_str]["Usability"] = ret_json["Usability"]
        info_json[index_str]["Dynamicity"] = ret_json["Dynamicity"]
        info_json[index_str]["Circularity"] = ret_json["Circularity"]
        info_json[index_str]["IP Change Cycle"] = ret_json["IP Change Cycle"]
        info_json[index_str]["IP set"] = ret_json["IP set"]
    return info_json


def delete_info(request_json):
    return_json = {}
    if request_json["Delete_all"] is False:
        # 只是删除单个域名的解析信息
        url_delete = request_json["Domain"].strip()
        flag_suc = Tools.delete_result(url_delete)
        if flag_suc is True:
            return_json["Msg："] = "成功删除目标域名的解析信息。"
        else:
            return_json["Msg："] = "删除失败！目标域名的解析信息不存在。"
        return return_json
    else:
        # 删除全部域名的解析信息
        flag_suc = Tools.delete_all_result()
        if flag_suc is True:
            return_json["Msg："] = "成功删除所有域名的解析信息。"
        else:
            return_json["Msg："] = "删除失败！不存在解析信息。"
        return return_json


def add_url(url_post):
    # 保存该url到url.txt中
    flag_exist = False
    with open(file_url, "r") as fp_read:
        url_list = fp_read.readlines()
        for url in url_list:  # 先判断提交的url是否已存在于本地文件中
            url = url.strip()
            if url == url_post:
                flag_exist = True  # 提交的url已存在于本地文件中
                return jsonify(结果="所提交url已存在")
    if flag_exist is False:  # 本地文件中没有相同url，则在文件末尾追加该url
        with open(file_url, "a") as fp_addition:
            fp_addition.write("\n" + url_post)
        return jsonify(结果="提交url成功")


def del_url(url_del):
    flag_exist = False
    with open(file_url, "r") as fp_read:
        url_list = fp_read.readlines()
        url_list_new = []
        for url in url_list:  # 先判断提交的url是否已存在于本地文件中
            url = url.strip()
            if url == url_del:
                flag_exist = True  # 本地文件中存在要删除的url
                continue
            url_list_new.append(url + "\n")
    if flag_exist is False:  # 本地文件中没有要删除的url
        return {"结果": "删除失败，无所要删除的url"}
    with open(file_url, "w") as fp_write:
        for row in url_list_new:
            fp_write.write(row)
    return {"结果": "删除成功"}


if __name__ == '__main__':
    # get_all_urls()
    # get_all_info()
    # ret = del_url("br123")
    # print(ret)
    pass