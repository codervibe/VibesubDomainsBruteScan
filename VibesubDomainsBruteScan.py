#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import asyncio
import time
import signal
import os
import glob
import shutil
import platform
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager, Lock
from lib.cmdline import parse_args
from lib.scanner_py3 import SubNameBrute
from lib.common_py3 import load_dns_servers, load_next_sub, print_msg, get_out_file_name, \
    user_abort, wildcard_test, get_sub_file_path
import logging

# 配置日志
log_file = 'scan.log'
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s', handlers=[
    logging.FileHandler(log_file),
    logging.StreamHandler()
])

# 配置常量
MAX_THREADS = 1000 if platform.system() != 'Windows' else 200

def run_process(params):
    signal.signal(signal.SIGINT, user_abort)
    s = SubNameBrute(*params)
    s.run()

def setup_logging():
    logger = logging.getLogger()
    handler = logging.FileHandler('scan.log')
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

async def main():
    options, args = parse_args()
    if options.threads > MAX_THREADS:
        options.threads = MAX_THREADS

    # 创建临时目录
    root_path = os.path.dirname(os.path.abspath(__file__))
    tmp_dir = os.path.join(root_path, f'tmp/{args[0]}_{int(time.time())}')
    os.makedirs(tmp_dir, exist_ok=True)

    dns_servers = load_dns_servers()
    next_subs = load_next_sub(options.full_scan)

    manager = Manager()
    scan_count = manager.Value('i', 0)
    found_count = manager.Value('i', 0)
    queue_size_array = manager.list([0] * options.process)
    lock = Lock()

    try:
        logging.info('Running wildcard test')
        domain = wildcard_test(args[0], dns_servers) if not options.w else args[0]
        options.file = get_sub_file_path(options)
        logging.info(f'Starting {options.process} scan processes')
        logging.info('Please wait while scanning ...')

        start_time = time.time()

        # 异步扫描
        loop = asyncio.get_running_loop()
        with ProcessPoolExecutor(max_workers=options.process) as executor:
            tasks = [
                loop.run_in_executor(
                    executor, run_process,
                    (domain, options, process_num, dns_servers, next_subs, scan_count, found_count, queue_size_array, tmp_dir, lock)
                ) for process_num in range(options.process)
            ]

            await asyncio.gather(*tasks)

            for count in range(len(tasks)):
                groups_count = sum(queue_size_array)
                msg = f'[{"/-\\|"[count % 4]}] {found_count.value} found, {scan_count.value} scanned in {time.time() - start_time:.1f} seconds, {groups_count} groups left'
                logging.info(msg)
                await asyncio.sleep(0.3)

    except KeyboardInterrupt:
        logging.error('User aborted the scan!')
    except Exception as e:
        logging.error(f'Error: {str(e)}', exc_info=True)
    finally:
        # 确保临时目录被清理
        try:
            shutil.rmtree(tmp_dir)
        except Exception as e:
            logging.warning(f'Failed to remove tmp dir: {e}')

    out_file_name = get_out_file_name(domain, options)
    all_domains = set()
    domain_count = 0

    with open(out_file_name, 'w') as f:
        for _file in glob.glob(os.path.join(tmp_dir, '*.txt')):
            with open(_file, 'r') as tmp_f:
                for domain in tmp_f:
                    if domain not in all_domains:
                        domain_count += 1
                        all_domains.add(domain)
                        f.write(domain)

    msg = f'All Done. {domain_count} found, {scan_count.value} scanned in {time.time() - start_time:.1f} seconds.'
    logging.info(msg)
    logging.info(f'Output file is {out_file_name}')


if __name__ == '__main__':
    asyncio.run(main())
