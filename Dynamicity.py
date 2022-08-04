import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import Tools
import Resolvability
import Usability
from Config import time_ping_max, file_url, threads_max_num


def api_judge_dynamicity(url_post):
    # 保存该url到url.txt中
    flag_exist = False
    with open("url.txt", "r") as fp_read:
        url_list = fp_read.readlines()
        for url in url_list:        # 先判断提交的url是否已存在于本地文件中
            url = url.strip()
            if url == url_post:
                flag_exist = True   # 提交的url已存在于本地文件中
                break
    if flag_exist is False:         # 本地文件中没有相同url，则在文件末尾追加该url
        with open("url.txt", "a") as fp_addition:
            fp_addition.write("\n" + url_post)

    Tools.create_result_file(url_post)  # 检查是否已经创建了result文件
    result_json = Tools.read_result_file(url_post)
    if result_json["Domain"] == "":
        # Result文件的Domain字段为空，说明该文件是刚刚被创建的，里面没有任何数据
        # 此时需要调用另外两个模块的函数，将数据填入该域名的json文件后再重新读取
        for i in range(10):      # 要对域名进行多次解析，收集尽可能多的ip以分析[动态特性]
            Resolvability.thread_task_parse_domain(url_post)
        Usability.thread_task_ping(url_post, time_ping_max)
        result_json = Tools.read_result_file(url_post)

    if len(result_json["IP set"]) > 1:  # [动态性]判断
        result_json["Dynamicity"] = True
    else:
        result_json["Dynamicity"] = False
    last_ip = ""
    ip_change_rule_list = []  # 记录ip的变化
    time_change_rule_list = []  # 记录ip的变化的时间
    for ip_time, ip in result_json["Result"].items():  # 用items方法得到字典的键和值
        if ip != last_ip:  # 若ip变化，则记录到新列表中
            ip_change_rule_list.append(ip)  # 两个列表相同索引中的值是对应的，方便之后计算更换周期
            time_change_rule_list.append(ip_time)
    # 对ip_change_rule_list进行判断，看ip变化是否有规律
    flag_circularity, change_cycle = judge_circularity(ip_change_rule_list, time_change_rule_list)  # 判断[周期性]
    if flag_circularity is True and result_json["Dynamicity"] is True:  # 有动态性且有周期性
        print("[%s]该域名有动态性且IP变化具有周期性，周期为：%.04f秒" % (url_post, change_cycle))
        result_json["IP Change Cycle"] = change_cycle
        result_json["Circularity"] = True
    elif flag_circularity is False and result_json["Dynamicity"] is True:  # 有动态性但没有周期性
        print("[%s]该域名有动态性但IP变化没有周期性" % url_post)
    else:
        print("[%s]该域名没有动态性" % url_post)
        result_json["IP Change Cycle"] = "0"  # 固定ip的更换周期看作是0
        result_json["Circularity"] = True
    Tools.save_result_file(url_post, result_json)
    return result_json


def thread_parse_result(url, result_json):
    # 完整调用-动态性解析
    if len(result_json["IP set"]) > 1:  # [动态性]判断
        result_json["Dynamicity"] = True
    else:
        result_json["Dynamicity"] = False
    last_ip = ""
    ip_change_rule_list = []  # 记录ip的变化
    time_change_rule_list = []  # 记录ip的变化的时间
    for ip_time, ip in result_json["Result"].items():  # 用items方法得到字典的键和值
        if ip != last_ip:  # 若ip变化，则记录到新列表中
            ip_change_rule_list.append(ip)  # 两个列表相同索引中的值是对应的，方便之后计算更换周期
            time_change_rule_list.append(ip_time)
    # 对ip_change_rule_list进行判断，看ip变化是否有规律
    flag_circularity, change_cycle = judge_circularity(ip_change_rule_list, time_change_rule_list)  # 判断[周期性]
    if flag_circularity is True and result_json["Dynamicity"] is True:  # 有动态性且有周期性
        print("[%s]该域名有动态性且IP变化具有周期性，周期为：%.04f秒" % (url, change_cycle))
        result_json["IP Change Cycle"] = change_cycle
        result_json["Circularity"] = True
    elif flag_circularity is False and result_json["Dynamicity"] is True:  # 有动态性但没有周期性
        print("[%s]该域名有动态性但IP变化没有周期性" % url)
    else:
        print("[%s]该域名没有动态性" % url)
        result_json["IP Change Cycle"] = "0"  # 固定ip的更换周期看作是0
        result_json["Circularity"] = True



