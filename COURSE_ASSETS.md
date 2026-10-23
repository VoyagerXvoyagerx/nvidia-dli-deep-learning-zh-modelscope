# NVIDIA DLI 课程资源清单与迁移记录

日期：2026-10-23。原所有者：`VoyagerX`；现所有者：`NVIDIA_Training_and_Certification`。

本次直接转移了 **3 个数据集、3 个模型，共 50 个文件、3,010,774,389 字节（约 2.80 GiB）**，全部保持公开。仓库数值 ID 与文件 Git 版本保留；原个人路径均返回 HTTP 404，个人名下未保留这六个仓库的副本。

| 类型 | 当前仓库 | 课程用途 | 许可 | 文件数 | 大小（MiB） |
|---|---|---|---|---:|---:|
| 数据集 | [mnist](https://modelscope.cn/datasets/NVIDIA_Training_and_Certification/mnist) | 01：MNIST 手写数字 | mit | 8 | 11.06 |
| 数据集 | [asl-hg](https://modelscope.cn/datasets/NVIDIA_Training_and_Certification/asl-hg) | 02–04：手语分类、CNN、数据增强与预测 | cc-by-4.0 | 11 | 437.12 |
| 数据集 | [penny-the-corgi](https://modelscope.cn/datasets/NVIDIA_Training_and_Certification/penny-the-corgi) | 05b：柯基识别与迁移学习 | cc-by-4.0 | 5 | 199.89 |
| 模型 | [vgg16-imagenet1k](https://modelscope.cn/models/NVIDIA_Training_and_Certification/vgg16-imagenet1k) | 05a、05b：VGG16 图像分类与迁移学习 | bsd-3-clause | 6 | 527.80 |
| 模型 | [bert-base-cased](https://modelscope.cn/models/NVIDIA_Training_and_Certification/bert-base-cased) | 06：BERT 掩码语言模型 | apache-2.0 | 10 | 416.21 |
| 模型 | [bert-large-uncased-whole-word-masking-finetuned-squad](https://modelscope.cn/models/NVIDIA_Training_and_Certification/bert-large-uncased-whole-word-masking-finetuned-squad) | 06：BERT SQuAD 问答 | apache-2.0 | 10 | 1279.20 |

## 迁移与核验

- 使用官网设置页所用的网页兼容接口进行所有者转移；官方 OpenAPI 当前未列出此操作。模型使用 `POST /api/v1/models/{owner}/{name}/rename`，数据集使用 `POST /api/v1/datasets/rename/repo`。
- 转移前记录仓库数值 ID、文件路径、大小、SHA-256、Git 版本与 LFS 标记；转移后逐项比对，50 个文件完全一致。这里的文件摘要来自远端文件清单，并非重新下载全部 3.01 GB 后计算。
- 每个组织仓库均匿名完整下载 README，并计算 SHA-256 与远端记录比对；另匿名读取最大文件的前 1024 字节，确认可取得真实载荷及正确文件总大小。
- 六个原个人 API 路径均返回 HTTP 404。所有者转移已经移除了个人名下的独立仓库，因此没有再执行仓库 DELETE。
- 逐文件清单与校验值见 [course_assets_manifest.json](course_assets_manifest.json)。

## 课程代码与发布

- `course_content/tutorials/modelscope_assets.py` 的六个下载 ID 均使用组织命名空间。
- 更新全部 Notebook 的资源来源说明、ASL 仓库链接/注释、README 和适配报告；保留 VoyagerX 的适配者署名。
- HTML 从 Notebook 重建，GitHub Actions 校验后自动同步现有组织 Gallery；本清单和 JSON 核验记录保留在 GitHub。
- 本次验证覆盖所有者、文件一致性和公开下载链路；历史前向推理结果见 [VALIDATION.md](VALIDATION.md)，本次未重新执行模型推理或完整课程训练。
