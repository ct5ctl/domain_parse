import threading
import Tools
import socket
# from multiping import MultiPing  # root
from tcping import Ping

from Config import time_ping_max, file_url
import Resolvability

def api_judge_usability(url_post, time_max):
    # 保存该url到url.txt中
    flag_exist = False
    with open(file_url, "r") as fp_read:
        url_list = fp_read.readlines()
        for url in url_list:  # 先判断提交的url是否已存在于本地文件中
            url = url.strip()
            if url == url_post:
                flag_exist = True  # 提交的url已存在于本地文件中
                break
    if flag_exist is False:  # 本地文件中没有相同url，则在文件末尾追加该url
        with open(file_url, "a") as fp_addition:
            fp_addition.write("\n" + url_post)

    Resolvability.thread_task_parse_domain(url_post)
    result_json = Tools.read_result_file(url_post)
    result_json["Domain"] = url_post
    ip = socket.gethostbyname(url_post)  # 用socket模块获取ip
    ping = Ping(ip, 80, time_max)
    ping.ping(count=1)
    ret = ping.result.rows
    for r in ret:
        suc_flag = r[2]
        rtt = r[5]
    if suc_flag != 1:
        print("[%s]this addresse did not respond: %s" % (url, ip))
        result_json["Usability"] = False
    else:
        print("[%s]%s responded in %s" % (url, ip, rtt))
        result_json["Usability"] = True

    Tools.save_result_file(url_post, result_json)
    return result_json

def thread_ping(url, time_max, result_json):
    if len(result_json["IP set"]) > 0 and result_json["Parsability"] == True:
        ip = result_json["IP set"][0]
        ping = Ping(ip, 80, time_max)
        ping.ping(count=1)
        ret = ping.result.rows
        for r in ret:
            suc_flag = r[2]
            rtt = r[5]
        if suc_flag != 1:
            print("[%s]this addresse did not respond: %s" % (url, ip))
            result_json["Usability"] = False
        else:
            print("[%s]%s responded in %s" % (url, ip, rtt))
            result_json["Usability"] = True
    else:
        result_json["Parsability"] = False
        result_json["Usability"] = False



def thread_task_ping(url, time_max):
    Tools.create_result_file(url)  # 检查是否已经创建了result文件
    result_json = Tools.read_result_file(url)
    result_json["Domain"] = url
    ip = socket.gethostbyname(url)  # 用socket模块获取ip
    # # MultiPing方法需要root权限
    # mp = MultiPing([ip, ])  # 这个MultiPing模块可以直接ping多个ip，但因为采用多线程，只ping一个先
    # mp.send()
    # responses, no_responses = mp.receive(1)  # responses存放ping成功的ip和往返时延
    # if no_responses:  # no_responses存放所有ping失败的ip（这里最多只有一个）
    #     print("[%s]this addresse did not respond: %s" % (url, no_responses))
    #     result_json["Usability"] = False
    # else:
    #     for addr, rtt in responses.items():
    #         if rtt < time_max:
    #             print("[%s]%s responded in %f seconds" % (url, addr, rtt))
    #             result_json["Usability"] = True
    #         else:
    #             print("[%s]%s responded in %f seconds, overtime!" % (url, addr, rtt))
    ping = Ping(ip, 80, time_max)
    ping.ping(count=1)
    ret = ping.result.rows
    for r in ret:
        suc_flag = r[2]
        rtt = r[5]
    if suc_flag != 1:
        print("[%s]this addresse did not respond: %s" % (url, ip))
        result_json["Usability"] = False
    else:
        print("[%s]%s responded in %s" % (url, ip, rtt))
        result_json["Usability"] = True
        Tools.save_result_file(url, result_json)


def judge_usability(url_list):
    thread_list = []
    for url in url_list:
        url = url.strip()  # 一定记住要strip，否则解析不出ip
        if url != "":  # 有些行是全空的，需要判断
            t = threading.Thread(target=thread_task_ping, args=(url, time_ping_max))
            thread_list.append(t)
    for t in thread_list:
        t.start()
    for t in thread_list:  # 主进程等待所有子进程退出才退出
        t.join()
    print("-" * 50)


if __name__ == '__main__':
    thread_task_ping("www.baidu.com", 1)
