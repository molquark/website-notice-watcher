from Config import Config


class SecretConfig(Config):

    def __init__(self, config: dict):
        super().__init__(config)

    @classmethod
    def fromYaml(cls, path: str):
        return cls(Config.loadYaml(path))

    def getEmail(self):
        return self._config["email"]

    def getObservers(self) -> list:
        return self._config["observers"]



# 驱动程序
if __name__ == "__main__":
    sc = SecretConfig.fromYaml("./secret.config.yaml")
    print(sc)

