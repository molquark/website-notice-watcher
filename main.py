
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

import sys
from email.mime.text import MIMEText  # 导入email库的MIMEText类，用于创建邮件内容
from EmailSender import EmailSender
from RunTimeContext import RunTimeContext
from WebWatcher import WebWatcher


if __name__ == "__main__":
    configFilePath = sys.argv[1]

    runtimeContext = RunTimeContext(configFilePath)

    targets = runtimeContext.get_targets()
    targetConfigs = runtimeContext.get_target_configs()
    observers = runtimeContext.get_observers()

    # 读取网页
    targetResults: dict[str, list[WebWatcher.WatchResult]] = {}
    for target, targetConfig in targetConfigs.items():
        watcher = WebWatcher(targetConfig, runtimeContext)
        targetResults[target] = watcher.webWatch(runtimeContext.get_last_run_time())

    # TODO: 格式化发送内容
    targetMsgs: dict[str, MIMEText] = {}
    for target, results in targetResults.items():
        targetMsgs[target] = MIMEText("\n".join(map(lambda x: str(x), results)), "plain", "utf-8")

    # TODO: 发送邮件
    emailSender = EmailSender(runtimeContext.get_email_config())
    if len(sys.argv) == 3 and sys.argv[2] == "test":  # 测试模式
        for target, msg in targetMsgs.items():
            print(bytes(msg.get_payload(decode=True)).decode(encoding="utf8"), observers[target],
                  targetConfigs[target].targetName)
    else:
        for target, msg in targetMsgs.items():  # 正常模式
            emailSender.sendEmail(msg, observers[target], Subject="新公告通知 " + targetConfigs[target].targetName)

    # 保存本次运行时间
    runtimeContext.dump_last_record()






