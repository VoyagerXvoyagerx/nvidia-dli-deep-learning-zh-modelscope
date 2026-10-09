# NVIDIA DLI 深度学习基础：魔搭适配改动报告

更新日期：2026-10-08。适配者：VoyagerX。

原版：[NVDLI/fundamentals-of-deep-learning-zh](https://github.com/NVDLI/fundamentals-of-deep-learning-zh)。
公开适配版：[NVIDIA DLI at ModelScope Notebook](https://www.modelscope.cn/gallery/VoyagerX/nvidia-dli-deep-learning-zh-modelscope)。

## 相比原版的改动

| 范围 | 原版 | 魔搭适配版 |
|---|---|---|
| 运行环境 | 原仓库部署及依赖安装流程 | 使用用户提供的 ModelScope Notebook 镜像预装库；所有 notebook 均无需 pip 安装或依赖降级 |
| 数据下载 | MNIST 从 TorchVision 外部下载站；ASL 从 Hugging Face；柯基从 Kaggle | 三个数据集统一从 VoyagerX 的公开 ModelScope 仓库下载，保留原始来源和许可说明 |
| 模型下载 | VGG16 由 TorchVision 下载权重，BERT 通过 Hugging Face 模型标识加载 | VGG16 从 ModelScope 获取原始权重后加载；BERT 从 ModelScope 下载到本地，使用 `local_files_only=True` |
| 资源辅助代码 | 各课程分别触发外部下载 | 新增 `modelscope_assets.py`，负责按需下载、缓存、解压、完整性检查，以及 HF 离线设置；无外部备用下载路径 |
| 工作目录 | 相对路径依赖 Notebook 的当前工作目录 | 所有 11 个 notebook 检查固定目录 `/mnt/workspace/fundamentals-of-deep-learning-zh/tutorials/`，不存在时从公开灵感流下载整个 `course_content`，保存到 `/mnt/workspace/fundamentals-of-deep-learning-zh/`；随后切换到 `tutorials/` 并加入 Python 导入路径 |
| 初始化与导入 | 先前适配版含统一安装、版本检查和全量辅助函数导入 | 删除安装单元格、PyTorch/TorchVision 版本断言、无关导入及重复导入；每个课程仅导入实际使用的辅助函数 |
| 开头与平台说明 | NVIDIA 原版标题；02 中介绍 Hugging Face Hub | 所有 11 个 notebook 开头统一为用户指定的 NVIDIA DLI at ModelScope Notebook 介绍；02 改为介绍 ModelScope 和 VoyagerX/asl-hg |
| Notebook 许可证单元格 | 独立 SPDX 注释单元格 | 按用户要求删除；仓库 `LICENSE`、`LICENSES/`、第三方归属及资源许可保留 |
| 执行兼容性 | 原版部分代码直接依赖 CUDA、默认编译模型 | 保留 CPU/GPU 设备选择；`maybe_compile` 默认使用普通执行，设置 `DLI_USE_TORCH_COMPILE=1` 可启用编译 |
| 课程完整性 | 课程讲解、训练任务、练习和配套材料 | 保留其余正文、学习任务、FIXME/TODO 练习、图片、辅助代码和六份 PPT；未填写练习答案或缩短训练 |

课程源文件、图片和辅助代码继续保留 `course_content/tutorials/` 的相对目录结构。04a 训练得到的 `model.pth` 供 04b 使用；04b 增加了缺少该文件时的说明。

## 各课程的具体改动

| Notebook | 必要辅助函数 | 特定适配 |
|---|---|---|
| `00_jupyterlab.ipynb` | 无 | 删除不必要的 PyTorch 导入；新增同一课程目录下载/初始化单元格，保留 JupyterLab 入门内容 |
| `01_mnist.ipynb` | `prepare_mnist`、`maybe_compile` | 先准备 ModelScope MNIST，再以 `download=False` 读取；保留 60,000/10,000 样本规模 |
| `02_asl.ipynb` | `prepare_asl as download_asl_dataset`、`maybe_compile` | ModelScope 数据获取及缓存；替换 2.2.1 的 Hugging Face 平台介绍 |
| `03_asl_cnn.ipynb` | 同 02 | 沿用同一 ASL 数据和原 CNN 练习 |
| `04a_asl_augmentation.ipynb` | 同 02 | 沿用原数据增强与训练任务，仍生成供 04b 使用的 `model.pth` |
| `04b_asl_predictions.ipynb` | 无 | 仅保留目录初始化及课程原有导入；使用前一课程产生的本地模型 |
| `05a_doggy_door.ipynb` | `load_vgg16` | 使用 ModelScope 镜像中的原始 VGG16 权重；保留 ImageNet 预处理和分类逻辑 |
| `05b_corgi_door.ipynb` | `prepare_corgi`、`load_vgg16` | 保留原始柯基数据目录；图片枚举兼容大写 `.JPG`，覆盖全部 202 张图片 |
| `06_nlp.ipynb` | `prepare_bert` | 两个 BERT 模型及 tokenizer 都使用 ModelScope 下载后的本地目录；删除未使用的 `BertModel` 导入 |
| `index.ipynb` | 无 | 更新课程入口及直接运行说明，增加同一课程目录下载/初始化单元格 |
| `smoke_test.ipynb` | 三种数据准备函数、`load_vgg16`、`prepare_bert` | 更新目录初始化，删除先安装再重启的说明；保留资源和前向推理验证 |

## ModelScope 资源与来源

| 类型 | ModelScope 仓库 | 原始来源 |
|---|---|---|
| MNIST | [VoyagerX/mnist](https://modelscope.cn/datasets/VoyagerX/mnist) | TorchVision 使用的原始 MNIST IDX 文件 |
| ASL | [VoyagerX/asl-hg](https://modelscope.cn/datasets/VoyagerX/asl-hg) | `juanjodurillo/asl-hg`；原始 ASL-HG 数据记录 DOI 10.17632/j4y5w2c8w9.1 |
| 柯基 | [VoyagerX/penny-the-corgi](https://modelscope.cn/datasets/VoyagerX/penny-the-corgi) | Kaggle `danielledetering/penny-the-corgi`，版本 1 |
| VGG16 | [VoyagerX/vgg16-imagenet1k](https://modelscope.cn/models/VoyagerX/vgg16-imagenet1k) | TorchVision `vgg16-397923af.pth` |
| BERT 掩码模型 | [VoyagerX/bert-base-cased](https://modelscope.cn/models/VoyagerX/bert-base-cased) | Google BERT `bert-base-cased` |
| BERT 问答模型 | [VoyagerX/bert-large-uncased-whole-word-masking-finetuned-squad](https://modelscope.cn/models/VoyagerX/bert-large-uncased-whole-word-masking-finetuned-squad) | Google BERT SQuAD 问答权重 |

ASL 镜像保留原始 Parquet，同时提供按原课程规则生成的 CSV：28×28 灰度、去除数字和 J/Z、24 类，训练 19,200 张、验证 4,800 张。没有替换成其他手语 MNIST 数据集。柯基数据含 Penny 116 张、Not_Penny 86 张，保留两类目录。资源的首次下载和以后缓存读取均由 ModelScope helper 管理。

## 本次更新针对的镜像

用户提供的库清单已包括课程所需的 torch 2.13.0、torchvision 0.28.0、transformers 5.16.1、modelscope 1.40.1、numpy 2.5.2、pandas 2.3.3、pillow 11.3.0、matplotlib 3.11.1、safetensors 0.8.0 和 tqdm 4.70.0。因此删除先前适配版的 `%pip` 单元格，避免把 Transformers 降到 4.57.6；`requirements.txt` 改为镜像版本注释记录，README 和入口同步删除安装/重启要求。

## 验证范围

本次对 11 个 notebook 进行 nbformat 格式校验和全部代码单元格的 Python 语法校验，均通过。确认安装命令、版本断言、指定 SPDX 单元格均已删除，所有导入的 ModelScope 辅助函数均实际使用，课程 FIXME/TODO 标记数量与原版一致。

本次用本地 CPU 和已有完整资源缓存运行新版 `smoke_test.ipynb` 的代码，模拟 `/mnt/workspace` 子目录定位，验证数据、模型和前向推理；具体结果见 `VALIDATION.md`。本地使用 PyTorch 2.6.0+cpu、TorchVision 0.21.0+cpu、Transformers 4.57.6，不能替代目标镜像的运行验证。

尚未在用户提供的云端镜像执行完整 GPU 训练，也未自动完成课程练习。04b 仍需先完成 04a。首次下载大型权重时需要等待 ModelScope 下载完成。

## 固定目录与首次下载更新

所有 11 个 notebook 共用同一初始化代码。固定课程根目录为 `/mnt/workspace/fundamentals-of-deep-learning-zh/`，notebook、辅助代码和数据路径位于 `tutorials/`。该子目录存在时跳过下载；不存在时，通过已验证的灵感流网页 API 下载 `course_content/` 全部文件，包含 slides、environment 和 tutorials，保留内部目录结构。公开 Gallery 无需 token。文件先下载到临时目录，全部成功后再安装 tutorials 目录；下载失败不会留下被下次运行误判为完整课程的 tutorials 目录。已有课程目录不会自动覆盖更新。

本次固定目录更新的验证覆盖缺失、已有、下载失败三个分支，采用模拟 API 响应；11 个 notebook 的初始化代码一致，格式和语法检查通过。模型推理代码未改变，沿用此前的资源/推理验证记录。


## 2026-10-09 更新

- 11 个 Notebook 初始化 cell 改为条件执行的一行 `!python -c` 下载命令，保留中文注释，跳过空 URL 并打印文件名。固定目录与必要函数导入保留。
- 增加 `build_html.py`，不执行 Notebook，自动生成 10 个 D2L 风格 HTML 阅读页面，位于 `course_content/html/`。支持课程搜索、本页目录、代码复制、前后课导航、嵌入图片及本地 MathJax。
- 报告、REUSE、smoke_test、第三方来源、验证记录、environment 与 slides 在完整 GitHub 版本保留；Gallery 清理这些文件，入口改用 GitHub 链接。
- 已恢复原课程的 part3.pptx 与 imagenet_class_index.json；Gallery 公共下载接口此前对这两个待审核文件返回空 URL。
- 预览只展示 Notebook 已保存的输出，不生成训练结果。
