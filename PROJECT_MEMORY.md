# PROJECT_MEMORY：LadderHelper

## 项目目的

为零基础读者提供从域名、VPS、DNS 到 3x-ui 部署与客户端验证的图文教程站点。

## 内容与安全边界

- 教程必须以清晰、分步、可验证的说明面向非技术用户，并明确适用条件、风险和法律/服务条款边界。
- 云服务商、产品版本、界面、价格、端口、安装命令和可用性会变化；更新前须检查权威来源与当前测试环境。
- 不收录真实服务器、订阅、账号、密钥、二维码、完整私密 URL 或个人网络配置。
- `README.md`、`docs/`、`SUMMARY.md`、构建工具与部署文档共同构成当前内容事实来源。

## 当前状态与 Native Memory 边界

- 注册表标记为 active；继续前先确认目标读者、发布方式和需更新的章节。
- 未发现对应 Native 项目任务组。教程细节只保留在本项目，不进入 Native Memory。

## Project Card

- home: Mac mini
- category: personal-documentation
- runtime: static-site；当前不部署，后续部署目标另行确认
- repository_model: single-repo
- source_of_truth: 本目录的教程正文、构建配置、图片资源与部署说明
- git: GitHub private；`origin` 是唯一权威远端
- mirror: none
- vps_source: none
- sensitivity: 不纳入真实服务器、订阅、账号、密钥、二维码、完整私密 URL 或个人网络配置
- sync: Git clone / pull 到两台工作台；构建缓存和依赖目录仅本地生成
- shared_memory: 不写入教程细节、环境或配置快照
- status: migrated
- last_reviewed: 2026-08-11
