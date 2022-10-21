from scapy.all import *
import getopt
import sys
import re
import socket
import time
from scapy.layers.inet import TCP, IP, UDP, ICMP
from scapy.layers.l2 import ARP, Ether

tcp_port = [20, 21, 22, 23, 25, 53, 70, 79, 80, 88, 110, 113, 119, 139, 220, 443, 636, 1080, 8000, 8080, 8888]
udp_port = [53, 67, 68, 69, 137, 138, 161, 162]


def check_ip(ip):
    compile_ip = re.compile('^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
    if compile_ip.match(ip):
        return True
    else:
        return False


def is_host_up(ip):
    p = Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(pdst=ip)
    ans = srp(p, timeout=1, verbose=0)
    if ans is not None:
        print("\nhost is available\n")
        print("Start scanning\n")
        return True
    else:
        return False


def tcp_connect(ip, ports=tcp_port):
    for p in ports:
        print("Scanning port " + str(p))
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.settimeout(15)
        try:
            skt.connect((ip, int(p)))
        except Exception as ex:
            print(ex)
            print(ip, "port", str(p), "is closed/filtered.")
            continue
        skt.shutdown(socket.SHUT_RDWR)
        skt.close()
        print(ip, "port", str(p), "is open.")
        open_port.append(p)
        time.sleep(1)


def tcp_stealth(ip, ports=tcp_port):
    for p in ports:
        print("Scanning port " + str(p))
        pkt = IP(dst=ip) / TCP(dport=int(p), flags='S')
        ans = sr1(pkt, timeout=1, verbose=0)
        if ans is None:
            print(ip, "port", str(p), "is filtered.")
        else:
            if ans[TCP].flags == 'SA':
                print(ip, "port", str(p), "is open.")
                open_port.append(p)
            elif 'R' in ans[TCP].flags:
                print(ip, "port", str(p), "is closed.")
            else:
                print(ip, "port", str(p), "is filtered.")


def tcp_xmas(ip, ports=tcp_port):
    for p in ports:
        print("Scanning port " + str(p))
        pkt = IP(dst=ip) / TCP(dport=int(p), flags="FPU")
        ans = sr1(pkt, timeout=1, verbose=0)
        if ans is None:
            print(ip, "port", str(p), "may be open/filtered.")
            open_port.append(p)
        elif ans is not None and ans[TCP].flags == 'RA':
            print(ip, "port", str(p), "is closed.")
        else:
            print(ip, "port", str(p), "is filtered.")


def tcp_fin(ip, ports=tcp_port):
    for p in ports:
        print("Scanning port " + str(p))
        pkt = IP(dst=ip) / TCP(dport=int(p), flags="F")
        ans = sr1(pkt, timeout=1, verbose=0)
        if ans is None:
            print(ip, "port", str(p), "may be open/filtered.")
            open_port.append(p)
        elif ans is not None and ans[TCP].flags == 'RA':
            print(ip, "port", str(p), "is closed.")
        else:
            print(ip, "port", str(p), "is filtered.")


def tcp_null(ip, ports=tcp_port):
    for p in ports:
        print("Scanning port " + str(p))
        pkt = IP(dst=ip) / TCP(dport=int(p), flags='')
        ans = sr1(pkt, timeout=1, verbose=0)
        if ans is None:
            print(ip, "port", str(p), "is open/filtered.")
            open_port.append(p)
        elif ans is not None and ans[TCP].flags == 'RA':
            print(ip, "port", str(p), "is closed.")
        else:
            print(ip, "port", str(p), "is filtered.")


def udp(ip, ports=udp_port):
    for p in ports:
        pkt = IP(dst=ip) / UDP(dport=int(p)) / 'This is a test'
        ans = sr(pkt, timeout=3, verbose=0)
        if ans is not None:
            try:
                if ans[0][0][1][ICMP].code == 3:
                    print(ip, "port", str(p), "is closed")
                elif ans[0][0][1][ICMP].code in [1, 2, 9, 10, 13]:
                    print("port ", str(p), " may is filtered")
                else:
                    open_port.append(p)
                    print(ip, "port", str(p), "is open")
            except:
                print("port ", str(p), " may be open/filtered")
                open_port.append(p)
        else:
            print("port ", str(p), " may be open/filtered")
            open_port.append(p)


def show_help():
    print("""Usage:  main.py <option> <ip> [port]
    options:
        -c  TCP connect scan
        -s  TCP stealth scan
        -x  TCP xmas scan
        -f  TCP fin scan
        -n  TCP null scan
        -u  UDP scan
    port:
        --port <port number> (Only accepted when single option)""")


if __name__ == "__main__":
    command = []
    args = []
    hasPort = False
    port = []
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], 'c:s:x:f:n:u:', ['port='])
        for opt, arg in opts:
            # check ip
            if opt != "--port" and not check_ip(arg):
                print("ip of option " + opt + " has a format error")
                continue
            # get opt and arg
            if opt == '-h':
                show_help()
            if opt.replace('-', '') not in command:
                if opt == "--port":
                    hasPort = True  # 可选特定端口扫描（仅支持单命令）
                    port.append(arg)
                    continue
                command.append(opt.replace('-', ''))
                args.append(arg)
            else:
                continue
    except Exception as e:
        print(e)
        show_help()
        exit(1)

    if len(command) > 1 and hasPort:
        print("ERROR: Port can only be used when single option")
        show_help()
        exit(1)
    if len(command) < 1:
        show_help()

    if hasPort:
        for i in range(len(command)):
            open_port = []
            if not is_host_up(args[i]):
                print("Host is down")
                exit(0)
            if command[i] == 'c':
                tcp_connect(args[i], ports=port)
            elif command[i] == 's':
                tcp_stealth(args[i], ports=port)
            elif command[i] == 'x':
                tcp_xmas(args[i], ports=port)
            elif command[i] == 'f':
                tcp_fin(args[i], ports=port)
            elif command[i] == 'n':
                tcp_null(args[i], ports=port)
            elif command[i] == 'u':
                udp(args[i], ports=port)
    else:
        for i in range(len(command)):
            open_port = []
            if not is_host_up(args[i]):
                print("Host is down")
                exit(0)
            if command[i] == 'c':
                tcp_connect(args[i])
            elif command[i] == 's':
                tcp_stealth(args[i])
            elif command[i] == 'x':
                tcp_xmas(args[i])
            elif command[i] == 'f':
                tcp_fin(args[i])
            elif command[i] == 'n':
                tcp_null(args[i])
            elif command[i] == 'u':
                udp(args[i])

            pstr = ""
            if len(open_port) > 0:
                for j in open_port:
                    pstr += str(j)
                    pstr += ", "
                print("\n-----------------------------------------")
                print("Ip " + args[i] + " port " + pstr[:-2] + " is / may be open")
                print("\n-----------------------------------------")
            else:
                print("\n-----------------------------------------")
                print("Ip " + args[i] + " has no default port is open")
                print("\n-----------------------------------------")
