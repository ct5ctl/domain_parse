import re
import threading
import time
import dns.resolver
import socket

import Config
import Tools
# dns.resolver.default_resolver=dns.resolver.Resolver(configure=False)
# dns.resolver.default_resolver.nameservers=['8.8.8.8']

# restful api的可解析性判断处理函数
def api_judge_resolvability(url_post):
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

    # 对提交的域名进行解析性判断
    Tools.create_result_file(url_post)
    result_json = Tools.read_result_file(url_post)
    result_json["Domain"] = url_post
    answer = dns.resolver.Resolver.resolve(url_post, "A", raise_on_no_answer=False, lifetime=1)  # raise_on_no_answer当查询无应答时是否触发异常
    if answer.rrset is not None:
        result_json["Parsability"] = True  # 【可解析性】
        for i in answer.response.answer:  # i的类型：dns.rrset.RRset
            for ip in i:
                ip = str(ip)
                # pattern = re.compile(r'(([1-9]?\d|1\d\d|2[0-4]\d|25[0-5])\.){3}([1-9]?\d|1\d\d|2[0-4]\d|25[0-5])')
                pattern = re.compile(r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}')
                if re.match(pattern, ip, flags=0):  # 正则ip格式(因为有些域名有CNAME，所以要用正则来匹配，筛选出ip）
                    time_now = time.time()
                    result_json["Result"][time_now] = ip  # 记录当前时间和当前ip到该域名的ip集中
                    if ip not in result_json["IP set"]:  # 若是新的未在ip固定集中的ip，则添加到ip固定集
                        result_json["IP set"].append(ip)
    else:
        result_json["Parsability"] = False
    Tools.save_result_file(url, result_json)
    return result_json["Parsability"], result_json["IP set"][0]


# all parse without stop
def thread_parse_domain(url, result_json, flag_succ_parse):
    # 整体解析-dns解析
    try:
        if flag_succ_parse["flag"] is False:
            return
        time_dns1 = time.time()
        answer = dns.resolver.resolve(url, "A", raise_on_no_answer=True, lifetime=Config.time_dns_max)  # raise_on_no_answer当查询无应答时是否触发异常
        time_dns2 = time.time()
        dns_time = time_dns2 - time_dns1
        print(dns_time)
        if answer.rrset is not None:
            result_json["Parsability"] = True  # 【可解析性】
            for i in answer.response.answer:  # i的类型：dns.rrset.RRset
                for ip in i:
                    ip = str(ip)
                    # pattern = re.compile(r'(([1-9]?\d|1\d\d|2[0-4]\d|25[0-5])\.){3}([1-9]?\d|1\d\d|2[0-4]\d|25[0-5])')
                    pattern = re.compile(r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}')
                    if re.match(pattern, ip, flags=0):  # 正则ip格式(因为有些域名有CNAME，所以要用正则来匹配，筛选出ip）
                        time_now = time.time()
                        result_json["Result"][time_now] = ip  # 记录当前时间和当前ip到该域名的ip集中
                        if ip not in result_json["IP set"]:  # 若是新的未在ip固定集中的ip，则添加到ip固定集
                            result_json["IP set"].append(ip)
        else:
            result_json["Parsability"] = False
    except Exception as err:
        print(err, url)
        result_json["Parsability"] = False
        result_json["IP set"] = []
        flag_succ_parse["flag"] = False


    # socket方法（不适合多线程，会阻塞线程）
    # try:
    #     ip_ex = Tools.my_gethostbyname_ex(url)  # 用socket模块获取ip
    #     ip_set = ip_ex[2]
    # except:
    #     ip_set = []
    #
    # if len(ip_set) != 0:
    #     result_json["Parsability"] = True  # 【可解析性】
    #     ip = ip_set[0].strip()
    #     time_now = time.time()
    #     result_json["Result"][time_now] = ip  # 记录当前时间和当前ip到该域名的ip集中
    #     result_json["IP set"] = ip_set        #
    # else:
    #     result_json["Parsability"] = False



def thread_task_parse_domain(url):
    # 线程任务：域名解析性判断
    Tools.create_result_file(url)
    result_json = Tools.read_result_file(url)
    result_json["Domain"] = url
    answer = dns.resolver.resolve(url, "A", raise_on_no_answer=False)   # raise_on_no_answer当查询无应答时是否触发异常
    if answer.rrset is not None:
        result_json["Parsability"] = True   # 【可解析性】
        for i in answer.response.answer:    # i的类型：dns.rrset.RRset
            for ip in i:
                ip = str(ip)
                # pattern = re.compile(r'(([1-9]?\d|1\d\d|2[0-4]\d|25[0-5])\.){3}([1-9]?\d|1\d\d|2[0-4]\d|25[0-5])')
                pattern = re.compile(r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}')
                if re.match(pattern, ip, flags=0):  # 正则ip格式(因为有些域名有CNAME，所以要用正则来匹配，筛选出ip）
                    time_now = time.time()
                    result_json["Result"][time_now] = ip    # 记录当前时间和当前ip到该域名的ip集中
                    if ip not in result_json["IP set"]:     # 若是新的未在ip固定集中的ip，则添加到ip固定集
                        result_json["IP set"].append(ip)
    else:
        result_json["Parsability"] = False
    # ip_ex = socket.gethostbyname_ex(url)  # 用socket模块获取ip
    # ip_set = ip_ex[2]
    # if len(ip_set) != 0:
    #     result_json["Parsability"] = True  # 【可解析性】
    #     ip = ip_set[0].strip()
    #     time_now = time.time()
    #     result_json["Result"][time_now] = ip  # 记录当前时间和当前ip到该域名的ip集中
    #     result_json["IP set"] = ip_set
    # else:
    #     result_json["Parsability"] = False
    Tools.save_result_file(url, result_json)


# 解析性判断
def judge_resolvability(url_list):
    thread_list = []
    for url in url_list:
        url = url.strip()    # 一定记住要strip，否则解析不出ip
        if url != "":        # 有些行是全空的，需要判断
            t = threading.Thread(target=thread_task_parse_domain, args=(url,))
            thread_list.append(t)
    for t in thread_list:
        t.start()
    for t in thread_list:   # 主进程等待所有子进程退出才退出
        t.join()


if __name__ == '__main__':
    thread_task_parse_domain("www.baidu.com")
    # test_json = {
    #     "Domain": "www.baidu.com"
    # }
    # api_judge_resolvability(test_json)
    # with open("url.txt", "a") as fp_addition:
    #     fp_addition.write("\n" + test_json["Domain"])
    pass