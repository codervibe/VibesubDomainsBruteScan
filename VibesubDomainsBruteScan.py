#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import multiprocessing
import time
import signal
import os
import glob
import shutil
import platform
from lib.cmdline import parse_args

import warnings

warnings.simplefilter("ignore", category=UserWarning)
max_threads = 1000

# 定义版本号
VERSION = "2.43.16"  # 这里设置你的版本号

# 版本兼容性处理部分
# 检查Python版本，如果是Python 3.5及以上版本，导入相关模块
if sys.version_info.major >= 3 and sys.version_info.minor >= 5:
    import asyncio
    from lib.scanner_py3 import SubNameBrute
    from lib.common_py3 import (
        load_dns_servers, load_next_sub, print_msg, get_out_file_name,
        user_abort, wildcard_test, get_sub_file_path
    )

    if platform.system() == 'Windows':
        # Windows平台特殊处理，设置适当的事件循环策略
        if sys.version_info.minor >= 8 and hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        else:
            if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            max_threads = 200  # 限制最大线程数为200
else:
    # 如果是Python 2.x版本，导入对应的模块
    from lib.scanner_py2 import SubNameBrute
    from lib.common_py2 import (
        load_dns_servers, load_next_sub, print_msg, get_out_file_name,
        user_abort, wildcard_test, get_sub_file_path
    )

    if platform.system() == 'Windows':
        max_threads = 200  # 限制最大线程数为200


# 多进程扫描子域名的函数
def run_process(*params):
    signal.signal(signal.SIGINT, user_abort)  # 设置中断信号处理函数
    s = SubNameBrute(*params)  # 创建SubNameBrute对象
    s.run()  # 运行子域名枚举


# 显示帮助信息
def show_help():
    help_text = """
用法: python VibesubDomainsBruteScan.py [选项] <域名>

选项:
  -h, --help            显示此帮助信息并退出
  -f, --full-scan       启用全面扫描模式
  -t THREADS, --threads=THREADS
                        线程数 (默认: 10)
  -p PROCESSES, --process=PROCESSES
                        进程数 (默认: 6)
  -o OUTPUT, --output=OUTPUT
                        输出文件名 (默认: {domain}_result.txt)
  -w, --wildcard        跳过通配符检测
  --dns=DNS_SERVERS     指定DNS服务器 (默认: 系统默认DNS)
  --version             显示版本信息并退出
"""
    print(help_text)


# 主程序入口
if __name__ == '__main__':
    if '--version' in sys.argv:
        print("VibesubDomainsBruteScan 版本: " + VERSION)
        sys.exit(0)

    if len(sys.argv) == 1:
        show_help()
        sys.exit(0)

    options, args = parse_args()  # 解析命令行参数
    if options.threads > max_threads:
        options.threads = max_threads  # 限制线程数不超过最大值

    # 创建临时目录用于存储扫描结果
    root_path = os.path.dirname(os.path.abspath(__file__))
    tmp_dir = os.path.join(root_path, 'tmp/%s_%s' % (args[0], int(time.time())))
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    multiprocessing.freeze_support()  # 支持多进程冻结
    dns_servers = load_dns_servers()  # 加载DNS服务器列表
    next_subs = load_next_sub(options.full_scan)  # 加载子域名列表
    scan_count = multiprocessing.Value('i', 0)  # 创建多进程共享变量记录扫描数量
    found_count = multiprocessing.Value('i', 0)  # 创建多进程共享变量记录发现的子域名数量
    queue_size_array = multiprocessing.Array('i', options.process)  # 创建多进程共享数组记录队列大小

    try:
        print('[+] 进行通配符测试')
        if not options.w:
            # 进行通配符测试以确定域名
            domain = wildcard_test(args[0], dns_servers)
        else:
            domain = args[0]
        options.file = get_sub_file_path(options)  # 获取子域名字典文件路径
        print('[+] 启动 %s 个扫描进程' % options.process)
        print('[+] 扫描中，请稍候 ... \n')
        start_time = time.time()
        all_process = []
        for process_num in range(options.process):
            # 启动多进程进行子域名扫描
            p = multiprocessing.Process(
                target=run_process,
                args=(domain, options, process_num, dns_servers, next_subs,
                      scan_count, found_count, queue_size_array, tmp_dir)
            )
            all_process.append(p)
            p.start()

        char_set = ['\\', '|', '/', '-']
        count = 0
        while all_process:
            for p in all_process:
                if not p.is_alive():
                    all_process.remove(p)
            groups_count = 0
            for c in queue_size_array:
                groups_count += c
            msg = '[%s] 已发现 %s 个子域名，已扫描 %s 个，耗时 %.1f 秒，剩余 %s 个分组' % (
                char_set[count % 4], found_count.value, scan_count.value, time.time() - start_time, groups_count)
            print_msg(msg)  # 打印扫描进度
            count += 1
            time.sleep(0.3)  # 每0.3秒更新一次进度
    except KeyboardInterrupt as e:
        print('[错误] 用户中断扫描!')  # 用户中断扫描
        for p in all_process:
            p.terminate()
    except Exception as e:
        import traceback

        traceback.print_exc()  # 打印异常堆栈
        print('[错误] %s' % str(e))

    # 收集所有扫描结果并写入输出文件
    out_file_name = get_out_file_name(domain, options)
    all_domains = set()
    domain_count = 0
    with open(out_file_name, 'w') as f:
        for _file in glob.glob(tmp_dir + '/*.txt'):
            with open(_file, 'r') as tmp_f:
                for domain in tmp_f:
                    if domain not in all_domains:
                        domain_count += 1
                        all_domains.add(domain)  # cname查询可能导致重复的域名
                        f.write(domain)

    msg = '全部完成。共发现 %s 个子域名，扫描 %s 个，耗时 %.1f 秒。' % (
        domain_count, scan_count.value, time.time() - start_time)
    print_msg(msg, line_feed=True)  # 打印最终的扫描结果
    print('输出文件是 %s' % out_file_name)  # 打印输出文件路径
    try:
        shutil.rmtree(tmp_dir)  # 删除临时目录
    except Exception as e:
        pass  # 忽略删除临时目录时的异常
