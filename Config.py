from datetime import timezone, timedelta

import yaml


class Config:
    """
    该类及子类用于读取配置文件, 不提供修改配置文件的方法, 以防止误操作
    该类不提供修改配置的方法, 使得运行过程属性不可变
    """
    def __init__(self, config: dict):
        self._config: dict = config.copy()

    @classmethod
    def fromYaml(cls, path: str):
        return cls(Config.loadYaml(path))

    @staticmethod
    def loadYaml(path: str) -> dict:
        with open(path, encoding="UTF8") as f:
            out: dict = yaml.safe_load(f)
            return out

    def __getattr__(self, item):
        r = self._config.get(item, None)
        return r

    def __str__(self):
        return str(self._config)

    class TimeZoneHandler:
        @staticmethod
        def get_timezone_or_default(timezoneConfig: dict) -> timezone:
            _k_timezone = "timezone"
            _k_timedelta = "timedelta"

            if timezoneConfig is None or timezoneConfig.get(_k_timedelta, None) is None:
                # 未设置时区, 则使用默认+0800
                timezoneConfig = {"timedelta": {"hours": 8}, "name": "UTC+08:00"}

            timezoneConfig = timezone(timedelta(**timezoneConfig[_k_timedelta]), timezoneConfig.get("name", None))
            return timezoneConfig
