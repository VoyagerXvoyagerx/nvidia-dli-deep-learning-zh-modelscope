# NVIDIA DLI 深度学习基础 · ModelScope Notebook 适配版

原始课程：https://github.com/NVDLI/fundamentals-of-deep-learning-zh 。原作者为 NVIDIA DLI；由 VoyagerX 适配下载、环境与路径逻辑。

## 在 ModelScope Notebook 中运行

1. 在本 Gallery 点击“运行”，保留全部文件和目录结构。
2. 打开 `course_content/tutorials/` 中的课程 notebook，按 00、01、02、03、04a、04b、05a、05b、06 的顺序学习。
3. 直接运行初始化单元格：检查 `/mnt/workspace/fundamentals-of-deep-learning-zh/tutorials/`；不存在则从公开灵感流下载 `course_content` 到 `/mnt/workspace/fundamentals-of-deep-learning-zh/`，然后切换到 `tutorials/`。
4. 使用镜像预装库：PyTorch 2.13.0、TorchVision 0.28.0、Transformers 5.16.1、ModelScope 1.40.1 等。无需 pip 安装、降级或版本断言。
5. 模型和数据首次从 modelscope.cn 下载，后续使用 `tutorial_assets/` 缓存。Hugging Face/Kaggle/PyTorch 外部下载被替换，无外网备用下载路径。

原课程中的 `FIXME` / `TODO` 练习仍保留，须由学习者填写。04b 需要先完成 04a，生成 `model.pth`。`torch.compile` 默认关闭；如确需启用，设置 `DLI_USE_TORCH_COMPILE=1`。

## 已搬运的资源

