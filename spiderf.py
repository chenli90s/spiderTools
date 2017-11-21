import requests
import re
import os
import queue


class MainSpider(object):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'}

    def __init__(self, path="ptml"):
        self.path = path
        self.css_path = path + "/css/"
        self.js_path = path + "/js/"
        self.img_path = path + "/img/"
        self.u_set = set()

    def main(self, url, path="ptml"):
        response = self.get_response(url)
        init_page = response.content
        # self.f_loader(init_page, path + "/index.html")
        domains = re.findall(r"http://[\w\.]*", url)
        if not domains:
            domains = re.findall(r"https://[\w\.]*", url)
        domain = domains[0]
        self.process(response, domain)

    def process(self, response, domain):
        self.parse_content(response, domain)
        # try:
        #     self.parse_content(response, domain)
        # except Exception as e:
        #     print(e)

    def get_response(self, url):
        # print(url)
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response
        else:
            print(response.url, response.status_code)
            raise response.status_code

    def get_content(self, url):
        return self.get_response(url).content

    def get_content_perfix(self, url, domain):
        res = url.split(":")
        if len(res) == 1:
            rss = re.match(r"^//", url)
            if rss:
                if domain:
                    hs = domain.split(':')[0]
                    url = hs + ":" + url
                else:
                    raise 'Domain is None'
            else:
                url = domain + url
        return url

    def parse_content(self, response, domain=None):
        content = response.content.decode(response.encoding)
        content = self.parse_css(content, domain)
        content = self.parse_script(content, domain)
        content = self.parse_img(content, domain)
        self.f_loader(content.encode(), self.path+"/index.html")

    def parse_core(self, content, r, type, domain, file_path=""):
        # res = re.findall(r'<link.*?href="(.*?)".*?/>', content, re.DOTALL)
        res = r
        for ress in res:
            # print(ress)
            rss = ress.split('?')[0]
            # if rss.endswith("css"):
            if type == "":
                name = rss.split('/')[-1]
            elif rss.endswith(type):
                name = rss.split('/')[-1]
            else:
                return content
            name = rss.split('/')[-1]
            url = self.get_content_perfix(ress, domain)
            if url not in self.u_set:
                self.u_set.add(url)
                bytet = self.get_content(url)
                self.f_loader(bytet, file_path + name)
            print(ress)
            content = re.sub(ress, file_path + name, content)
        return content

    def parse_a(self, content, domain):
        res = re.findall('<a.*?href="(.*?)".*?>', content, re.DOTALL)
        return self.parse_core(content, res, "", domain, "html")

    def parse_css(self, content, domain):
        res = re.findall('<link.*?href="(.*?)".*?/>', content, re.DOTALL)
        return self.parse_core(content, res, "css", domain, self.css_path)

    def parse_script(self, content, domain):
        res = re.findall('<script.*?src="(.*?)".*?>', content, re.DOTALL)
        return self.parse_core(content, res, "js", domain, self.js_path)

    def parse_img(self, content, domain):
        res = re.findall(r'<img.*?src="(.*?)".*?>', content, re.DOTALL)
        return self.parse_core(content, res, "", domain, self.img_path)

    def f_loader(self, content, path):
        paths = path.split("/")
        # print(paths)
        path = os.getcwd() + os.sep + os.sep.join(paths[:-1])
        if not os.path.exists(path):
            os.makedirs(path)
        path += os.sep+paths[-1]
        with open(path, "wb") as f:
            f.write(content)


if __name__ == '__main__':
    spider = MainSpider()
    content = spider.main(
        'http://www.cnblogs.com/zhangzhen894095789/p/6475033.html')
