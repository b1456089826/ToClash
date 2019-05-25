#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests
import base64


def getBasefile(url):  # 获取订阅链接加密文本
    try:
        html = requests.get(url)
        html.raise_for_status
        html.encoding = html.apparent_encoding
        return str(html.text)
    except:
        return "错误"


def getAllLinks(url):  # 从加密文本解析出所有ss链接
    links = getBasefile(url)
    result = decodeInfo(links)
    alllinks = result.split('\\n')
    if len(alllinks[-1]) < 10:
        alllinks.pop()
    return alllinks


def getAllNodes(url):  # 从ss链接汇总得到所有节点信息
    allnodes = []
    links = getAllLinks(url)
    for ss in links:
        link = ss.split('//')[1].split("'")[0]
        # node = getNode(link) if ss.split(':')[0] == "ss" else getNodeR(link)
        node = getNodeR(link)
        if node[0].find('过期时间')< 0 and node[0].find("剩余流量") < 0:
            allnodes.append(node)
    return allnodes


def getV2Nodes(url):  # 从ss链接汇总得到所有节点信息
    allnodes = []
    links = getAllLinks(url)
    for ss in links:
        link = ss.split('//')[1].split("'")[0]
        # node = getNode(link) if ss.split(':')[0] == "ss" else getNodeR(link)
        if ss.split(':')[0] == "vmess":
            node = getNodeV(link)
            allnodes.append(node)
    return allnodes


# def formatLink(link):
#     l1 = link.replace('-', '+')
#     l2 = l1.replace('_', '/')
#     return l2


def getNode(link):  # 从ss链接中得到节点信息
    info = decodeInfo(link)
    method = info.split(':')[0]
    pwd = info.split("@")[0].split(":")[1]
    server = info.split("@")[1].split(":")[0]
    port = info.split(':')[2]
    remark = server
    node = [remark, server, port, method, pwd]
    return node


def getNodeR(link):  # 从ssr链接中得到节点信息
    info = decodeInfo(link)
    pwd = decodeInfo(info.split('/')[0].split(':')[-1]).split("'")[1]
    server = info.split(':')[0].split("'")[1]
    port = info.split(':')[1]
    protocol = info.split(':')[2]
    method = info.split(':')[3]
    obfs = info.split(':')[4]
    #  print(info)
    # print(info.split('&')[2].split('=')[1])
    remark = getName(info.split('&')[2].split('=')[1])
    # print(server, port, method, pwd, protocol, obfs, remark)
    node = [remark, server, port, method, pwd, protocol, obfs]
    return node


def getNodeV(link):  # 从v2ray链接中得到节点信息
    info = decodeInfo(link)
    # print(info)
    s = str(link)
    s1 = base64.b64decode(s.encode('utf-8'))
    # print(str(s1, 'utf-8'))
    name = str(s1, 'utf-8').split(',')[4].split('"')[3]

    port = info.split(',')[6].split('"')[3]  # 端口

    server = info.split(',')[5].split('"')[3]  # 地址

    uuid = info.split(',')[7].split('"')[3]  # uuid

    alterId = info.split(',')[8].split('"')[3]  # alterid

    cipher = info.split(',')[10].split('"')[3]  # 加密

    node = [name, port, server, uuid, alterId, cipher]
    return node


def getName(info):  # 得到节点名称（有待合并）
    lens = len(info)
    # lenx = lens - (lens % 4 if lens % 4 else 4)
    if lens % 4 == 1:
        info = info + "==="
    elif lens % 4 == 2:
        info = info + "=="
    elif lens % 4 == 3:
        info = info + "="
    result = base64.urlsafe_b64decode(info).decode('utf-8', errors='ignore')
    return result


def checkNode(node):  # 检查节点是否是ss节点
    obfs = node[6]
    pro = node[5]
    return True


def checkObfs(str):  # 检查是否为ss混淆
    if str == "plain" or str.split('_')[-1] == "compatible":
        return True
    else:
        return False


def checkPro(str):  # 检查是否为ss协议
    if str == "origin" or str.split('_')[-1] == "compatible":
        return True
    else:
        return False


