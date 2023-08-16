from typing import Union

import yaml
from datetime import datetime, timezone, timedelta

from Config import Config


class TargetConfig(Config):
    """
    TargetConfig, read the *target.yaml file
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self._config["timezone"] = Config.TimeZoneHandler\
            .get_timezone_or_default(self._config.get("timezone", None))

    def setUrl(self, url: str):
        self._config["url"] = url

    @classmethod
    def fromYaml(cls, path: str):
        with open(path, encoding="UTF8") as f:
            out: dict = yaml.safe_load(f)
            obj = cls(out)
            return obj

    def getBaseUrl(self):
        return self._config["baseUrl"]

    def getUrl(self):
        return self._config["url"]

    def getPageXPath(self):
        return self._config["pageXPath"]

    def getTimeXPath(self):
        return self._config["timeXPath"]

    def getTimeFormat(self):
        return self._config["timeFormat"]

    def getTitleXPath(self):
        return self._config["titleXPath"]

    def getHrefXPath(self):
        return self._config["hrefXPath"]

    def getTimezone(self) -> timezone:
        return self._config["timezone"]

    def isOnlyDate(self) -> bool:
        return self._config.get("onlyDate", False)

    def getTarget(self) -> str:
        return self._config["target"]


# 驱动程序
if __name__ == "__main__":
    targetConfig = TargetConfig.fromYaml("targetConfigs/scut.target.yaml")
    print(targetConfig)