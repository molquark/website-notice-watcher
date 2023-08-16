import os
import re

from datetime import datetime# 时间处理
from typing import Union

import yaml  # 配置文件处理

from Config import Config
from EmailSender import EmailConfig
from SecretConfig import SecretConfig
from TargetConfig import TargetConfig


class RunTimeContext:
    """
    运行时上下文, 用于记录运行时信息, 主要为从配置文件读取配置并进行处理, 及记录本次运行时间
    """
    def __init__(self, config_file_path: str):
        self._lastRecord: dict[str, Union[str, dict[str, list[str]]]] = \
            {'sentMsgs': {}, 'lastRunTime': None, 'lastRunTimeFormat': None}
        # # 读取配置文件
        # 获取普通配置
        self._config = Config.fromYaml(config_file_path)
        self._machineTimeZone = Config.TimeZoneHandler\
            .get_timezone_or_default(self._config.timezone)
        # 记录本次运行时间
        self._thisRunTime: datetime = datetime.now(self._machineTimeZone)

        # 获取上次运行时间
        lastRunTimeLoad: str
        lastRunTimeFormat: str
        # 判断是否存在上次运行时间记录文件
        if not os.path.isfile(self._config.recordFilePath):
            # 不存在, 则创建
            self._lastRunTimeFormat = self._config.recordTimeFormat
            self.recordThisRunTime()
            self.dump_last_record()
            # 退出
            exit(0)
        # 读取上次运行记录
        with open(self._config.recordFilePath, encoding="UTF8") as f:
            out: dict = yaml.safe_load(f)
            lastRunTimeLoad = out["lastRunTime"]
            lastRunTimeFormat = out["lastRunTimeFormat"]
            self._lastRecord = out
        self._lastRunTime: datetime = datetime.strptime(lastRunTimeLoad, lastRunTimeFormat)
        self._lastRunTimeFormat: str = lastRunTimeFormat
        self.recordThisRunTime()  # 记录本次运行时间

        # 获取敏感配置
        self._secretConfig = SecretConfig.fromYaml("secret.config.yaml")
        self._observers: dict[str, list[str]] = self._secretConfig.getObservers()
        self._emailConfig = EmailConfig(self._secretConfig.getEmail())

        # 构建目标配置文件名
        self._targets = list(self._observers.keys())
        self._targets = {x: x + ".target.yaml" for x in self._targets}
        self._targets = {x: os.path.join(self._config.targetConfigPath, y) for x, y in self._targets.items()}

    def get_targets(self) -> dict[str, str]:
        return self._targets

    def get_target_configs(self) -> dict[str, TargetConfig]:
        """从目标配置文件读取配置, 返回目标与对应配置的字典"""
        targetConfigs: dict[str, TargetConfig] = {}
        for target, targetConfigFileName in self.get_targets().items():
            if not os.path.isfile(targetConfigFileName):
                raise FileNotFoundError(f"目标配置文件不存在: {targetConfigFileName}")
            targetConfig = TargetConfig.fromYaml(targetConfigFileName)
            targetConfigs[target] = targetConfig
        return targetConfigs

    def get_last_run_time(self):
        return self._lastRunTime

    def get_now_run_time(self):
        return self._thisRunTime

    def get_email_config(self):
        return self._emailConfig

    def get_observers(self):
        return self._observers

    def recordThisRunTime(self):
        self._lastRecord["lastRunTime"] = self._thisRunTime.strftime(self._lastRunTimeFormat)
        self._lastRecord["lastRunTimeFormat"] = self._lastRunTimeFormat

    def dump_last_record(self):
        # open(self._config.recordFilePath, "w", encoding="UTF8"),
        content = yaml.dump(self._lastRecord, allow_unicode=True).split("\n")
        matcher = re.compile(r"\s*- !!python/object.*")
        content = list(filter(lambda x: not matcher.match(x), content))
        with open(self._config.recordFilePath, "w", encoding="UTF8") as f:
            f.write("\n".join(content))

    def record_sent_msg(self, target: str, msg: str):
        if "sentMsgs" not in self._lastRecord or self._lastRecord["sentMsgs"] is None:
            self._lastRecord["sentMsgs"] = {}
        if target not in self._lastRecord["sentMsgs"]:
            self._lastRecord["sentMsgs"][target] = []
        self._lastRecord["sentMsgs"][target].append(msg)

    def get_sent_msgs(self, target: str):
        if "sentMsgs" not in self._lastRecord or self._lastRecord["sentMsgs"] is None:
            self._lastRecord["sentMsgs"] = {}
        ret = self._lastRecord["sentMsgs"].get(target)
        return [] if ret is None else ret

    def clear_sent_msgs(self, target: str):
        if "sentMsgs" not in self._lastRecord or self._lastRecord["sentMsgs"] is None:
            self._lastRecord["sentMsgs"] = {}
            return
        self._lastRecord["sentMsgs"][target] = []