def thread_task_parse_all(url):
    # 完整调用-线程执行函数
    Tools.create_result_file(url)  # 检查是否已经创建了result文件
    result_json = Tools.read_result_file(url)
    if result_json["Domain"] == "":
        # Result文件的Domain字段为空，说明该文件是刚刚被创建的，里面没有任何数据
        # 此时需要调用另外两个模块的函数，将数据填入该域名的json文件后再重新读取
        result_json["Domain"] = url
        flag_succ_parse = {"flag": True}
        for i in range(10):  # 要对域名进行多次解析，收集尽可能多的ip以分析[动态特性]
            Resolvability.thread_parse_domain(url, result_json, flag_succ_parse)    # dns解析
            if flag_succ_parse["flag"] is False:
                # 若域名解析失败，则无需进行之后的解析判断
                Tools.save_result_file(url, result_json)
                return result_json
        Usability.thread_ping(url, time_ping_max, result_json)     # ping
    thread_parse_result(url, result_json)                          # 动态性解析
    Tools.save_result_file(url, result_json)
    return result_json


def api_judge_dynamicity_all():
    # api函数-实现对整个url文件的完整解析
    thread_list = []    # 线程列表
    executor = ThreadPoolExecutor(max_workers=threads_max_num)
    with open(file_url, "r") as fp:
        url_list = fp.readlines()  # 获得url列表
    for url in url_list:
        url = url.strip()  # 一定记住要strip，否则解析不出ip
        if url != "":  # 有些行是全空的，需要判断
            # t = threading.Thread(target=thread_task_parse_all, args=(url,))
            t = executor.submit(thread_task_parse_all, url)
            thread_list.append(t)
    # for t in thread_list:
    #     t.start()
    # for t in thread_list:  # 主进程等待所有子进程退出才退出
    #     t.join()
    # 读json文件返回给前端
    index = 1
    info_json = {}
    for task in thread_list:
        index_str = "第%d个域名" % index
        index += 1
        info_json[index_str] = {}
        info_json[index_str]["Domain"] = task.result()["Domain"]
        info_json[index_str]["Parsability"] = task.result()["Parsability"]
        info_json[index_str]["Usability"] = task.result()["Usability"]
        info_json[index_str]["Dynamicity"] = task.result()["Dynamicity"]
        info_json[index_str]["Circularity"] = task.result()["Circularity"]
        info_json[index_str]["IP Change Cycle"] = task.result()["IP Change Cycle"]
        info_json[index_str]["IP set"] = task.result()["IP set"]
    return info_json



