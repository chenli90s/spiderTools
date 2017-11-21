from spiderf import MainSpider
import time
import datetime
import re
import queue


class VideoSpider(object):
    s_time = '2017-11-13 19:39:56'
    start_url = 'http://www.letvlive.com/player/lovev.php?id=hunan&pindao=%E6%B9%96%E5%8D%97%E5%8D%AB%E8%A7%86'

    video_url = 'http://live.hcs.cmvideo.cn:8088/wd-hunanhd-600/'

    start_header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "Host": "www.letvlive.com",
        "Referer": "http://www.letvlive.com/tv2.php?id=hunan",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    }

    headers = {
        "Host": "live.hcs.cmvideo.cn:8088",
        "Connection": "keep - alive",
        "X-Requested-With": "ShockwaveFlash/22.0.0.192",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
        "Accept": "*/*",
        "Referer": "http://www.letvlive.com/player/lovev.php?id=hunan&pindao=%E6%B9%96%E5%8D%97%E5%8D%AB%E8%A7%86",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
    }

    def __init__(self, file_name="download_video", until_time=""):
        self.startTime = time.strptime(self.s_time, '%Y-%m-%d %H:%M:%S')
        self.startTime_stamp = str(int(time.mktime(self.startTime))) + "657"
        self.process_time = datetime.datetime.fromtimestamp(int(self.startTime_stamp) / 1000)
        self.next_time = self.process_time + datetime.timedelta(seconds=15 * 10)
        self.next_time_stamp = str(self.next_time.timestamp() * 1000)[:-2]
        self.core_spider = MainSpider()
        self.core_spider.headers = self.headers
        self.counter = 0
        self.start_m3u8 = ""
        self.file = file_name + ".mpeg"
        self.u_set = set()
        self.time_inter = 0
        self.process_queue = queue.Queue()
        self.cur_url = ""
        self.load_f = open(self.file, "wb")

    def start_request(self):
        self.core_spider.headers = self.start_header
        content = None
        try:
            content = self.core_spider.get_content(self.start_url)
        except:
            print("开始连接已断开，正在重新连接。。。")
        self.core_spider.headers = self.headers
        if content:
            content = content.decode()
            print("抓取视频内容中")
            res = re.findall(r'<video.*?src="(.*?)".*?>', content, re.DOTALL)
            if res:
                url = res[0]
                print('解析内容')
                mmt = self.core_spider.get_content(url)
                if mmt:
                    mm = mmt.decode()
                    ss = mm.split("\r\n")[2]
                    self.start_m3u8 = self.video_url + ss
                    print('成功提取， 准备下载.....')

    def cur_time(self):
        # next_time = self.process_time + datetime.timedelta(seconds=self.counter * 10)
        next_time = datetime.datetime.now()
        return str(next_time.timestamp() * 1000)[:-2]

    def parse_m3u8(self):
        url = self.start_m3u8 + "&time=" + self.cur_time()
        try:
            content = self.core_spider.get_content(url).decode()
            res = re.findall(r'#EXTINF:10,\r\n(.*?)\n', content)
            if not res:
                res = re.findall(r'#EXTINF:10,\r\n(.*?)\r\n', content)
        except:
            print("请求错误，重新连接")
        print(len(res), "个数据包")
        for rs in res:
            vide0_url = self.video_url + rs.strip()
            self.u_set
            if vide0_url not in self.u_set:
                self.u_set.add(vide0_url)
                self.process_queue.put(vide0_url)
                # print(vide0_url)
            else:
                print("抓取到重复地址", vide0_url)


    def load_content(self):
        self.time_inter = 0
        self.counter = 0
        while not self.process_queue.empty():
            start_time = datetime.datetime.now()
            url = self.process_queue.get_nowait()
            try:
                content = self.core_spider.get_content(url)
            except:
                # todo: 自定义队列，将未下载好的视频放入队头
                print('请求数据发生了一些错误, 若反复请求不到，请手动关闭 Ctrl+c ')
                self.process_queue
            # print(len(content), "个数据包")
            if content:
                self.load_f.write(content)
                self.counter += 1
                end_time = datetime.datetime.now()
                self.time_inter = self.time_inter + (end_time - start_time).seconds
                print(str(
                    '{:.2f}'.format(len(content) / 1000 / ((end_time - start_time).seconds + 1))),
                    "KB/S")

    def run(self):
        self.start_request()
        while True:
            if self.start_m3u8:
                self.parse_m3u8()
                self.load_content()
                sleep_time = 10 * self.counter - self.time_inter
                if sleep_time > 0:
                    print('将等待', str(10 * self.counter - self.time_inter), "秒")
                    time.sleep(sleep_time)
            else:
                self.start_request()


if __name__ == '__main__':
    videoSpider = VideoSpider()
    videoSpider.run()
