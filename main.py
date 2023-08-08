
"""
一个获取指定网站公告的脚本
设想通过系统定时任务启动, 获取自上次启动后的新公告
通过邮件发送通知
XPath解析网页
发送邮件
指定监视网站
指定通知接收者
考虑尝试观察者模式, 不同邮箱附加到某个网站观察者.
每个网站一个观察者
"""
import os
import sys

import requests  # 导入requests库，用于发送网络请求
from lxml import etree  # 导入lxml库的etree模块，用于解析HTML文档
import time  # 导入time库，用于处理时间相关操作
import numpy as np  # 导入numpy库，用于进行数值计算
import smtplib  # 导入smtplib库，用于发送邮件
from email.mime.text import MIMEText  # 导入email库的MIMEText类，用于创建邮件内容
from datetime import datetime, timedelta, timezone  # 时间处理
import yaml  # 配置文件处理

from Config import Config
from EmailSender import EmailSender, EmailConfig
from SecretConfig import SecretConfig
from TargetConfig import TargetConfig
from WebWatcher import WebWatcher


def recordThisRunTime():
    timeRecord = {
        "lastRunTime": thisRunTime.strftime(lastRunTimeFormat),
        "lastRunTimeFormat": lastRunTimeFormat
    }
    yaml.safe_dump(timeRecord, open(config.recordFilePath, "w", encoding="UTF8"))


if __name__ == "__main__":
    configFilePath = sys.argv[1]

    # # 读取配置文件

    # 获取普通配置
    config = Config.fromYaml(configFilePath)
    machineTimeZone = Config.TimeZoneHandler.get_timezone_or_default(config.timezone)
    # 记录本次运行时间
    thisRunTime: datetime = datetime.now(machineTimeZone)

    # 获取上次运行时间
    lastRunTimeLoad: str
    lastRunTime: datetime
    lastRunTimeFormat: str
    # 判断是否存在上次运行时间记录文件
    if not os.path.isfile(config.recordFilePath):
        # 不存在, 则创建
        lastRunTimeFormat = config.recordTimeFormat
        recordThisRunTime()
        # 退出
        exit(0)
    # 读取上次运行时间
    with open(config.recordFilePath, encoding="UTF8") as f:
        out: dict = yaml.safe_load(f)
        lastRunTimeLoad = out["lastRunTime"]
        lastRunTimeFormat = out["lastRunTimeFormat"]
    lastRunTime = datetime.strptime(lastRunTimeLoad, lastRunTimeFormat)

    # 获取敏感配置
    secretConfig = SecretConfig.fromYaml("secret.config.yaml")
    observers: dict[str, list[str]] = secretConfig.getObservers()
    emailConfig = EmailConfig(secretConfig.getEmail())

    # 构建目标配置文件名
    targets = list(observers.keys())
    targets = {x: x+".target.yaml" for x in targets}
    targets = {x: os.path.join(config.targetConfigPath, y) for x, y in targets.items()}

    # 获取目标配置文件读取配置
    targetConfigs: dict[str, TargetConfig] = {}
    for target, targetConfigFileName in targets.items():
        if not os.path.isfile(targetConfigFileName):
            raise FileNotFoundError(f"目标配置文件不存在: {targetConfigFileName}")
        targetConfig = TargetConfig.fromYaml(targetConfigFileName)
        targetConfigs[target] = targetConfig

    # 读取网页
    targetResults: dict[str, list[WebWatcher.WatchResult]] = {}
    for target, targetConfig in targetConfigs.items():
        watcher = WebWatcher(targetConfig)
        targetResults[target] = watcher.webWatch(lastRunTime)

    # TODO: 格式化发送内容
    targetMsgs: dict[str, MIMEText] = {}
    for target, results in targetResults.items():
        targetMsgs[target] = MIMEText("\n".join(map(lambda x: str(x), results)), "plain", "utf-8")

    # TODO: 发送邮件
    emailSender = EmailSender(emailConfig)
    for target, msg in targetMsgs.items():
        emailSender.sendEmail(msg, observers[target], Subject="新公告通知 "+targetConfigs[target].targetName)

    # 保存本次运行时间
    recordThisRunTime()






