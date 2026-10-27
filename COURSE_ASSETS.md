# NVIDIA DLI 当前资源清单

课程数据集来自 AI-ModelScope；模型直接复用魔搭已存在的同名 HF 仓库，不再依赖组织模型副本。

| 类型 | 当前下载仓库 | 用途 | 许可 |
|---|---|---|---|
| 数据集 | [AI-ModelScope/MNIST](https://modelscope.cn/datasets/AI-ModelScope/MNIST) | 01：手写数字，复用现有 raw/MNIST.tar.gz 中相同的 IDX gzip 文件 | MIT |
| 数据集 | [AI-ModelScope/asl-hg](https://modelscope.cn/datasets/AI-ModelScope/asl-hg) | 02–04：课程所需 CSV、24 类映射与原始数据 | CC-BY-4.0 |
| 数据集 | [AI-ModelScope/penny-the-corgi](https://modelscope.cn/datasets/AI-ModelScope/penny-the-corgi) | 05b：202 张图像 | CC-BY-4.0 |
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

## 2026-10-27 资源更新

MNIST 复用魔搭现有 AI-ModelScope/MNIST；该仓库标注 Apache-2.0，原数据来源许可说明沿用课程 README。实际下载的 raw/MNIST.tar.gz 为 11,597,129 字节，SHA-256：0c238d89673aa552c96e688f8f2d0e2c1fd6001d5feca288ff66811030e6f790。包内四个 gzip 文件与原组织备份的实际摘要完全一致，因此无需创建重复 MNIST 镜像。ASL-HG 与柯基通过所有者转移进入 AI-ModelScope，逐文件校验记录见本次迁移清单。
