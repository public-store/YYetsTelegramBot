这是一个人人影视资源搜索机器人，效果自行看演示就好 [戳我](https://cdn.jsdelivr.net/gh/AlphaBrock/md_img/macos/20200815001650.mp4)

目前实现的功能:
1. 输入任意内容可自行去人人影视查询，并返回资源海报
2. 通过点击返回的内容获取资源下载链接
3. 没事干加一个捐赠接口，需要扶贫

使用方法
1. 代码克隆
    ```
    git clone https://github.com/AlphaBrock/YYetsTelegramBot.git
    ```
2. 安装依赖
    ```
    pip install -r requirements.txt
    ```
3. 修改config.py进行配置，TOKEN 为 Bot 的 API
    ```
    TOKEN = 'Your TOKEN'
    ```
4. 添加启动服务
   创建单元文件：vim /lib/systemd/system/yyetsbot.service 自行替换输入如下信息
   ```
   [Unit]	
    Description=A Telegram Bot for querying YYets
    After=network.target network-online.target nss-lookup.target	
    
    [Service]	
    Restart=on-failure	
    Type=simple	
    ExecStart=/usr/bin/python3 /root/YYetsTelegramBot/src/main.py	
    
    [Install]	
    WantedBy=multi-user.target
   ```
   重新载入 daemon、自启、启动
   ```
    systemctl daemon-reload
    systemctl enable yyetsbot.service
    systemctl start yyetsbot.service
    ```