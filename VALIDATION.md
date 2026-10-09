# 适配验证记录

日期：2026-10-08。原课程：NVDLI/fundamentals-of-deep-learning-zh。适配者：VoyagerX。

## 验证方法与环境

本地 CPU：Python 3.12、PyTorch 2.6.0+cpu、TorchVision 0.21.0+cpu、Transformers 4.57.6。

命令 `python -m nbconvert --to notebook --execute smoke_test.ipynb --ExecutePreprocessor.kernel_name=python3` 在本容器启动内核时失败：`Operation not permitted` / `Kernel died before replying to kernel_info`。IPC 模式也被容器权限阻止。

因此按顺序在单一 Python 进程执行 **同一份 smoke_test.ipynb 的原样代码单元**，保存结果为 `smoke_test.executed.ipynb`。这验证了 Python 下载准备/加载/前向路径，不代表 Jupyter 内核或 ModelScope 云端 GPU 完整训练已经验证。测试使用已取得的完整本地资源；另行验证公开 ModelScope 仓库下载及远端文件大小/校验和。

## 测试结果

```text
2.6.0+cpu 0.21.0+cpu CUDA available: False
```

```text
MNIST: 60000 10000 first label: 5
```

```text
ASL-HG: (19200, 785) (4800, 785) 24-class forward pass OK
```

```text
Penny the Corgi: 202 images; original class folders retained
```

```text
VGG16: (1, 1000) predicted class: 179
```

```text
BERT masked LM: (1, 9, 28996) prediction: capital
```

```text
BERT QA: (1, 18) answer: berlin
All asset/model smoke checks passed.
```


## 课程差异

替换模型、数据集下载；保留缓存完整性检查、CPU 兼容路径和可选 torch.compile。当前版本删除所有 notebook 安装单元格和 torch 版本检查，精简目录定位与导入，统一开头，02 的平台介绍改为 ModelScope，删除指定 SPDX 单元格。其余正文及 FIXME/TODO 练习保留。05b 图片枚举兼容大写 .JPG。未缩短训练或更换数据集/权重。

完整课程训练未执行，课程包含待学习者填写的练习；04b 依赖 04a 的 model.pth。资源清单、原始来源与许可见 README.md 和各资源仓库。

## 当前镜像适配更新

用户提供的目标镜像为 torch 2.13.0、torchvision 0.28.0、transformers 5.16.1、modelscope 1.40.1，所需库均已预装。上述 CPU 推理结果属于此前适配验证，不代表当前目标镜像已验证。新版 notebook 清空历史输出；本次新增检查记录见 ADAPTATION_REPORT.md。

本次重新执行新版 `smoke_test.ipynb` 的全部代码单元格（单一 Python 进程，本地 CPU，已有完整资源缓存），全部通过；仅将 `/mnt/workspace` 的目录遍历映射到本地课程根目录，其他代码原样执行。MNIST 60,000/10,000；ASL 19,200/4,800、24 类；柯基 202 张；VGG16 输出 (1, 1000)、类别 179；BERT 掩码输出 capital，问答输出 berlin。11 个 notebook 格式/语法检查通过，辅助函数导入均有调用，FIXME/TODO 数量与原版一致。

## 固定目录初始化验证

新版所有 11 个 notebook 的固定目录为 `/mnt/workspace/fundamentals-of-deep-learning-zh/tutorials/`。本次通过模拟 API 响应验证三个分支：目录不存在时下载整个 course_content 并保留目录结构；目录已存在时完全跳过网络请求；下载失败时不创建 tutorials 目录，临时文件被清理。所有 notebook 初始化代码一致，格式与全部代码语法校验通过。本次未重新执行模型推理，资源和模型推理结果沿用上一次验证。


## 2026-10-09 课程下载与 HTML 验证

- 11 个 Notebook 通过 nbformat 校验；全部代码经过 IPython 输入转换后通过 Python 语法解析。
- 一行下载命令使用模拟接口验证：有效链接写入正确路径；空 URL 不发起请求，不创建空文件，并打印对应文件名。
- 10 个 HTML 页面构建成功，全部本地链接和脚本/样式引用可解析；每页课程目录含 10 个入口，正文 cell 数量与对应 Notebook 一致。
- 图片全部内嵌；页面没有远程 src 资源，MathJax 和 CSS 本地加载。构建不执行 Notebook。
- 浏览器截图验证未完成：本地 Chromium 下载返回不完整 ZIP，不能据此声称已进行视觉/交互运行验证。
- 本次未重新执行模型推理或完整 GPU 训练。
