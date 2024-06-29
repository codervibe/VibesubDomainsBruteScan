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
