# OpenAI_wechat_bot
如果你有基于 openai 的 key，可以用这个项目定制自己的微信机器人，来作为你的聊天替身，或者客服，或者私人学习工作助理

## 介绍
这是一个微信机器人项目，将openai的chatgpt接入微信，把你的微信号变成一个机器人。
在这个项目，你可以通过设置prompt词和example示例来调教AI成为聊天小伙伴，插科打诨小能手，客服机器人，论文帮手等，也可以不做任何调教，仅作为随时随地对接chatgpt的便利工具。
### 用法
1，安装环境

- Windows系统
- 微信PC客户端
- Python3.6+
- 
下载本项目的requirements.txt文件，在命令行中运行以下命令
```bash
pip install -r requirements.txt
```
2，从以下网址下载wxauto库整个文件夹。注意不是pip install wxauto

```bash
git clone https://github.com/cluic/wxauto.git
```
或者直接访问网址下载

3，复制wx_robot_gui.py到wxauto根目录下

4，在文件夹里创建.env文件，填写你的openai api key
```bash
OPENAI_API_KEY='your key'
OPENAI_BASE_URL='url'
```
5，根据wxauto页面提示安装对应的pc端微信并登录

6，运行 UI界面一目了然，不再多介绍
```bash
python wx_robot_gui.py
```
## 功能
- 自动回复
- 自动回复群聊
- 设置群聊触发关键词
- 设置群聊自动接话概率
- 设置prompt引导内容
- 设置回复示例内容
- 设置temperature值
- 设置白名单，非白名单无法回复

## 注意事项
- 因为wxauto的运行机制，程序在模拟真人操作微信客户端，需要时间点击，读取等等，如果短时间内消息过多，会造成消息的漏收漏发，当然这一点可以尽量在代码中优化。
- 微信机器人项目有封号风险。虽然我已经选择了wxauto这个最模拟真人操作的库，但是微信官方是不支持不鼓励微信机器人的，被发现的话仍然有被封号的风险。
- 欢迎魔改，欢迎提issue，欢迎pr
- 如果遇到问题，欢迎添加我的微信咨询（尽量回复，不保证随时能看到消息）：DragonSmaug

## 最后
如果对您有帮助，希望可以帮忙点个Star，如果您正在使用这个项目，可以将右上角的 Unwatch 点为 Watching，以便在我更新或修复某些 Bug 后即使收到反馈，感谢您的支持，非常感谢！

## 免责声明
代码仅供交流学习使用，请勿用于非法用途和商业用途！如因此产生任何法律纠纷，均与作者无关！

## 支持
非常感谢您对该项目的支持