# 周期性判断思路：
# 1.对变化规律列表进行遍历，用两个指针指向列表中任意不同位置的两相同ip，并一起向后遍历，每后移一次就再比较一次，
# 2.比较时：若所指ip不同，则两指针归位并重新找相同ip进行相同上述操作；若相同，则继续后移并比较
# 3.当前一指针移到后一指针的最初位置时,初步得到周期（后一指针初试位置的时间-前一指针初始位置的时间）
# 4.继续遍历比较，直到后一指针到达列表的末尾，若均匹配成功，则得到周期，且认为具有周期性；
#   若该过程中出现了匹配失败，则依然回到原位置，回到1继续匹配
def judge_circularity(ip_change_rule_list, time_change_rule_list):
    flag_circularity = False
    change_cycle = None
    change_cycle_temp = None
    for i in range(len(ip_change_rule_list)):
        for j in range(i + 1, len(ip_change_rule_list)):
            if ip_change_rule_list[i] == ip_change_rule_list[j]:
                i_old = i   #记录i和j的当前位置，以便匹配失败时归位
                j_old = j
                change_cycle_temp = float(time_change_rule_list[j_old]) - float(time_change_rule_list[i_old])
                while ip_change_rule_list[i] == ip_change_rule_list[j]:
                    i += 1
                    j += 1
                    if j == len(ip_change_rule_list):
                        break
                if j == len(ip_change_rule_list) and i >= j_old:
                    flag_circularity = True
                    change_cycle = change_cycle_temp
                    break
                else:
                    j = j_old
                    i = i_old
        if flag_circularity is True:
            break
    return flag_circularity, change_cycle       #返回周期性标志和周期


# 模块独立调用的线程函数
def thread_task_parse_result(url):
    Tools.create_result_file(url)  # 检查是否已经创建了result文件
    result_json = Tools.read_result_file(url)
    if result_json["Domain"] == "":  # Result文件的Domain字段为空，说明该文件是刚刚被创建的，里面没有任何数据
        print("[%s]该域名的Result文件无数据，无法解析动态特性" % url)
        return
    if len(result_json["IP set"]) > 1:      # [动态性]判断
        result_json["Dynamicity"] = True
    else:
        result_json["Dynamicity"] = False
    last_ip = ""
    ip_change_rule_list = []   # 记录ip的变化
    time_change_rule_list = []   # 记录ip的变化的时间
    for ip_time, ip in result_json["Result"].items():  # 用items方法得到字典的键和值
        if ip != last_ip:                            # 若ip变化，则记录到新列表中
            ip_change_rule_list.append(ip)           # 两个列表相同索引中的值是对应的，方便之后计算更换周期
            time_change_rule_list.append(ip_time)
    # 对ip_change_rule_list进行判断，看ip变化是否有规律
    flag_circularity, change_cycle = judge_circularity(ip_change_rule_list, time_change_rule_list)  # 判断[周期性]
    if flag_circularity is True and result_json["Dynamicity"] is True:  # 有动态性且有周期性
        print("[%s]该域名有动态性且IP变化具有周期性，周期为：%.04f秒" % (url, change_cycle))
        result_json["IP Change Cycle"] = change_cycle
        result_json["Circularity"] = True
    elif flag_circularity is False and result_json["Dynamicity"] is True:  # 有动态性但没有周期性
        print("[%s]该域名有动态性但IP变化没有周期性" % url)
    else:
        print("[%s]该域名没有动态性" % url)
        result_json["IP Change Cycle"] = "0"    # 固定ip的更换周期看作是0
        result_json["Circularity"] = True
    Tools.save_result_file(url, result_json)


def judge_dynamicity_circularity(url_list):
    thread_list = []
    for url in url_list:
        url = url.strip()  # 一定记住要strip，否则解析不出ip
        if url != "":      # 有些行是全空的，需要判断
            t = threading.Thread(target=thread_task_parse_result, args=(url,))
            thread_list.append(t)
    for t in thread_list:
        t.start()
    for t in thread_list:  # 主进程等待所有子进程退出才退出
        t.join()
    print("="*100)


if __name__ == '__main__':
    # thread_task_parse_result("www.baidu.com")
    # ip_change_rule_list = ["a", "b", "c", "a", "a", "b", "c", "a", "a", "d"]
    # time_change_rule_list = [1, 3, 5, 6, 7, 11, 12, 15, 16, 18]
    # flag, cir = judge_circularity(ip_change_rule_list, time_change_rule_list)
    # print(flag, cir)
    # api_judge_dynamicity("www.52pojie.cn")
    # api_judge_dynamicity_all()
    pass
