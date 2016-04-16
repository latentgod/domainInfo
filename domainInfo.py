#!/usr/bin/python
#-*-coding: utf-8 -*-
# Author :si
import subprocess
import sys
import os
import socket
import requests
import multiprocessing
import time
import optparse
from bs4 import BeautifulSoup
from pylsy import pylsytable
from itertools import izip_longest, ifilter

class DomainInfo():

    def __init__(self):
        self.initParameter()
        self.ipThreads = 5
        self.cmsThreads = 5
        self.wafThreads = 5
        self.allDomain = []
        self.runDir = "./"

    def subDomain(self, domain):
        """
        获取 域名的子域名，爆破和公共DNS的正常子域名解释，使子域名更全
        """
        print "-----------" + domain +" -----------"
        print 'Bruting subDomain, wait a minute ...'
        if not os.path.exists(self.runDir +'tmp'):
            os.mkdir(self.runDir +'tmp')
        command = "perl "+ self.runDir +"dnsenum.pl "+ domain +" -w -d 5 --noreverse --threads 100 -f "+\
                self.runDir +"dns.txt --subfile "+ self.runDir +"tmp/"+ domain +".txt"
        child = subprocess.Popen(command,shell=True, stdout=subprocess.PIPE,stderr = subprocess.PIPE)
        printStr = str(child.stdout.read())
        self.getZoneTransfers(printStr)
        child.wait()

    def getOnlineSubdomian(self, website,allDomain):
        data = {'domain':website,'b2':1,'b3':1,'b4':1}
        postTarget = "http://i.links.cn/subdomain/"
        headers = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',\
                'User-Agent':' Mozilla/5.0 (WindowsNT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0',\
                'cookie':' linkhelper=sameipb3=1&sameipb4=1&sameipb2=1&bbaiduqz=&sameipbbaidu=&sameipbpr=;\
                CNZZDATA30012337=cnzz_eid%3D1618185584-1452593571-%26ntime%3D1456125061; AJSTAT_ok_times=2;\
                serverurl=; ASPSESSIONIDQARSSQCB=AHEEABOAGCNMCHIDPJJMPICA; umid=umid=24eed876dfc56c3747dffb\
                c612c0a527&querytime=2016%2D2%2D22+15%3A29%3A49; AJSTAT_ok_pages=1',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'
                }
        try:
            r = requests.post(postTarget, data=data, headers=headers,timeout = 30)
        except:
            return allDomain
        subdomainList = self.selectDomain(r.text)
        for i in subdomainList:
            allDomain.append(i.lstrip("http://").lstrip("https://"))
        return allDomain

    def selectDomain(self, html):
        soup = BeautifulSoup(html)
        subdomainList = []
        for i in xrange(len(soup.select('[class=domain]'))):
            subDomain = soup.select('[name=domain'+ str(i+1) +']')[0].attrs['value']
            subdomainList.append(subDomain)
        return subdomainList

    def getTargetUrlFile(self, filename,allDomain):
        f1 = open( self.runDir + "tmp/" + filename + '.txt',"r")
        # pre like ,mail,vpn
        for pre in f1.readlines(): 
            if pre in ["\n", None, ""]:
                continue
            subDomain = pre.strip("\n") + "." + filename
            allDomain.append(subDomain)
        return allDomain

    def getZoneTransfers(self, dnsenumStr):
        """
        处理 dnsenum 输出的数据，只显示域传送的输出
        """
        fileContent = dnsenumStr.split('\n')
        flag  = False
        a = []
        for eachLine in fileContent:
            if eachLine.find('Transfers') != -1:
                flag = True
            if flag == True:
                if eachLine.find('forcing') != -1:
                    flag = False
                    continue
                a.append(eachLine)
                if eachLine != r'\x1b[0m' and eachLine != '' and eachLine != r"\x1b[1;31m":
                    print eachLine

    def getIpFunc(self, targetList):
        """
        由域名获取ip，其中如果域名主机down的话，则获取不了
        """
        domainIpDict = {}
        for eachDomain in targetList: 
            if eachDomain in ["", None, "\n"]:
                continue
            eachDomain = eachDomain.strip("\n")
            myaddr = "error"
            try:
                myaddr = socket.getaddrinfo(eachDomain,'http')[0][4][0]
            except socket.gaierror:
                pass
            if myaddr == 'error':
                continue
            domainIpDict[eachDomain] = myaddr
            print eachDomain + " ----> " + myaddr
        return domainIpDict

    def getSubdomain(self):
        self.subDomain(self.options.domain)
        self.allDomain = self.getTargetUrlFile(self.options.domain,self.allDomain)
        self.allDomain = self.getOnlineSubdomian(self.options.domain,self.allDomain)
        self.allDomain = list(set(self.allDomain))

    def initParameter(self):
        parser = optparse.OptionParser()
        parser.add_option("-d", "--domain",
                          default = None,
                          help='''domain target,top domain  (e.g. "baidu.com , qq.com''')

        parser.add_option("-f", "--file",
                          default = None,
                          help="The file will be use to save result")

        (self.options, args) = parser.parse_args()
        if self.options.domain == None or self.options.domain == '':
            print parser.print_help()
            print "Please Completed  parameters, you can show -h to get help"
            sys.exit()
        if self.options.file != None:
            self.isFIle(self.options.file)

    def splitDict(self, bigDict, n):
        """
        这个函数，是个将大字典分成固定数量的小字典算法，使符合
        设定的线程数来进行多线程运行
        """
        if len(bigDict) < n:
            n = len(bigDict)
        # 是分成等块的一个列表的算法
        chunks = [bigDict.iteritems()]*(len(bigDict)/n)
        g = (dict(ifilter(None, v)) for v in izip_longest(*chunks))
        chunksList = list(g)
        # 这个遍历，是将分成等块后，将多余的拼接到前面去，使符合线程数
        for i in xrange(len(chunksList)-n):
            chunksList[i]=dict(chunksList[i],**chunksList.pop())
        return chunksList

    def startGetDomainInfo(self,domainIpDict):
        manager = multiprocessing.Manager()
        cmsQueue = manager.Queue()
        wafQueue = manager.Queue()
        processJobs = []
        for eachCmsDict in self.splitDict(domainIpDict, self.cmsThreads):
            p = multiprocessing.Process(target=self.cmsFunc, args=(cmsQueue, eachCmsDict))
            processJobs.append(p)
            p.start()
        for eachWafDict in self.splitDict(domainIpDict, self.wafThreads):
            p = multiprocessing.Process(target=self.wafFunc, args=(wafQueue, eachWafDict))
            processJobs.append(p)
            p.start()
        for eachProcess in processJobs:
            eachProcess.join()
        return [cmsQueue,wafQueue]

    def getCms(self,website):
        """
        从网上 whatweb 平台来获取cms，那个平台的cms指纹够全
        """
        print website + ", get cms ..."
        data = {'url':website}
        postTarget = "http://whatweb.bugscaner.com/what/"
        headers = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',\
                'User-Agent':' Mozilla/5.0 (WindowsNT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0',\
                'cookie':'saeut=CkMPGlbKeuabXlCdBK2qAg==; a8995_pages=1; a8995_times=1'}
        try:
            r = requests.post(postTarget, data=data, headers=headers)
        except:
            return "No"
        try:
            if eval(r.content)['cms'] != "":
                return eval(r.content)['cms']
        except SyntaxError:
            return "whatweb down"
        return "No"

    def cmsFunc(self,cmsQueue,targetDict):
        cmsDict = {}
        for domain in targetDict.keys():
            cmsDict[domain] = self.getCms(domain)
        cmsQueue.put(cmsDict)

    def getWaf(self,website):
        """
        识别目标是否有waf，再根据情况来做不同的渗透测试。用到wafw00f，这个工具对waf识别够全
        """
        print website + ", get waf ..."
        child = subprocess.Popen('wafw00f '+website, stdout=subprocess.PIPE,stderr = subprocess.PIPE,shell=True)
        child.wait()
        printStr = child.stdout.read()
        if printStr.find("is behind a") != -1:
            return "Yes"
        elif printStr.find("No WAF") != -1:
            return "No"
        elif printStr.find("seems to") != -1:
            return "May be"
        else:
            return "Http error"

    def wafFunc(self,wafQueue,targetDict):
        wafDict = {}
        for domain in targetDict.keys():
            wafDict[domain] = self.getWaf(domain)
        wafQueue.put(wafDict)

    def formatPrint(self,cmsQueue,domainIpDict,wafQueue):
        """
        格式化输出
        """
        attributes=["id","domain","cms","waf","ip"]
        table=pylsytable(attributes)
        domainList = domainIpDict.keys()
        cmsDict = self.queueToDict(cmsQueue)
        wafDict = self.queueToDict(wafQueue)
        for i in xrange(len(domainList)):
            table.append_data("id", i+1)
        for domain in domainList:
            table.append_data("cms", cmsDict[domain])
            table.append_data("domain", domain)
            table.append_data("waf", wafDict[domain])
            table.append_data("ip", domainIpDict[domain])
        if self.options.file != None:
            resultFile = open(self.options.file,'w')
            resultFile.write(str(table))
            time.sleep(0.1)
        print "----------- result -----------"
        print(table)

    def isFIle(self,filename):
        if not os.path.isfile(filename):
            return 
        print 'result file is exists, continue ?',
        choice = raw_input("(y/n): ")
        if choice.lower() == 'n':
            print 'Please rename filename, exit ...'
            sys.exit()
        if choice.lower() == 'y':
            return 
        else:
            return self.isFIle(filename)

    def queueToDict(self,queue):
        queueDict = {}
        while not queue.empty():
            queueDict =dict(queueDict,**queue.get())
        return queueDict

    def main(self):
        self.getSubdomain()
        domainIpDict = self.getIpFunc(self.allDomain)
        cmsAndWafQueueList = self.startGetDomainInfo(domainIpDict)
        self.formatPrint(cmsAndWafQueueList[0],domainIpDict,cmsAndWafQueueList[1])

if __name__ == '__main__':
    di = DomainInfo()
    di.main()
    __import__('shutil').rmtree(di.runDir + 'tmp')
