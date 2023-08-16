import sys
from datetime import datetime, timezone, timedelta

import requests
from lxml import etree

from TargetConfig import TargetConfig
from RunTimeContext import RunTimeContext

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

    def __init__(self, targetConfig: TargetConfig, context: RunTimeContext):
        self._targetConfig = targetConfig
        self._context = context

    def webWatch(self, lastTime: datetime) -> list[WatchResult]:
        # print("脚本上次启动时间: " + lastTime.__str__())
        result = []
        html = self.get_html()

        # 判断是否接受公告的函数
        decide = None
        if self._targetConfig.isOnlyDate():  # 只比较日期, 需要记录本次发送的公告
            # 获取已发送的公告记录
            sent_msgs = self._context.get_sent_msgs(self._targetConfig.getTarget())
            # 清理今日之前记录的已发送公告
            if lastTime.date() < self._context.get_now_run_time().date():
                self._context.clear_sent_msgs(self._targetConfig.getTarget())

            decide = lambda t, c: t.date() >= lastTime.date() and c not in sent_msgs
        else:  # 比较时间, 无特殊处理
            decide = lambda t, c: t > lastTime

        for t, c in self.parse_html(html):
            if decide(t, c.getTitle()):
                result.append(c)
                # 记录已发送的公告
                self._context.record_sent_msg(self._targetConfig.getTarget(), c.getTitle())

        return result

    def get_html(self):
        """获取网页内容"""
        return requests.get(self._targetConfig.getUrl())\
            .content.decode('utf-8')  # 发送网络请求，获取网页内容并解码为utf-8格式

    def parse_html(self, html: str):
        """
        解析HTML文档并解析公告时间、标题、链接
        生成器函数，返回值为(时间: datetime, WatchResult)
        """
        targetConfig = self._targetConfig
        node = etree.HTML(html)  # 解析HTML文档
        for i in node.xpath(targetConfig.getPageXPath()):
            # 解析获取公告时间、标题、链接
            n_time = i.xpath(targetConfig.getTimeXPath())[0]
            n_title = i.xpath(targetConfig.getTitleXPath())[0]
            n_href: str = i.xpath(targetConfig.getHrefXPath())[0]

            # 拼接链接为可点击的完整链接
            n_href = self.href2url(n_href, targetConfig)
            # 解析时间
            the_time = self.parse_time(n_time, targetConfig)
            yield the_time, self.WatchResult(n_time, n_title, n_href)

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
    def parse_time(strtime: str, targetConfig: TargetConfig) -> datetime:
        t = datetime.strptime(strtime, targetConfig.getTimeFormat()).replace(tzinfo=targetConfig.getTimezone())
        return t

if __name__ == "__main__":
    sys.argv.append("config.yaml")
    sys.argv.append("test")
    targetConfig = TargetConfig.fromYaml("targetConfigs/scut.target.yaml")
    context = RunTimeContext("./config.yaml")
    watcher = WebWatcher(targetConfig, context)

    t = datetime.now() - timedelta(days=153)
    print(t)
    out = watcher.webWatch(t)
    for i in out:
        print(i)


    context.dump_last_record()



