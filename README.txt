# 项目功能
对批量域名的特性解析（包括：可解析性、可用性、动态性、周期性、周期、ip固定集）

# 关键路径（虚拟机中）
项目目录：/home/ct5ctl/Desktop/域名解析_0314
存放待解析域名的文本文件：/home/ct5ctl/Desktop/域名解析_0314/url.txt
解析结果存放文件夹：/home/ct5ctl/Desktop/域名解析_0314/Result
依赖文件:/home/ct5ctl/Desktop/域名解析_0314/requirements.txt
uwsgi配置文件：/home/ct5ctl/Desktop/域名解析_0314/run.ini
uwsgi日志：/home/ct5ctl/Desktop/域名解析_0314/logs/uwsgi.log
nginx配置文件：/etc/nginx/nginx.conf
nginx日志目录：/var/log/nginx/

# 项目运行
1.用xshell连接虚拟机
2.启动服务
	1）启动uwsgi：/home/ct5ctl/Desktop/域名解析_0314# uwsgi --ini run.ini
	2）启动nginx：/usr/local/nginx/sbin# sudo nginx
3.使用api
	1./api/resolvavility  
		1.方法：[POST]
			以JSON格式提交域名，获得该域名的[可解析性]的解析结果
			eg:{ "Domain": "www.github.com" }
	2./api/usability
		1.方法：[POST]
			以JSON格式提交域名，获得该域名的[可用性]的解析结果
	3./api/dynamicity
		1.方法：[POST]
			以JSON格式提交域名，获得该域名的[可用性]的解析结果
		**2.方法：[GET]
			对服务器域名文件url.txt中所有域名进行解析（各特性都会进行解析）
	4./api/url
		1.方法：[GET]
			获得服务器的url.txt中所有域名
		2.方法：[POST]
			以JSON格式提交域名，新增该域名到url.txt中
		3.方法：[DELETE]
			以JSON格式提交域名，将该域名从url.txt中删除
	5./api/all_info
		1.方法：[GET]
			获得所有已有的解析结果
		2.方法：[POST]
			删除一个或全部解析结果（由标志位“Delete_all”决定）
			eg:{ "Domain": "",   
			       "Delete_all": true}
