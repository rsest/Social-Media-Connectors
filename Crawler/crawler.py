import json
import os
import re
import ssl
import time
from datetime import timedelta
from urllib.parse import quote, urlencode

import requests
from lxml import etree
from tornado import httpclient, gen, ioloop, queues, httputil


class ProducerConsumer(object):

    def __init__(self, concurrency=500):
        super(ProducerConsumer, self).__init__()
        self.concurrency = concurrency

    def producer(self):
        raise

    def consumer(self):
        raise

    @gen.coroutine
    def __procon(self):
        """
                producer
                consumer
                concurrency（parallelism）
        """
        start = time.time()

        q = queues.Queue(maxsize=self.concurrency)

        @gen.coroutine
        def worker():
            while True:
                d = yield q.get()
                try:
                    yield self.consumer(d)
                except Exception as e:
                    print("PRO_CON:" + str(e), d)
                q.task_done()

        # consumer worker
        for i in range(self.concurrency):
            worker()

        # producer
        for d in self.producer():
            yield q.put(d)

        yield q.join(timeout=timedelta(seconds=300))
        print("concurrency task done in %d seconds" % (time.time() - start))

    def run(self):
        io_loop = ioloop.IOLoop.current()
        io_loop.run_sync(self.__procon)


class BaseCrawler(ProducerConsumer):
    """docstring for BaseCrawler"""

    def __init__(self, concurrency=500):
        super(BaseCrawler, self).__init__(concurrency)

        dstdirs = [
            "/data/",
            "/database/",
        ]
        dstnames = []
        for dstdir in dstdirs:
            for root, subdir, files in os.walk(dstdir):
                dstnames.extend(files)
        self.e_names = set(dstnames)
        print("Name", len(self.e_names), " ")
        self.basic_path = "/data/"
        self.max_page = 50

    def search_many_keywords(self, keywords_list):
        for keywords in keywords_list:
            try:
                print("searching %s" % keywords)
                path = "." + self.basic_path + keywords.replace(" ", "_") + "/"
                if not os.path.exists(path):
                    os.makedirs(path)
                self.path = path
                self.keywords = keywords
                self.run()
            except Exception as e:
                print(e)
            else:
                print("searching done %s" % self.keywords)
            if os.listdir(path) == []: os.remove(path)

    @gen.coroutine
    def consumer(self, data):
        src, filename = data

        if filename not in self.e_names:
            request = httpclient.HTTPRequest(src, connect_timeout=60, request_timeout=10 * 60)
            response = yield httpclient.AsyncHTTPClient().fetch(request)
            with open(self.path + filename, "wb") as file:
                file.write(response.body)
                file.flush()
                self.e_names.add(filename)


class BaiduImgsCrawler(BaseCrawler):
    """docstring for BaiduImgsCrawler"""

    lang = "zh"

    def __init__(self, concurrency=1):
        super(BaiduImgsCrawler, self).__init__(concurrency)
        self.basic_path += "imgs/baidu/"

    def producer(self):
        keywords = self.keywords
        imgre = re.compile('"thumbURL":"(.*?)",')
        gsmre = re.compile('"gsm":"(.*?)",')
        gsm = "5a"
        for i in range(1, self.max_page):
            url = "https://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&is=&fp=result&queryWord=" + quote(
                keywords) + "&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=-1&z=&ic=0&word=" + quote(
                keywords) + "&s=&se=&tab=&width=&height=&face=0&istype=2&qc=&nc=1&fr=&pn=" + str(
                60 * i) + "&rn=60&gsm=" + gsm + "&1533019896783="
            html = requests.get(url)
            imglist = imgre.findall(html.text)
            gsm = gsmre.findall(html.text)[0]
            if len(imglist) == 0: break
            print("page: %05d, #pics: %d" % (i, len(imglist)))
            for src in imglist:
                filename = src.split("/")[-1]
                yield (src, filename)


