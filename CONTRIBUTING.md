# 课程维护与发布指南

本仓库是 NVIDIA DLI《深度学习基础》中文课程的 ModelScope 适配版。日常维护以 GitHub 的 `main` 分支为准：修改课程源文件、提交到 GitHub，由 GitHub Action 构建 HTML 并更新同一个公开灵感流。

- GitHub：https://github.com/VoyagerXvoyagerx/nvidia-dli-deep-learning-zh-modelscope
- 灵感流：https://modelscope.cn/gallery/VoyagerX/nvidia-dli-deep-learning-zh-modelscope
- Gallery ID：`cb1503c2-1458-4f67-b9c3-bd505091cb47`
- 自动发布：https://github.com/VoyagerXvoyagerx/nvidia-dli-deep-learning-zh-modelscope/actions/workflows/sync-gallery.yml

## 灵感流类型与入口

当前灵感流属于个人用户 **VoyagerX**，设置为公开，类型为 **`website`**，入口文件为 **`course_content/html/00_jupyterlab.html`**。Gallery 也包含 `index.ipynb` 和各课程 notebook，供下载、查看或在 ModelScope Notebook/IDE 中运行练习。

类型与入口后缀的规则如下，后缀不区分大小写：

| 类型 | 入口文件要求 | 用途 |
|---|---|---|
| `website` | `.html` | 当前课程的 HTML 预览 |
| `notebook` | `.ipynb` | 以 notebook 为入口 |
| `pdf` | `.pdf` | 以 PDF 为入口 |
| `file` | 不限制后缀 | 其他文件内容 |

同步脚本会读取并保留灵感流当前的类型、入口、名称和标签，保持 Gallery ID 和 URL。入口必须在本次发布清单中，且后缀与类型匹配；同步会明确设置为公开。若需更换入口或类型，可在灵感流管理页面修改，并确认新入口在 GitHub 的发布范围内。上传期间不要同时编辑、发布该灵感流，以免触发冲突检查。

## 课程文件与运行目录

| 路径 | 内容 |
|---|---|
| `index.ipynb` | 课程总览与初始化代码 |
| `course_content/tutorials/*.ipynb` | 课程正文和练习，日常编辑的主要源文件 |
| `course_content/tutorials/modelscope_assets.py` | 从 VoyagerX 的 ModelScope 仓库获取模型、数据集并加载本地资源 |
| `course_content/tutorials/images/`、`data/` | 图片、辅助数据及代码 |
| `course_content/html/` | 从 notebook 生成的静态 HTML 及本地样式、MathJax |
| `build_html.py` | HTML 构建脚本 |
| `scripts/sync_gallery.py` | Gallery 上传、更新与发布脚本 |
| `.github/workflows/sync-gallery.yml` | GitHub 自动发布工作流 |

编辑 notebook 时保留原课程练习、资源相对路径和许可证归属。新增模型、数据下载应通过 ModelScope 仓库完成，避免恢复 Hugging Face、Kaggle 或 PyTorch 外部下载；课程镜像已有依赖，不要添加重复安装或降级命令。

Notebook 初始化使用持久化目录 `/mnt/workspace/fundamentals-of-deep-learning-zh/tutorials/`：若该目录不存在，则从公开 Gallery 下载 `course_content/`，保存到 `/mnt/workspace/fundamentals-of-deep-learning-zh/`，随后切换工作目录并加入 Python 导入路径。API 返回空下载链接时会跳过并打印文件名。目录存在时不会自动重新下载；已有 Notebook 会话的本地文件需要按需重新下载更新。Gallery 临时挂载目录与 `/mnt/workspace` 的实际工作目录可能不同，排查相对路径时应检查当前工作目录。

## 本地构建 HTML

在仓库根目录执行。下面的依赖安装用于本地构建和维护环境；课程 Notebook 的目标镜像已预装依赖。

```bash
python -m pip install -r requirements-gallery-sync.txt
python build_html.py
python -m http.server 8000
```

浏览器打开 `http://localhost:8000/course_content/html/index.html`，检查课程导航、正文、图片、公式和代码显示。构建使用 nbformat、nbconvert、BeautifulSoup 和 Pygments，采用 D2L 风格侧栏与本页目录，图片嵌入 HTML，样式和 MathJax 从本地加载。**构建不执行 notebook，也不运行训练或填写练习。**

Notebook 是正文来源。不要只修改生成的 HTML，否则下一次构建会覆盖修改；页面布局、链接转换等应修改 `build_html.py`。本地重新生成的 HTML 可与 notebook 一起提交，保持 GitHub 中的预览文件更新。Action 还会再次构建 HTML 后上传到 Gallery，但不会自动把生成结果提交回 GitHub。

提交前检查：

```bash
python -m unittest discover -s tests -v
git add index.ipynb course_content/html
# 按修改范围补充 git add，例如课程 notebook、图片或构建脚本。
python scripts/sync_gallery.py --dry-run
git diff --cached --check
git diff --cached --stat
git commit -m "更新课程内容"
git push origin main
```

`--dry-run` 只检查和列出待发布文件，不联网，不需要 token。新文件须先 `git add` 才能进入 Git 跟踪文件清单；新构建的 HTML 文件会额外加入发布清单。

