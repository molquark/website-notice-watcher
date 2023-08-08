from datetime import datetime, timezone, timedelta

import requests
from lxml import etree

from TargetConfig import TargetConfig





class WebWatcher:
    class WatchResult:

        def __init__(self, time: str, title: str, href: str):
            self._time = time
            self._title = title
            self._href = href

        def getTime(self):
            return self._time

        def getTitle(self):
            return self._title

        def getHref(self):
            return self._href

        def __str__(self):
            return f"{self._time}: {self._title} ({self._href})"



    def __init__(self, targetConfig: TargetConfig):
        self._targetConfig = targetConfig

    def webWatch(self, lastTime: datetime) -> list[WatchResult]:
        # print("脚本上次启动时间: " + lastTime.__str__())
        result = []
        targetConfig = self._targetConfig
        html = requests.get(targetConfig.getUrl())\
            .content.decode('utf-8')  # 发送网络请求，获取网页内容并解码为utf-8格式

        node = etree.HTML(html)  # 解析HTML文档
        for i in node.xpath(targetConfig.getPageXPath()):
            # 解析获取公告时间、标题、链接
            n_time = i.xpath(targetConfig.getTimeXPath())[0]
            n_title = i.xpath(targetConfig.getTitleXPath())[0]
            n_href: str = i.xpath(targetConfig.getHrefXPath())[0]

            # 拼接链接为可点击的完整链接
            n_href = self.href2url(n_href, targetConfig)
            # 解析时间
            the_time = self.parsetime(n_time, targetConfig)
            if the_time > lastTime:
                result.append(self.WatchResult(n_time, n_title, n_href))

        return result

    @staticmethod
    def href2url(href: str, targetConfig: TargetConfig) -> str:
        # 拼接链接, 有https://xxx.edu.cn/2022/xxx, /2022/xxx, 2022/xxx 三种形式?
        if not href.startswith("http"):
            if href.startswith("/"):
                baseUrl = targetConfig.getBaseUrl()
                baseUrl = baseUrl[:-1] if baseUrl.endswith("/") else baseUrl
                href = targetConfig.getBaseUrl() + href
            else:  # n_href = 2022/xxx.htm
                url = targetConfig.getUrl()
                url = url if url.endswith("/") else url + "/"
                href = url + href
        return href

    @staticmethod
    def parsetime(strtime: str, targetConfig: TargetConfig) -> datetime:
        t = datetime.strptime(strtime, targetConfig.getTimeFormat()).replace(tzinfo=targetConfig.getTimezone())
        return t

if __name__ == "__main__":
    watcher = WebWatcher(TargetConfig.fromYaml("targetConfigs/scut.target.yaml"))
    res = watcher.webWatch(datetime.now().replace(month=6, tzinfo=timezone(timedelta(hours=8))))

    for i in res:
        print(i)