class QuanjingImgsCrawler(BaseCrawler):
    """docstring for QuanjingImgsCrawler"""

    lang = "zh"

    def __init__(self, concurrency=1):
        super(QuanjingImgsCrawler, self).__init__(concurrency)
        self.basic_path += "imgs/quanjing/"

    def producer(self):
        keywords = self.keywords
        for i in range(1, self.max_page):
            url = "http://search.quanjing.com/search?key=" + quote(keywords) + "&pageSize=100&pageNum=" + str(
                i) + "&imageType=2&sortType=1&imageUType=p&callback=searchresult&_=1532325422612"
            html = requests.get(url)
            result = json.loads(html.text[13:-1])
            imglist = result["imglist"]
            print("page: %05d/%05d, #pics: %d" %
                  (result["pageindex"], result["pagecount"], len(imglist)))
            for img in imglist:
                src = img["imgurl"]
                filename = src.split("/")[-2] + ".jpg"
                yield (src, filename)
            if result["pageindex"] == result["pagecount"]: break


class QuanjingVideosCrawler(BaseCrawler):
    """docstring for QuanjingVideosCrawler"""

    lang = "zh"

    def __init__(self, concurrency=1):
        super(QuanjingVideosCrawler, self).__init__(concurrency)
        self.basic_path += "videos/quanjing/"

    def producer(self):
        keywords = self.keywords
        for i in range(1, self.max_page):
            url = "http://v.quanjing.com/Handler/SearchBindHandler.ashx?key=" + \
                  quote(keywords) + "&pagesize=100&pageNum=" + str(i) + \
                  "&Fr=1&sortFlag=1&resolution=2&FPS=0&minlength=0&maxlength=120000"
            html = requests.get(url)
            try:
                result = json.loads(html.text)
            except:
                print(html.text)
                print("PARSE JSON ERROR, Next page!")
            videolist = result["videolist"]
            print("page: %05d/%05d, #videos: %d" %
                  (i, result["pagecount"], len(videolist)))
            for video in videolist:
                src = video["videosUrl"]
                filename = src.split("?")[0].split("/")[-1]
                yield (src, filename)
            if i == result["pagecount"]: break


class VeerImgsCrawler(BaseCrawler):
    """docstring for VeerImgsCrawler"""

    lang = "zh"

    def __init__(self, concurrency=1):
        super(VeerImgsCrawler, self).__init__(concurrency)
        self.basic_path += "imgs/veer/"

    def producer(self):
        keywords = self.keywords
        for i in range(1, self.max_page):
            url = "https://www.veer.com/ajax/search"

            data = {"graphicalStyle": "1", "phrase": keywords, "page": i, "perpage": 100,
                    "key": "3JNAAH", "page_type": 6}

            html = requests.post(url, data)
            result = json.loads(html.text)
            imglist = result["data"]["list"]
            if len(imglist) == 0: break
            print("page: %05d,totalCount: %d, #pics: %d" %
                  (i, result["data"]["totalCount"], len(imglist)))
            for img in imglist:
                src = img["oss400"]
                filename = src.split("/")[-1]
                yield (src, filename)
            if i * 100 >= result["data"]["totalCount"]:
                break


class TuchongImgsCrawler(BaseCrawler):
    """docstring for TuchongImgsCrawler"""

    lang = "zh"

    def __init__(self, concurrency=1):
        super(TuchongImgsCrawler, self).__init__(concurrency)
        self.basic_path += "imgs/tuchong/"

    def producer(self):
        keywords = self.keywords
        imgid = re.compile(r'"imageId":"(\d+)"')
        serverlist = [
            '//p1.pstatp.com/',
            '//p3.pstatp.com/',
            '//p9.pstatp.com/',
            '//p3a.pstatp.com/'
        ]
        for i in range(1, self.max_page):

            url = "https://stock.tuchong.com/search?term=" + quote(
                keywords) + "&use=2&type=&layout=&sort=0&category=0&page=" + str(
                i) + "&size=100&search_from=head&exact=0&platform=weili&tp=&abtest=&royalty_free=0&option=&has_person=0&face_num=&gender=0&age=&racial="

            html = requests.get(url)
            sr = imgid.findall(html.text)
            print("page: %05d, #pics: %d" % (i, len(sr)))
            if len(sr) == 0: break
            for x in sr:

                for server in serverlist:
                    src = "https:%sweili/sm/" % server + x + ".jpg"
                    filename = src.split("/")[-1]
                    yield (src, filename)