## GitHub Action 如何更新 Gallery

向 `main` 推送提交会触发 **Publish ModelScope Gallery**，也可从 Actions 页面选择 `main`，点击 **Run workflow** 手动执行。工作流使用 Ubuntu 24.04、Python 3.12，过程如下：

1. 拉取执行时最新的 `main`，安装构建与发布依赖。
2. 运行同步脚本测试，从 notebook 重建 HTML。
3. 筛选发布文件并检查数量、大小、路径与 notebook 内容。
4. 读取现有 Gallery，检查 VoyagerX 管理权限及入口类型。
5. 每批获取 6 个文件的草稿上传 URL，并发通过文件流上传到 OSS；遇到地址过期或可重试错误，会重新获取地址、从文件开头重试，并记录异常类型。
6. 检查草稿文件大小，并确认上传期间 Gallery 的已发布信息没有被修改。
7. 更新完整文件清单，再调用发布接口。
8. 读取发布结果，检查文件清单、公开状态、入口和类型，并在 Action Summary 中记录实际提交 SHA 与待内容审核的文件。

这是**全量同步**，每次上传全部选定文件，以新的清单发布；不只上传 Git diff 中的文件。移出清单的文件不再列在发布结果中，但脚本不负责清理旧草稿对象。任务串行执行，不取消正在上传、发布的任务；排队任务会使用执行时最新的 `main`。

认证使用仓库 Actions Secret **`MODELSCOPE_API_TOKEN`**，该 token 需要当前 VoyagerX Gallery 的管理员权限。密钥不写入源码；ModelScope 请求使用 Bearer token 和 `m_session_id` Cookie，OSS 上传只使用签名 URL，不附带 ModelScope token。

发布失败时先查看对应步骤的日志。上传失败、草稿大小不符或并发修改检查失败会阻止发布；更新清单和发布是两个请求，不是数据库事务，不承诺自动回滚。修复后可重新运行工作流。平台内容审核可能让部分已发布文件暂时没有下载链接，具体路径见 Action Summary。

### 发布范围

同时保留在 GitHub 和 Gallery：根目录的 `LICENSE`、`README.md`、`CONTRIBUTING.md`、`index.ipynb`、`build_html.py`，以及 `LICENSES/`、课程 notebook、图片、辅助代码与 HTML 预览。

仅保留在 GitHub：`ADAPTATION_REPORT.md`、`REUSE.toml`、`smoke_test.ipynb`、`THIRD_PARTY_NOTICES.md`、`VALIDATION.md`、`course_content/README.md`、`course_content/environment/`、`course_content/slides/`，以及工作流、同步脚本、测试和发布依赖列表。隐藏文件、运行缓存和 `model.pth` 不发布。

同步脚本采用 **50 文件预算**，(API 实际没有这个 50 的限制)。为加入本指南，重复的 `course_content/README.md` 改为仅保留在 GitHub。新增文件超过预算时，先调整 `scripts/sync_gallery.py` 的发布范围，再通过 `--dry-run` 检查，不能默默跳过新课程。脚本还检查单文件不超过 5 MiB。

### Gallery OpenAPI 使用说明

官方文档的 `POST /galleries`（服务完整路径 `/openapi/v1/galleries`）用于创建新的 Gallery：先上传得到文件 ID，再提交 `files` ID 列表，Gallery ID 由服务端生成。当前同步使用从 Gallery 网页前端代码、SDK 兼容实现中确认并实际验证的网页 HTTP API：

| 步骤 | 网页 HTTP API |
|---|---|
| 读取 Gallery | `GET /api/v1/gallery`，参数 `Gid` |
| 获取草稿上传 URL | `POST /api/v1/gallery/square/files/upload`，参数 `Gid`、`FileNames` |
| 上传文件内容 | 对返回的 OSS 签名 URL 执行 `PUT` |
| 检查草稿 | `GET /api/v1/gallery/square/files`，参数 `Gid`、`Draft: True` |
| 更新清单与信息 | `PUT /api/v1/gallery` |
| 发布 | `PUT /api/v1/gallery/publish` |

网页接口的 `Files` 是相对路径清单，更新请求中需编码为 JSON 字符串；它不是创建 OpenAPI 的文件 ID 列表。网页接口可能随平台改版变化，不能将其稳定性视为公开 OpenAPI 的承诺。若平台提供正式的更新、发布 OpenAPI，后续应迁移同步脚本。

##  Wish List

以下为产品改进心愿单：

- [ ] Gallery 的 files 增加每个文件的 `path` / `name` 及稳定 URL，方便直接分享、引用指定文件，并支持嵌套目录。例如希望提供 `https://modelscope.cn/gallery/VoyagerX/nvidia-dli-deep-learning-zh-modelscope/files/README.md`。这里是期望的 URL 形式。
- [ ] 运行后文件直接存入持久化目录

验收时应覆盖 notebook 与图片/模块同目录、嵌套目录、Gallery 临时挂载目录和 `/mnt/workspace` 持久化目录；打开 notebook 后无需手动 `os.chdir` 或插入 `sys.path`，即可正确显示图片并导入相应课程模块。
