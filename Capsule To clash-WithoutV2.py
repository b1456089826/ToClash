#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests
import base64
import re
import os
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




# def formatLink(link):
#     l1 = link.replace('-', '+')
#     l2 = l1.replace('_', '/')
#     return l2




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


def setNodes(nodes):
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
    proxies.insert(0, '\nProxy:\n')
    return proxies


def setPG(nodes):
    # 设置策略组 auto,Fallback-auto,Proxy
    proxy_names = []
    select_names=[]
    ad_names=[]
    auto_names = []
    fallback_names = []
    select_names.append("DIRECT")
    select_names.append("代理模式")
    ad_names.append("REJECT")
    ad_names.append("DIRECT")
    ad_names.append("代理模式")
    proxy_names.append("延迟最低")
    proxy_names.append("故障转移")
    for node in nodes:
        if node[0].find("中转")< 0 or node[0].find('=>') >= 0:
            auto_names.append(node[0])
        strs = node[0].split(' ', 1)[0]
        if strs == "香港" or strs == "澳门" or strs == "台湾" or strs == "东京" or strs == "新加坡" or node[0].find('=>') >= 0:
            fallback_names.append(node[0])
        proxy_names.append(node[0])
    # print(str(proxy_names))
    auto = "- { name: '延迟最低', type: url-test, proxies: " + str(
        auto_names
    ) + ", url: 'http://www.gstatic.com/generate_204', interval: 300 }\n"
    Fallback = "- { name: '故障转移', type: fallback, proxies: " + str(
        fallback_names
    ) + ", url: 'http://www.gstatic.com/generate_204', interval: 300 }\n"
    Proxy = "- { name: '代理模式', type: select, proxies: " + str(
        proxy_names) + " }\n"
    Domestic = "- { name: '国内地址', type: select, proxies: " + str(select_names) + " }\n"
    Others = "- { name: '其他', type: select, proxies: " + str(select_names) + " }\n"
    Apple = "- { name: 'Apple网站', type: select, proxies: " + str(select_names) + " }\n"
    GlobalTV = "- { name: '海外视频', type: select, proxies: " + str(select_names) + " }\n"
    AsianTV = "- { name: '国内视频', type: select, proxies: " + str(select_names) + " }\n"
    AdBlock = "- { name: '广告网站', type: select, proxies: " + str(ad_names) + " }\n"
    ProxyGroup = ['\nProxy Group:\n', auto, Fallback, Proxy,Domestic,Others,Apple,GlobalTV,AsianTV,AdBlock]
    # ProxyGroup.insert(0, 'Proxy Group:\n')
    return ProxyGroup