def decodeInfo(info):  # 解码加密内容
    lens = len(info)
    if lens % 4 == 1:
        info = info + "==="
    elif lens % 4 == 2:
        info = info + "=="
    elif lens % 4 == 3:
        info = info + "="
    result = str(base64.urlsafe_b64decode(info))
    return result


def setNodes(nodes, v2node):
    # 设置节点
    proxies = []
    for node in nodes:
        name = node[0]
        server = node[1]
        port = node[2]
        cipher = node[3]
        pwd = node[4]
        proxy = "- { name: " + str(
            name).strip() + ", type: ss, server: " + str(
            server) + ", port: " + str(port) + ", cipher: " + str(
            cipher) + ", password: " + str(pwd) + " }\n"
        proxies.append(proxy)
    for node in v2node:
        name = node[0]
        port = node[1]
        server = node[2]
        uuid = node[3]
        alterId = node[4]
        cipher = node[5]
        proxy = "- { name: " + str(
            name).strip() + ", type: vmess, server: " + str(
            server) + ", port: " + str(port) + ", uuid: " + str(uuid) + ", alterId: " + str(
            alterId) + ", cipher: " + str(cipher) + " }\n"
        proxies.append(proxy)
    proxies.insert(0, '\nProxy:\n')
    return proxies


def setPG(nodes, v2node):
    # 设置策略组 auto,Fallback-auto,Proxy
    proxy_names = []
    auto_names = []
    fallback_names = []
    proxy_names.append("auto")
    proxy_names.append("Fallback-auto")
    for node in nodes:
        if node[0].find("中转")< 0 or node[0].find('=>') >= 0:
            auto_names.append(node[0])
        strs = node[0].split(' ', 1)[0]
        if strs == "香港" or strs == "澳门" or strs == "台湾" or strs == "东京" or strs == "新加坡" or node[0].find('=>') >= 0:
            fallback_names.append(node[0])
        proxy_names.append(node[0])
    for node in v2node:
        strs = node[0].split(' ', 1)[0]
        if strs != "上海" and strs != "北京" and strs != "广州" and strs != "温州" and strs != "徐州" and strs != "深圳" or node[
            0].find('=>') >= 0:
            auto_names.append(node[0])
        if strs == "香港" or strs == "澳门" or strs == "台湾" or strs == "东京" or strs == "新加坡" or node[0].find('=>') >= 0:
            fallback_names.append(node[0])
        proxy_names.append(node[0])
    # print(str(proxy_names))
    auto = "- { name: 'auto', type: url-test, proxies: " + str(
        auto_names
    ) + ", url: 'http://www.gstatic.com/generate_204', interval: 300 }\n"
    Fallback = "- { name: 'Fallback-auto', type: fallback, proxies: " + str(
        fallback_names
    ) + ", url: 'http://www.gstatic.com/generate_204', interval: 300 }\n"
    Proxy = "- { name: 'Proxy', type: select, proxies: " + str(
        proxy_names) + " }\n"
    ProxyGroup = ['\nProxy Group:\n', auto, Fallback, Proxy]
    # ProxyGroup.insert(0, 'Proxy Group:\n')
    return ProxyGroup


def getClash(nodes, v2node):
    gener = getBasefile(
        'https://raw.githubusercontent.com/b1456089826/ToClash/master/General.yml')
    with open("./config.yml", "w", encoding="UTF-8") as f:
        f.writelines(gener)

    info = setNodes(nodes, v2node) + setPG(nodes, v2node)
    with open("./config.yml", "a", encoding="UTF-8") as f:
        f.writelines(info)

    rules = getBasefile(
        'https://raw.githubusercontent.com/lhie1/Rules/blob/master/Clash/Rule.yml')
    with open("./config.yml", "a", encoding="UTF-8") as f:
        f.writelines(rules)


if __name__ == "__main__":
    url = "https://www.tkcss.me/link/7fYJqhreMpjOHrGp?mu=0"
    nodes = getAllNodes(url)
    v2url = "https://www.tkcss.me/link/7fYJqhreMpjOHrGp?mu=2"
    v2node = getV2Nodes(v2url)
    getClash(nodes, v2node)