class Pond5VideosCrawler(BaseCrawler):
    """docstring for Pond5VideosCrawler"""

    lang = "en"

    def __init__(self, concurrency=1):
        super(Pond5VideosCrawler, self).__init__(concurrency)
        self.basic_path += "videos/pond5/"

    def producer(self):
        keywords = self.keywords
        for i in range(1, self.max_page):
            url = "https://www.pond5.com/stock-video-footage/" + \
                  str(i) + "/" + quote(keywords) + ".html"
            html = requests.get(url)
            selector = etree.HTML(html.text)
            srcs = selector.xpath(
                "//img[contains(@class, 'SearchResultV3-thumbImg')]/@src")  # 返回为一列表
            if len(srcs) == 0: break
            print("page: %03d, #pics: %d" % (i, len(srcs)))
            for src in srcs:
                src = src.replace("images", "videos")
                src = src.replace("iconm.jpeg", "main_xl.mp4")
                filename = src.split("/")[-1]
                yield (src, filename)


class StoryblocksVideosCrawler(BaseCrawler):
    """docstring for StoryblocksVideosCrawler"""

    lang = "en"

    def __init__(self, concurrency=1):
        super(StoryblocksVideosCrawler, self).__init__(concurrency)
        self.basic_path += "videos/storyblocks/"

    def producer(self):
        keywords = self.keywords
        detailsUrl = re.compile('"thumbnailUrl":"(.*?)",')
        previewUrl = re.compile('"previewUrl":"(.*?)",')

        for i in range(1, self.max_page):
            url = "https://www.videoblocks.com/videos/%s" % "+".join(
                keywords.split()) + "?combined_page=" + str(i)
            html = requests.get(url)
            # imgs = detailsUrl.findall(html.text)
            vids = previewUrl.findall(html.text)
            if len(vids) == 0: break
            print("page: %03d, #pics: %d" % (i, len(vids)))
            for src in vids:
                src = src.replace("\\/", "/")
                filename = src.split("/")[-1]
                if len(filename) > 128:
                    filename = filename.split(".")[0][0:120] + ".mp4"
                yield (src, filename)


class ShutterstockVideosCrawler(BaseCrawler):
    """docstring for ShutterstockVideosCrawler"""

    lang = "en"

    def __init__(self, concurrency=1):
        super(ShutterstockVideosCrawler, self).__init__(concurrency)
        self.basic_path += "videos/shutterstock/"

    def producer(self):
        keywords = self.keywords
        for i in range(1, self.max_page):
            url = "https://www.shutterstock.com/zh/video/search/%s" % "-".join(
                keywords.split()) + "?page=" + str(i)
            html = requests.get(url)

            selector = etree.HTML(html.text)

            vid_srcs = selector.xpath("//source[@type='video/mp4']/@src")
            if len(vid_srcs) == 0: break
            print("page: %03d, #vids: %d" % (i, len(vid_srcs)))
            for src in vid_srcs:
                yield src, src.split("/")[-1]


class VideezyVideosCrawler(BaseCrawler):
    lang = "en"

    def __init__(self, concurrency=1):
        super(VideezyVideosCrawler, self).__init__(concurrency)
        self.basic_path += "videos/videezy/"

    def producer(self):
        keywords = self.keywords
        for i in range(1, self.max_page):
            url = "https://www.videezy.com/free-video/" + keywords + "?in_se=true&page=" + str(i)
            html = requests.get(url)
            selector = etree.HTML(html.text)
            vid_srcs = selector.xpath(
                "//ul[contains(@class, 'videezy-grid')]//a/@href")
            if len(vid_srcs) == 0: break
            print("page: %03d, #vids: %d" % (i, len(vid_srcs)))
            for src in vid_srcs:
                yield "https://www.videezy.com" + src, src.split("/")[-1] + ".mp4"

    re_download = re.compile('var download_file_url = "(.*?)";')

    @gen.coroutine
    def consumer(self, data):
        page_url, filename = data
        if filename not in self.e_names:
            response = yield httpclient.AsyncHTTPClient().fetch(page_url)
            download_url = "https://www.videezy.com" + VideezyVideosCrawler.re_download.findall(response.body.decode())[
                0]
            request_header = httputil.HTTPHeaders()
            request_header.add("cookie", response.headers.get("set-cookie"))
            request = httpclient.HTTPRequest(download_url, method='GET', headers=request_header, connect_timeout=10,
                                             request_timeout=10 * 60)
            response = yield httpclient.AsyncHTTPClient().fetch(request)
            with open(self.path + filename, "wb") as file:
                file.write(response.body)
                file.flush()
                self.e_names.add(filename)


