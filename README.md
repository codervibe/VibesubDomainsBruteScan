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
	--version             show program's version number and exit
	-h, --help            show this help message and exit
	-f FILE               File contains new line delimited subs, default is
			      subnames.txt.
	--full                Full scan, NAMES FILE subnames_full.txt will be used
			      to brute
	-i, --ignore-intranet
                        Ignore domains pointed to private IPs
	-w, --wildcard        Force scan after wildcard test failed
	-t THREADS, --threads=THREADS
				Num of scan threads, 500 by default
	-p PROCESS, --process=PROCESS
		                Num of scan process, 6 by default
	 --no-https            Disable get domain names from HTTPS cert, this can
		                save some time
	-o OUTPUT, --output=OUTPUT
		               Output file name. default is {target}.txt		
