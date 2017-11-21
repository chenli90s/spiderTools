import re
from urllib import request
from spiderf import MainSpider
from lxml import html

header = {
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding":"gzip, deflate, sdch, br",
    "Accept-Language":"zh-CN,zh;q=0.8",
    "Cache-Control":"max-age=0",
    "Connection":"keep-alive",
    "Cookie":"sessionuid=d58fe281-729a-4f34-8b9c-d0d245d658df; historybbsName4=c-2366%7CABT%2Cc-3170%7C%E5%A5%A5%E8%BF%AAA3%2Cc-266%7C%E9%98%BF%E6%96%AF%E9%A1%BF%26%23183%3B%E9%A9%AC%E4%B8%81%2Cc-2288%7C%E9%98%BF%E5%B0%94%E6%B3%95%E7%BD%97%E5%AF%86%E6%AC%A7; autoac=4A13E2A5455A6148527189D254B8CB69; papopclub=2702694DBA0337BB6FF640B626D39B06; pepopclub=574FA49DB712DFF2893DA1A4F2BEF969",
    "Host":"club.autohome.com.cn",
    "Referer":"http://safety.autohome.com.cn/userverify/index?locnum=656382&backurl=//club.autohome.com.cn/bbs/thread-c-2288-67125450-1.html",
    "Upgrade-Insecure-Requests":"1",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
}

class HackQiCar(object):

    def __init__(self, content=""):
        self.content = content
        # self.get_local_file()

    def init(self):
        res = re.findall(r"\(function\(\w*?\)\{(.*?)\}\)\(document\);", self.content)
        if res:
            self.content = res[0]

    def get_local_file(self):

        with open('test3.html', 'r') as f:
            for con in f.readlines():
                self.content += con

    def parse_main(self):
        self.init()
        res = re.findall(r"var \w+?= (\w+?)\('\w+?'\);", self.content)
        if res:
            res = re.findall(r"function "+res[0]+"\(\){(.*?)return ';';}", self.content, re.DOTALL)
            if res:
                return res[0]
        else:
            print(self.content)
            print("数据异常")

    def call_func(self, key):
        key = key.replace('(', '\(', 1)
        key = key.replace(')', '\)', 1)

        # "function vS_(){function _v(){return '%';};if(_v()=='%'){ return '%';}else{ return _v();}}"
        # "function "+key+"\{function \w+?\(\)\{return '(\w*?)';\};if\(\w+?\(\)=='(\w+?)'\)\{ return (.*?);\}else\{ return (.*?);\}\}"
        res = re.findall(r"function %s\{function \w+?\(\)\{return '(.*?)';\};if\(\w+?\(\)=='(.*?)'\)\{ return (.*?);\}else\{ return (.*?);\}\}"%key, self.content, re.DOTALL)
        if res:
            res = res[0]
            data = res[2]if res[0]==res[1] else res[3]
            if re.match(r"\w+?\(\)", data):
                data = res[0]
            # print(key, data, '__________')
            return data

        key = key.replace('\(', '', 1)
        key = key.replace('\)', '', 1)
        # var "+key+"=function\(\)\{ '\w*?'; return '\w*?';\}
        res = re.findall(r"var "+key+"=function\(\)\{.*?return '(.*?)';\}", self.content)
        if res:
            data = res[0]
            # print(key, data, "___________")
            return data

        # function\(\)\{ '\w*?'; return '\w*?';\}
        res = re.findall(r"function "+key+"\(\)\{'.*?';return '(.*?)';\}", self.content)
        if res:
            data = res[0]
            # print(key, data, "______________")
            return data
        print(key, "*************未匹配到的字符*****************")
        return ""

    def parse_core_func(self, key):
        if re.match(r'\w*\(\)', key):
            key = re.findall(r'(\w*\(\))', key)[0]
            data = self.call_func(key)
            return data
        elif re.match(r"'.*'", key):
            key = re.findall(r"('.*')", key)[0]
            return eval(key)
        elif re.match(r"\(function\(.*?\)\{.*?return (.*?)\}\)\((.*?)\)", key):
            res = re.findall(r"\(function\(.*?\)\{.*?;return (.*?)\}\)\((.*?)\)", key)[0]
            data = res[1]if res[1]else res[0]
            return data
        elif re.match(r"\w+?\('(.*?)'\)", key):
            res = re.findall(r"\w+?\('(.*?)'\)", key)[0]
            if res:
                return res
        elif re.match(r"(\w+)", key):
            # print(key)
            res = re.findall(r"(\w+)", key)[0]
            # print(res)
            res = re.findall(r"var %s.+?'(.*?)';"%res, self.content, re.DOTALL)
            if res:
                data = res[0]
                return data
        # elif re.match(r"\w+?\('(.*?)'\)\);.*?", key):
        #     print("hahah")
        #     res = re.findall(r"\w+?\('(.*?)'\)\);.*?", key)
        #     print(res, "------------------------------------------------")



    def parse_group_one(self):
        maindata = self.parse_main()
        # print(maindata)
        res = re.findall(r"=.*?\]\((.+?)=", maindata)
        if res:
            # print(res)
            # self.parse_one_info(res)
            result, index = self.parse_one(res)
            # print(result)
            result = request.unquote(result)
            data_index = self.parse_group_two(index)
            # print(result)
            return result, data_index

    def parse_group_two(self, index):
        field = index.split(';')[1]
        res = re.findall(r";%s=\w+?\(\((.*?),"%field, self.content)
        if res:
            # self.parse_one_info(res)
            result, index = self.parse_one(res)
            return result.split(";")


    def parse_one(self, res):
        res = res[0].split("+")
        result = ""
        for fun in res:
            if not fun == "''":
                # print("+++++", fun ,"++++++")
                data = self.parse_core_func(fun)
                if data:
                    if re.match(r"'.+?'", data):
                        data = eval(data)
                    # print(data)
                    result += data

        return result, res[-1]



    def parse_one_info(self, res):
        res = res[0].split("+")
        result = ""
        for fun in res:
            if not fun == "''":
                print("+++++", fun ,"++++++")
                data = self.parse_core_func(fun)
                if data:
                   print(data)

if __name__ == '__main__':
    ma = MainSpider()
    ma.headers = header
    text = ma.get_response("https://club.autohome.com.cn/bbs/thread-c-4171-68666819-1.html").text
    test = HackQiCar(text)
    # test.get_local_file()
    result, index = test.parse_group_one()
    print(result, index)

