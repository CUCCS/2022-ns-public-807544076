# Chap 0x05
> author: 807544076

## 实验环境

宿主机：Windows 10
虚拟机：VirtualBox
* 被扫描主机：Gateway-debian
* 扫描者主机：Attack-kali

网络拓扑：

![](./img/network.png)

## 实验要求

* 禁止探测互联网上的 IP ，严格遵守网络安全相关法律法规

* 完成以下扫描技术的编程实现
    * TCP connect scan / TCP stealth scan
    * TCP Xmas scan / TCP fin scan / TCP null scan
    * UDP scan

* 上述每种扫描技术的实现测试均需要测试端口状态为：开放、关闭 和 过滤 状态时的程序执行结果

* 提供每一次扫描测试的抓包结果并分析与课本中的扫描方法原理是否相符？如果不同，试分析原因；

* 在实验报告中详细说明实验网络环境拓扑、被测试 IP 的端口状态是如何模拟的

* （可选）复刻 nmap 的上述扫描技术实现的命令行参数开关

## 实验过程
### 前置过程 （在上个实验已完成）
1. 安装 Python3
2. 安装 Scapy

### 正式实验
编写 `main.py`

用法：
```bash
Usage:  main.py <option> <ip> [port]
    options:
        -c  TCP connect scan
        -s  TCP stealth scan
        -x  TCP xmas scan
        -f  TCP fin scan
        -n  TCP null scan
        -u  UDP scan
    port:
        --port <port number> (Only accepted when single option)
```

#### TCP 实验
设置开启端口命令（open/closed）：
```bash
> python3 -m http.server
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

设置端口过滤（filtered）命令：
```
sudo iptables -A INPUT -p tcp --dport 8000 -j DROP
// 设置丢弃 8000 端口的 tcp 包
```

##### 当 8000 端口打开时：

![](./img/open.png)

测试：

tcp connect scan：

![](./img/c_o.png)

抓包结果：成功完成三次握手和四次挥手

![](./img/co.png)


tcp stealth scan：

![](./img/s_o.png)

抓包结果：成功实现

![](./img/so.png)

tcp xmas scan：

![](./img/x_o.png)

抓包结果：成功实现

![](./img/xo.png)

tcp fin scan：

![](./img/f_o.png)

抓包结果：成功实现

![](./img/fo.png)

tcp null scan：

![](./img/n_o.png)

抓包结果：成功实现

![](./img/no.png)

##### 当 8000 端口关闭时：

![](./img/close.png)

测试：

tcp connect scan：

![](./img/c_c.png)

抓包结果发现除了返回 `RST`，还返回了 `ACK`

![](./img/cc.png)

查询 google 得知其实真实过程是

>C --SYN-> S
>C <-ACK-- S
>C <-RST-- S

tcp stealth scan：

![](./img/s_c.png)

抓包结果同 connect scan

![](./img/ss.png)

tcp xmas scan：

![](./img/x_c.png)

抓包结果同 connect scan

![](./img/xc.png)

tcp fin scan：

![](./img/f_c.png)

抓包结果同 connect scan

![](./img/fc.png)

tcp null scan：

![](./img/n_c.png)

抓包结果同 connect scan

![](./img/nc.png)

##### 设置 8000 端口过滤器：

![](./img/set_filter.png)

测试：

tcp connect scan:

![](./img/c_f.png)

抓包结果：无响应重发三次后报错 timeout

![](./img/cf.png)

tcp stealth scan：

![](./img/s_f.png)

抓包结果

![](./img/sf.png)

tcp xmas scan：

![](./img/x_f.png)

抓包结果

![](./img/xf.png)

tcp fin scan：

![](./img/f_c.png)

抓包结果

![](./img/fc.png)

tcp null scan：

![](./img/n_f.png)

抓包结果

![](./img/nf.png)

#### UDP 实验

UDP 的判断逻辑较为复杂
一般而言，对于一个关闭的 UDP 端口，发送 UDP 包将会收到一个 ICMP 报错，参数为 **Type：3，Code：3**，即 **port unreachable** 端口不可达

对一个随机端口（关闭）发送 UDP 扫描，并用 tcpdump 抓包
```bash
sudo python main.py -u 172.16.111.1 --port 12345
```

![](./img/u_c.png)

可以抓到反馈的 ICMP

![](./img/icmp.png)

而对于一个开放的 UDP 端口，在应用程序未设定回应的情况下，**默认不发送任何回应**

开放 UDP 端口 9999
```bash
nc -u -l -p 9999
```

进行扫描，由于接收不到 answer，将会在 timeout 后反馈 `open/filtered`

![](./img/u_o.png)

可以在终端收到携带的数据，但是不会进行回应

![](./img/recv.png)

而对于过滤有几种情况

* 默认设定为 `DROP`

在这种情况下，UDP 扫描也不会收到任何回应，同样显示为 `open/filtered`

![](./img/drop.png)

* 设定为 `REJECT --reject-with port-unreachable`

```bash
sudo iptables -A INPUT -p udp --dport 9999 -j REJECT
```

这种情况会和关闭一样发送一个 ICMP（Code：3），显示也同样为 `closed` 状态，无法区分

![](./img/reject.png)

* 设定为 `port-unreachable` 以外的 reject 状态，此时发回的 ICMP 包会具有不同的 Code

例如将 reject 设定为 `icmp-net-prohibited`

```bash
sudo iptables -A INPUT -p udp --dport 9999 -j REJECT --reject-with icmp-net-prohibited
```

此时就可以明确该端口为 `filtered` 状态

![](./img/reject2.png)

![](./img/icmp_c.png)

## 遇到的问题及解决

问题：UDP 无开放端口
解决：google 发现用 nc 命令可以开放端口

问题：TCP 连接失败
解决：放弃 scapy 而采用 socket 的方式进行 TCP 连接

## 参考资料
[Linux 开放端口](https://juejin.cn/post/6934952605227417614)

[Python socket 编程](https://python.readthedocs.io/en/stable/howto/sockets.html)

[Python + Scapy 实现端口扫描](https://blog.csdn.net/hell_orld/article/details/109231819)

[nmap UDP scan](https://nmap.org/book/scan-methods-udp-scan.html)

[老师的课件](https://c4pr1c3.github.io/cuc-ns-ppt/chap0x05.md.v4.html#/%E4%B8%BB%E6%9C%BA%E7%8A%B6%E6%80%81%E8%AF%A6%E7%BB%86%E4%BF%A1%E6%81%AF%E6%8E%A2%E6%B5%8B%E6%8A%80%E6%9C%AF)