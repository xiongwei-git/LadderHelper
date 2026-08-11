# 静态文档站部署说明

本项目使用 VitePress 构建静态文档站。构建产物在：

```text
.vitepress/dist
```

服务器只需要托管这个目录里的静态文件。

## 本地预览

```bash
npm install
npm run dev
```

默认本地地址：

```text
http://localhost:5173/
```

## 构建静态文件

```bash
npm run build
```

构建完成后，把 `.vitepress/dist` 目录里的内容上传到服务器网站根目录。

如果服务器上已经启用了访问统计，上传前清理网站根目录时要保留 `_stats` 目录，否则统计页会被删掉。定时任务会重新生成它，但中间会短暂无法访问。

## 访问统计

站点可以通过服务器 Nginx 访问日志生成一个私有统计页，不需要在公开页面里加入第三方统计脚本。

统计脚本位置：

```text
tools/generate_nginx_stats.py
```

服务器上的统计页建议放在：

```text
https://ladder.tedxiong.com/_stats/
```

这个页面会展示访问 IP、页面访问量、来源页面和浏览器信息，必须加账号密码保护，不建议公开分享截图。

当前线上实现方式：

- 服务器脚本：`/usr/local/bin/ladder-generate-stats.py`
- 读取日志：`/www/wwwlogs/ladder.tedxiong.com.log`
- 输出页面：`/www/wwwroot/ladder.tedxiong.com/_stats/index.html`
- Nginx 保护配置：`/www/server/panel/vhost/nginx/extension/ladder.tedxiong.com/stats.conf`
- 自动刷新：服务器 crontab 每 10 分钟生成一次

## Nginx 示例配置

```nginx
server {
    listen 80;
    server_name your-doc-domain.example.com;

    root /path/to/ladder-helper-site;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(?:css|js|png|jpg|jpeg|gif|svg|webp|ico|woff2?)$ {
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
        try_files $uri =404;
    }
}
```

如果后面配置 HTTPS，只需要把同一个静态目录继续作为站点根目录即可。
