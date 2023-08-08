import datetime
from email.mime.text import MIMEText
import smtplib
from typing import Sequence, Union

import SecretConfig
from Config import Config


class EmailConfig(Config):
    def __init__(self, config: dict):
        super().__init__(config)

    def getSender(self):
        return self._config["sender"]

    def getPasswd(self):
        return self._config["passwd"]

    def isSMTP_SSL_ON(self):
        return self._config["SMTP_SSL_ON"]

    def getSMTP_SSL(self):
        return self._config["SMTP_SSL"]

    def isSMTP_TLS_ON(self):
        return self._config["SMTP_TLS_ON"]

    def getSMTP_TLS(self):
        return self._config["SMTP_TLS"]


class EmailSender:

    class EmailConnector:
        def __init__(self, emailConfig: EmailConfig):
            self._emailConfig = emailConfig
            self.smtp: smtplib.SMTP = None

        def __connect_built(self):
            if self._emailConfig.isSMTP_SSL_ON():
                self.smtp = smtplib.SMTP_SSL(**self._emailConfig.getSMTP_SSL())
            elif self._emailConfig.isSMTP_TLS_ON():
                self.smtp = smtplib.SMTP(**self._emailConfig.getSMTP_TLS())
            else:
                raise RuntimeError("SMTP_SSL or SMTP_TLS must be ON")

        def connect(self):
            if self.smtp is None:
                self.__connect_built()
            if self._emailConfig.isSMTP_TLS_ON():
                self.smtp.starttls()
            self.smtp.login(self._emailConfig.getSender(),
                            self._emailConfig.getPasswd())

        def sendmail(self, to: Union[str, Sequence[str]], msg: MIMEText):
            if self.smtp is None:
                self.connect()
            self.smtp.sendmail(self._emailConfig.getSender(), to, msg.as_string())

        def quit(self):
            self.smtp.quit()
            self.smtp = None

        def getSender(self):
            return self._emailConfig.getSender()

    def __init__(self, emailConfig: EmailConfig):
        self._emailConnector = self.EmailConnector(emailConfig)

    # 发送邮件
    def sendEmail(self, msg: MIMEText, receivers: Union[str, Sequence[str]], Subject: str = None,
                  From: str = None, To: str = None):
        if Subject is not None:
            msg['Subject'] = Subject
        msg['From'] = From if From is not None else self._emailConnector.getSender()  # 发送方邮箱
        if To is not None:
            msg['To'] = To  # 收件人
        try:
            self._emailConnector.sendmail(receivers, msg)
        except Exception as e:
            raise e
        finally:
            self._emailConnector.quit()

    def sendPlainEmail(self, title: str, msg: str, receivers: Union[str, Sequence[str]]):
        m = MIMEText(msg, 'plain', 'utf-8')
        self.sendEmail(m, receivers, Subject=title)


if __name__ == "__main__":
    secret = SecretConfig.SecretConfig.fromYaml("./secret.config.yaml")
    emailConfig = EmailConfig(secret.email)
    emailSender = EmailSender(emailConfig)
    m = MIMEText(f"You will be attach to the web watcher! {datetime.datetime.now()}", 'plain', 'utf-8')

    emailSender.sendEmail(m, "xxx@outlook.com", Subject="The title", To="xxxx")