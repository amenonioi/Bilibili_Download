# Bilibili_Download
Download video or audio from bilibili

## 注意

* 软件不支持付费视频和地区限制视频，可能会报错
* 需要使用sessdata进行账号登录，sessdata仅用于获取视频的下载权限
* 未登录仅能下载最高480p视频，普通用户最大支持下载1080P视频，大会员最大支持下载8K视频
* b站视频是音画分离的，故可选择只下载视频或只下载音频，如两者同时选择下载，则会进行音视频合并

## 使用

* 在[releases](https://github.com/amenonioi/Bilibili_Download/releases)页面下载，python版本需自行安装requests库
  ```bash
  $ python -m pip install requests
  ```
* 若已有ffmpeg并已添加至环境变量，则无需下载带ffmpeg的版本

## 功能

* 下载视频
* 下载音频
* 下载封面
* 下载 合集/收藏夹/分p视频 的中全部视频
* 下载动漫


## sessdata的获取

使用chrome浏览器打开b站，在登录状态下
右键 -> 检查 -> application -> cookies -> sessdata
复制下方cookie value中的内容

![1](./screenshots/screenshot1.png)
![2](./screenshots/screenshot2.png)
![3](./screenshots/screenshot3.png)


## 闲话
这是一个做着玩的项目，功能跟其他下载器相差不大，如有不足请谅解
通常来说只要把网址完整的复制粘贴进程序就可以正常运行，如果没成功那可能是程序写的太菜了，没处理好
