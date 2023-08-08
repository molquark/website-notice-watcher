# 网站公告监视脚本

## 介绍

本脚本用于监视网站公告，当网站公告更新时，会自动发送邮件通知。

通过XPath解析网页

自定义网页解析XPath, 每个网页一个配置文件, 以适应不同网站的公告格式


## 使用方法

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 修改解析配置文件

参考`targetConfigs/`目录下的配置文件, 填入网址及解析公告的XPath,
以及对应时间, 标题, 链接的XPath.

解析配置文件命名格式为`自定义名.target.yaml`, 
如监视对象命名为`example`, 则配置文件名为`example.target.yaml`

3. 修改邮件配置文件

参考`secret.config.template.yaml`文件, 
填写对应信息后重命名为`secret.config.yaml`.

其中`observers`配置监视对象及通知的邮箱地址, 如监视对象为`example`, 
使用`myqq@qq.com`接收通知, 则配置为:

```yaml
observers:
  example:
    - myqq@qq.com
```

4. 指定配置文件路径

在`config.yaml`文件中指定了记录文件路径与解析配置文件的路径,
如需修改, 请修改`config.yaml`文件(如在系统定时任务中调用时, 修改为绝对路径)

5. 运行

```bash
python main.py <config.yaml文件路径>
```

参数必填, 为`config.yaml`文件路径, 
如在系统定时任务中调用时, 修改为绝对路径


## 依赖

- Python 3.6+
- lxml
- requests
- smtplib
- ...



