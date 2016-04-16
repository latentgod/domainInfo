## domainInfo
The program is use to get doamin information that waf,subdomain,ip,Zone Transfers ...

> 几乎都是基于现成成熟的产品进行整合调用，比如检测是基于wafw00f

> 所以，如果你首先得安装一些软件，请按照下面的方法安装。

### 安装

>+ dnsenum 参考链接: http://blog.csdn.net/star_xiong/article/details/37761239
>+ wafw00f 参考链接: http://www.freebuf.com/articles/web/21744.html

>其中也有些第三方库：

>+ pylsy 参考链接: https://github.com/Leviathan1995/Pylsy
>+ bs4  安装方法: pip install bs4
>+ requests 安装方法: pip install requests

### 使用方法：

> 不保存结果的,结果仅打印屏幕:

> <code> python subdomain.py -d example.com</code>

> 同时保存结果:

> <code> python subdomain.py -d example.com -f result.txt </code>

### 例子

![image](https://github.com/latentgod/domainInfo/blob/master/example.png)

说明：(当给出分享到github时，http://whatweb.bugscaner.com/ 因为些原因关闭了，相信不久会开启的，感谢站长)