class VidevoVideosCrawler(BaseCrawler):
    lang = "en"

    def __init__(self, concurrency=1):
        super(VidevoVideosCrawler, self).__init__(concurrency)
        self.basic_path += "videos/videvo/"

    def producer(self):
        keywords = self.keywords
        for i in range(1, self.max_page):
            url = "https://www.videvo.net/search/" + quote(
                keywords) + "/clip_type/free-stock-footage/freeclips/yes/" + ("?page=%d" % (i - 1) if i > 1 else "")
            html = requests.get(url)
            selector = etree.HTML(html.text)
            vid_srcs = selector.xpath("//div[contains(@class,'video-responsive')]/div[3]/div[1]/a/@href")
            vid_srcs = [src[:-1] for src in vid_srcs]
            if len(vid_srcs) == 0: break
            print("page: %03d, #vids: %d" % (i, len(vid_srcs)))
            for src in vid_srcs:
                yield "https://www.videvo.net" + src, src.split("/")[-2] + ".mp4"

    re_hash = re.compile('name="hash" value="(.*?)"')

    @gen.coroutine
    def consumer(self, data):
        page_url, filename = data
        vc_id = page_url.split("/")[-1]
        if filename not in self.e_names:
            response = yield httpclient.AsyncHTTPClient().fetch(page_url)
            data = dict(hash=VidevoVideosCrawler.re_hash.findall(response.body.decode())[0], vc_id=vc_id)
            data = urlencode(data)
            download_url = "https://www.videvo.net/api/?path=download/download"
            request_header = httputil.HTTPHeaders()
            request_header.add("cookie", response.headers.get("set-cookie"))
            request = httpclient.HTTPRequest(download_url, method='POST', headers=request_header, body=data,
                                             connect_timeout=10, request_timeout=10 * 60)
            response = yield httpclient.AsyncHTTPClient().fetch(request)
            with open(self.path + filename, "wb") as file:
                file.write(response.body)
                file.flush()
                self.e_names.add(filename)


class ClipcanvasVideosCrawler(BaseCrawler):
    lang = "en"

    def __init__(self, concurrency=1):
        super(ClipcanvasVideosCrawler, self).__init__(concurrency)
        self.basic_path += "videos/clipcanvas/"

    re_preview = re.compile(r'data-preview-url="https://d19n3nonuhb7ef\.cloudfront\.net/clips/medium/(\d+)\.mp4"')

    def producer(self):
        keywords = self.keywords
        for i in range(1, self.max_page):
            url = "https://www.clipcanvas.com/stock-footage/" + str(i) + "/" + "-".join(keywords.split()) + ".html"
            http = requests.get(url)
            srcs = ClipcanvasVideosCrawler.re_preview.findall(http.text)
            if len(srcs) == 0: break
            print("page: %03d, #vids: %d" % (i, len(srcs)))
            for src in srcs:
                yield "http://dtgy1q9vuxi5a.cloudfront.net/%s.mp4" % src, "%s.mp4" % src


def main():
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    debug = True
    keywords_list_en = open("keywords_list_en.txt", 'r',
                            encoding='utf-8').read().strip().split("\n")

    crawlers_list = BaseCrawler.__subclasses__()
    print(crawlers_list)
    if debug:
        cls = Pond5VideosCrawler
        print(cls)
        cls(concurrency=10).search_many_keywords(keywords_list_en)

    else:
        for cls in crawlers_list:
            cls(concurrency=30).search_many_keywords(keywords_list_en)


if __name__ == '__main__':
    main()
