# NVIDIA DLI 当前资源清单

课程数据集保留在 NVIDIA_Training_and_Certification；模型直接复用魔搭已存在的同名 HF 仓库，不再依赖组织模型副本。

| 类型 | 当前下载仓库 | 用途 | 许可 |
|---|---|---|---|
| 数据集 | [NVIDIA_Training_and_Certification/mnist](https://modelscope.cn/datasets/NVIDIA_Training_and_Certification/mnist) | 01：手写数字，原始 IDX | MIT |
| 数据集 | [NVIDIA_Training_and_Certification/asl-hg](https://modelscope.cn/datasets/NVIDIA_Training_and_Certification/asl-hg) | 02–04：课程所需 CSV、24 类映射与原始数据 | CC-BY-4.0 |
| 数据集 | [NVIDIA_Training_and_Certification/penny-the-corgi](https://modelscope.cn/datasets/NVIDIA_Training_and_Certification/penny-the-corgi) | 05b：202 张图像 | CC-BY-4.0 |
| 模型 | [timm/vgg16.tv_in1k](https://modelscope.cn/models/timm/vgg16.tv_in1k) | 05a、05b：TorchVision VGG16 ImageNet 权重 | BSD-3-Clause |
| 模型 | [google-bert/bert-base-cased](https://modelscope.cn/models/google-bert/bert-base-cased) | 06：掩码语言模型 | Apache-2.0 |
| 模型 | [google-bert/bert-large-uncased-whole-word-masking-finetuned-squad](https://modelscope.cn/models/google-bert/bert-large-uncased-whole-word-masking-finetuned-squad) | 06：问答模型 | Apache-2.0 |

## 当前适配与核验

- Notebook 运行时只从 ModelScope 下载，不访问 HF、Kaggle 或 PyTorch 外部下载站。
- 两个 BERT 所需的 model.safetensors、config.json、tokenizer.json、tokenizer_config.json、vocab.txt，与原组织备份逐文件远端 SHA-256 相同；这不是重新下载完整权重后计算摘要。
- VGG16 读取已有 timm 仓库的 model.safetensors。卷积 features 参数不变；将 pre_logits.fc1/fc2、head.fc 的六个权重/偏置参数映射并 reshape 到 TorchVision classifier，使用 strict=True 保留课程模型接口，不新增 timm 运行依赖。实际验证见 VALIDATION.md。
- 当前逐文件元数据见 [course_assets_manifest.json](course_assets_manifest.json)。优先复用现有资源的规则同样适用于数据集；课程派生 CSV 等缺失资源才需要单独托管。

## 历史：2026-10-23 所有者转移

此前 3 个数据集、3 个模型共 50 文件、3,010,774,389 字节由 VoyagerX 转移至组织，数值 ID、远端摘要、大小和 Git 版本保留。原个人路径为 404；当时没有执行 DELETE。该历史快照保留在 [history/asset-transfer-2026-10-23.json](history/asset-transfer-2026-10-23.json)，其中旧模型路径不再是课程依赖。

组织重复模型的清理由用户单独授权，在替代代码完成发布与回读核验后执行；三个组织数据集保留。