def getClash(nodes):
    gener = getBasefile(
        'https://raw.githubusercontent.com/b1456089826/ToClash/master/start.yml')
    info = setNodes(nodes) + setPG(nodes)
    with open("./configs.yml", "w", encoding="UTF-8") as f:
        f.writelines(gener)
        f.writelines(info)
    rules = getBasefile(
        'https://raw.githubusercontent.com/lhie1/Rules/master/Clash/Rule.yml')
    line_new = re.sub(r',Proxy', ',代理模式', re.sub(r',AsianTV', ',国内视频', re.sub(r',Apple', ',Apple网站',
                                                                              re.sub(r',GlobalTV', ',海外视频',
                                                                                     re.sub(r',AdBlock', ',广告网站',
                                                                                            re.sub(r',Domestic',
                                                                                                   ',国内地址',
                                                                                                   re.sub(r',Others',
                                                                                                          ',其他', re.sub(
                                                                                                           r',DIRECT',
                                                                                                           ',国内地址',
                                                                                                           re.sub(
                                                                                                               r'- MATCH,Others',
                                                                                                               ' ',
                                                                                                               rules)))))))))
    rules2 = getBasefile(
        'https://raw.githubusercontent.com/b1456089826/ToClash/master/rule.txt')
    line_new2 = re.sub(r',选择模式', ',代理模式', re.sub(r',国内媒体', ',国内视频', re.sub(r',Apple服务', ',Apple网站',
                                                                           re.sub(r',国际媒体', ',海外视频',
                                                                                  re.sub(r',屏蔽网站', ',广告网站',
                                                                                         re.sub(r',Proxy', ',代理模式',
                                                                                                re.sub(r',Others',
                                                                                                       ',其他', re.sub(
                                                                                                        r',DIRECT',
                                                                                                        ',国内地址',
                                                                                                        rules2))))))))
    fr = getBasefile('https://raw.githubusercontent.com/Hackl0us/SS-Rule-Snippet/master/LAZY_RULES/clash.yaml')
    line_new3 = re.sub(r',Proxy', ',代理模式',
                       re.sub(r',DIRECT', ',国内地址', re.sub(r',REJECT', ',广告网站', fr.split('Rule:')[1])))
    frs = getBasefile('https://raw.githubusercontent.com/ConnersHua/Profiles/master/Clash/Pro.yaml')
    line_new4 = re.sub(r',PROXY', ',代理模式', re.sub(r',REJECT', ',广告网站', re.sub(r',Apple', ',Apple网站',
                                                                              re.sub(r',ForeignMedia', ',海外视频',
                                                                                     re.sub(r',Hijacking', ',广告网站',
                                                                                            re.sub(r',Final', ',代理模式',
                                                                                                   re.sub(r',DomesticMedia',
                                                                                                          ',国内视频', re.sub(
                                                                                                           r',DIRECT',
                                                                                                           ',国内地址',
                                                                                                           frs.split(
                                                                                                               'Rule:')[
                                                                                                               1]))))))))
    lists=[]
    with open("./configs.yml", "a", encoding="UTF-8") as f:
        f.writelines(str(line_new))
        f.writelines("\n")
        f.writelines(str(line_new2))
        f.writelines(str(line_new3))
        f.writelines(str(line_new4))
        f.close()





def clean(infile, outfile):
    infopen = open(infile, 'r', encoding='utf-8')
    outstring = ''
    lines = infopen.readlines()
    list_1 = []
    for line in lines:
        if line not in list_1:
            list_1.append(line)
            outstring += line
    infopen.close()
    m = re.compile(r'#.*')
    outtmp = re.sub(m, '', outstring)
    outstring = outtmp

    outtmp = re.sub(r'^\n|\n+(?=\n)|\n$', '', outstring)
    outstring = outtmp
    f = open(outfile, 'w', encoding='UTF-8')
    f.write(outstring)
    f.close()



if __name__ == "__main__":
    print("ssstart")
    url = ""
    nodes = getAllNodes(url)
    print("ssok")
    judge = 0
    error = 1
    while judge >= 0:
        if error == 1:
            nodes = getAllNodes(url)
            getClash(nodes)
            with open("./configs.yml", encoding="UTF-8") as f:
                if f.read().find('错误') < 0:
                    with open("./configs.yml", "r+", encoding="UTF-8") as f1:
                        infos = f1.read()
                        line_new = re.sub(r'\\t', '', infos)
                        f1.seek(0)  # 将指针位置指到文件开头（注意：一定要有这步操作，不然无法清空文件）
                        f1.truncate()  # 清空文件内容（仅当以 "r+"   "rb+"    "w"   "wb" "wb+"等以可写模式打开的文件才可以执行该功能）
                        f1.write(line_new)
                        f1.close()
                    clean('./configs.yml', './config.yml')
                    print("转换成功，文件名称为config.yml，程序退出")
                    f.close()
                os.remove("./configs.yml")
                error = 0
            if error == 0:
                break
            else:
                if judge >= 5:
                    print("第5次失败，退出程序")
                    break
                else:
                    judge = judge + 1
                    print("第" + str(judge) + "次失败")
