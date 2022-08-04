# _*_ coding : utf-8 _*_
# @Author :Ct5Ct1
# @Project : 域名解析_0314

import time
# 导入本地模块
import Resolvability
import Usability
import Dynamicity
from Config import sleep_time, file_url


def multiprocessing_parse(file_url, sleep_time):
    while True:
        with open(file_url, "r") as fp:
            url_list = fp.readlines()                      # 获得url列表
        # 采用多线程对域名的各个特性进行分析
        Resolvability.judge_resolvability(url_list)        # 判断[可解析性]
        Usability.judge_usability(url_list)                # 判断[可用性]
        Dynamicity.judge_dynamicity_circularity(url_list)  # 判断[动态性]和[周期性],并推算[变化周期]和确定[ip固定集合]

        time.sleep(sleep_time)


def main():
    multiprocessing_parse(file_url, sleep_time)


if __name__ == "__main__":
    main()
