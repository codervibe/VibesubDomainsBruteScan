# VibesubDomainsBruteScan

高并发的DNS暴力枚举工具。


## 安装

~~~shell
git clone https://github.com/codervibe/VibesubDomainsBruteScan.git
pip install -r  requirements.txt
cd VibesubDomainsBruteScan/
python VibesubDomainsBruteScan.py
~~~

使用大字典，扫描qq.com


## 使用 ##

	Usage: VibesubDomainsBruteScan.py [options] target.com

	Options:
	--version             显示程序的版本号并退出
	-h, --help            显示此帮助消息并退出
	-f FILE               文件包含新的行分隔子，默认为subnames.txt。
	--full                全扫描，NAMES FILE subnames_full.txt将被用于brute
	-i, --ignore-intranet 忽略指向私有ip的域
	-w, --wildcard        在通配符测试失败后强制扫描
	-t THREADS, --threads=THREADS 扫描线程数，默认为500
	-p PROCESS, --process=PROCESS 扫描进程数，默认为6
    --no-https                    禁用从HTTPS证书获取域名，这可以节省一些时间
	-o OUTPUT, --output=OUTPUT    输出文件名。默认为{target}.txt		
## 更新日志
* [2024-06-29] 修复：
  1. 使用 Manager.Value 和 Manager.list 处理跨进程共享的数据，确保数据的一致性。
  2. 为每个进程创建独立的日志记录器，防止多进程日志冲突。
  3. 在 finally 块中清理临时目录，确保无论发生何种异常，临时目录都能被清理。
  4. 使用 Lock 确保在访问共享变量时的线程安全。
  5. 处理异步任务中的异常，确保任何一个子进程的异常都不会影响其他进程的执行。
* [2024-06-29] 升级：
  1. 配置选项验证：确保传入的配置参数有效。
  2. 日志记录改进：日志输出到文件，并保持标准输出。
  3. 性能优化：对扫描和存储进行优化。
  4. 用户界面改进：通过日志和控制台输出提供更好的用户体验。
  5. 代码模块化：拆分主逻辑，增强可维护性。
  