| 类型 | ModelScope 仓库 | 原来源 | 许可 |
|---|---|---|---|
| 数据集 | [VoyagerX/mnist](https://modelscope.cn/datasets/VoyagerX/mnist) | TorchVision OSSCI MNIST 原始 IDX；许可信息来自 ylecun/mnist | MIT |
| 数据集 | [VoyagerX/asl-hg](https://modelscope.cn/datasets/VoyagerX/asl-hg) | juanjodurillo/asl-hg；原始记录 DOI 10.17632/j4y5w2c8w9.1 | CC-BY-4.0 |
| 数据集 | [VoyagerX/penny-the-corgi](https://modelscope.cn/datasets/VoyagerX/penny-the-corgi) | Kaggle danielledetering/penny-the-corgi，版本 1 | CC-BY-4.0 |
| 模型 | [VoyagerX/vgg16-imagenet1k](https://modelscope.cn/models/VoyagerX/vgg16-imagenet1k) | TorchVision 原始 vgg16-397923af.pth；timm/vgg16.tv_in1k 模型卡 | BSD-3-Clause |
| 模型 | [VoyagerX/bert-base-cased](https://modelscope.cn/models/VoyagerX/bert-base-cased) | Google BERT，经 ModelScope google-bert 仓库获取 | Apache-2.0 |
| 模型 | [VoyagerX/bert-large-uncased-whole-word-masking-finetuned-squad](https://modelscope.cn/models/VoyagerX/bert-large-uncased-whole-word-masking-finetuned-squad) | Google BERT SQuAD，经 ModelScope google-bert 仓库获取 | Apache-2.0 |

ASL 保留原始 Parquet，并按照原课程算法生成 28×28 灰度 CSV：去掉 0–9、J、Z，按字母排序重新映射为 24 类，训练 19,200 张、验证 4,800 张。没有替换为其他手语 MNIST 数据集。柯基数据保留原版两类目录和 202 张图片（Penny 116 张、Not_Penny 86 张）。

## 验证与限制

[smoke_test.ipynb](https://github.com/VoyagerXvoyagerx/nvidia-dli-deep-learning-zh-modelscope/blob/main/smoke_test.ipynb) 用于检查三个数据集、VGG16 分类、BERT 掩码预测与问答前向推理。具体结果见 [VALIDATION.md](https://github.com/VoyagerXvoyagerx/nvidia-dli-deep-learning-zh-modelscope/blob/main/VALIDATION.md)。

课程的文档外链仅用于阅读；执行路径不依赖它们。完整训练未自动执行，原课程保留待填写练习。验证使用本地 CPU 环境；当前修改依据用户提供的云端镜像库清单；未在该云端镜像执行完整课程训练。

## 许可与变更

课程代码 Apache-2.0；非代码课程内容 CC-BY-4.0；第三方媒体许可见 [THIRD_PARTY_NOTICES.md](https://github.com/VoyagerXvoyagerx/nvidia-dli-deep-learning-zh-modelscope/blob/main/THIRD_PARTY_NOTICES.md)。保留 `LICENSE`、`LICENSES/` 和第三方归属说明。本版新增 ModelScope 资源 helper、简化目录初始化和最小验证 notebook；替换模型/数据下载和本地读取逻辑。开头统一简化、02 的平台介绍改为 ModelScope，删除 notebook 的 SPDX 单元格，保留仓库许可证与第三方归属；其余课程正文和练习保留。详见 [适配改动报告](https://github.com/VoyagerXvoyagerx/nvidia-dli-deep-learning-zh-modelscope/blob/main/ADAPTATION_REPORT.md)。


## HTML 课程预览

入口：[course_content/html/index.html](course_content/html/index.html)。页面采用 D2L 风格的课程侧栏、本页目录、蓝色顶栏和代码高亮。图片嵌入 HTML，MathJax 与样式从本地加载。构建不执行 Notebook。

在仓库根目录运行：

```bash
python build_html.py
```

随后直接打开 `course_content/html/index.html`，或运行 `python -m http.server 8000` 后访问 `http://localhost:8000/course_content/html/`。构建需要 nbconvert、nbformat、beautifulsoup4、pygments，目标镜像已预装。

## GitHub 与 Gallery 文件范围

报告、`REUSE.toml`、`smoke_test.ipynb`、第三方来源说明、`VALIDATION.md`、`course_content/README.md`、`course_content/environment/` 和 `course_content/slides/` 仅在 [GitHub](https://github.com/VoyagerXvoyagerx/nvidia-dli-deep-learning-zh-modelscope) 保留。灵感流仅提供课程运行与预览所需文件。首次下载会跳过接口返回的空链接并打印文件名；这表示对应文件未下载。目录存在时不会自动更新。

## GitHub 提交后自动发布灵感流

推送到 `main` 后，[Publish ModelScope Gallery](https://github.com/VoyagerXvoyagerx/nvidia-dli-deep-learning-zh-modelscope/actions/workflows/sync-gallery.yml) 自动测试同步脚本、从 notebook 重建 HTML，并将课程上传、发布到[现有公开灵感流](https://modelscope.cn/gallery/VoyagerX/nvidia-dli-deep-learning-zh-modelscope)。保留灵感流当前的入口文件、类别、名称和标签；入口必须仍在发布清单内。也可在 Actions 页面点击 **Run workflow** 手动重试。排队任务取执行时最新的 `main`；上传与发布串行执行，不取消正在发布的任务。HTML 构建不执行课程训练，也不向 GitHub 自动提交文件。

认证由仓库 Actions Secret `MODELSCOPE_API_TOKEN` 提供，需使用有该灵感流管理员权限的 VoyagerX token。密钥不会写入源码或发往 OSS 文件上传地址。工作流、同步脚本、依赖列表和自动化测试仅在 GitHub 保留。

同步文件从 Git 跟踪文件中选择根目录 `LICENSE`、`README.md`、`CONTRIBUTING.md`、`index.ipynb`、`build_html.py`，以及 `LICENSES/` 和 `course_content/`，并加入本次生成的 HTML。上述 GitHub 专属目录、运行缓存和隐藏文件除外。当前共 50 个文件，达到同步脚本采用的文件预算（参考创建 OpenAPI，不代表网页更新接口的官方限制）；新增文件超过上限会使 Action 失败，需调整发布范围后重试，不会默默遗漏新课程。上传失败、草稿文件大小不符或检测到灵感流被同时修改时，不执行发布。平台内容审核可能使部分已发布文件暂时没有下载链接，文件名会显示在 Action Summary 中。

接口说明：公开 OpenAPI 的 `POST /openapi/v1/galleries` 目前只支持创建，未提供更新已有 Gallery 的接口。本工作流为保持 ID 和 URL，使用 Gallery 网页的 HTTP API：获取信息 `GET /api/v1/gallery`，获取草稿上传地址 `POST /api/v1/gallery/square/files/upload`，校验草稿 `GET /api/v1/gallery/square/files`，更新文件清单 `PUT /api/v1/gallery`，发布 `PUT /api/v1/gallery/publish`。这些网页接口可能随平台改版变化；认证或接口变化会在 Actions 中报错。

本地检查（不联网、不需要 token）：

```bash
python -m pip install -r requirements-gallery-sync.txt
python -m unittest discover -s tests -v
python build_html.py
python scripts/sync_gallery.py --dry-run
```

课程维护、灵感流类型、HTML 构建、自动发布和魔搭产品侧 TODO，详见 [CONTRIBUTING.md](https://github.com/VoyagerXvoyagerx/nvidia-dli-deep-learning-zh-modelscope/blob/main/CONTRIBUTING.md)。该指南也同步到 Gallery；为维持 50 文件预算，重复的 `course_content/README.md` 仅保留在 GitHub。
