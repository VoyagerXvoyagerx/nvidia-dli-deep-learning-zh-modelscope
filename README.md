# 《深度学习基础》| NVIDIA 开源课程（ModelScope 适配 · 免费 GPU · 零配置）

**《深度学习基础》** 是 NVIDIA 深度学习培训中心（DLI）官方出品的入门级深度学习课程，现已作为 NVIDIA 开源课程面向个人学习者、教育机构、企业及开发者社区开放，提供可直接获取和使用的课程内容与实验材料。

深度学习理论是整个 AI 技术体系的**基石**——本课覆盖的概念与方法，是后续所有 NVIDIA 高阶课程（生成式 AI / LLM、加速计算、Agentic AI、Physical AI、AI Factory）**必备的前置知识**。

**在 ModelScope 上怎么学？**

- **算力免费**：ModelScope 提供免费 GPU 环境，无需自备显卡、无需本地部署；
- **环境零配置**：PyTorch、TorchVision、Transformers、ModelScope 等核心库镜像预装，一行 `pip` 都不用敲；
- **资源国内直连**：3 个数据集 + 3 个预训练模型全部搬运至 modelscope.cn，告别外网超时；
- **课程资料齐全**：每个模块配套 PPT 讲义（`course_content/slides/`）与 Notebook 实验（`course_content/tutorials/`），按 00 → 01 → 02 → 03 → 04a → 04b → 05a → 05b → 06 顺序学习即可。

**学习意义**

学完本课程，你将具备独立构建、训练并部署神经网络的能力——下一步就能用这些本领去做自己真正想做的项目：搭一个图像分类应用、微调一个专属模型，或给物理世界装上"AI 眼睛"。从这块基石出发，你的 AI 之路前途无量。

> 🚀 想进一步衔接 NVIDIA 进阶培训与认证？直达官网：[NVIDIA 培训和认证中文官网](https://www.nvidia.cn/training/?ncid=bn-prom-596593-modelscope)

---

## 学习成果

完成本课程的实验后，学员将能够：

- 使用 PyTorch 在真实图像数据集上构建并训练神经网络
- 将卷积神经网络（CNN）应用于图像分类任务
- 利用数据增强与迁移学习提升有限数据集上的模型精度
- 理解偏差-方差权衡，并掌握应对过拟合的技术手段
- 部署已训练的模型，对新的未见数据进行预测

---

## 课程模块

| #   | 模块        | 幻灯片                                                  | Notebook                                                                                                                                                              |
| --- | --------- | ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01  | 深度学习简介    | [slides_01.pptx](./course_content/slides/part1.pptx) | [01_mnist.ipynb](./course_content/tutorials/01_mnist.ipynb)                                                                                                           |
| 02  | 神经网络的训练方式 | [slides_02.pptx](./course_content/slides/part2.pptx) | [02_asl.ipynb](./course_content/tutorials/02_asl.ipynb)                                                                                                               |
| 03  | 卷积神经网络    | [slides_03.pptx](./course_content/slides/part3.pptx) | [03_asl_cnn.ipynb](./course_content/tutorials/03_asl_cnn.ipynb)                                                                                                       |
| 04  | 数据增强与模型部署 | [slides_04.pptx](./course_content/slides/part4.pptx) | [04a_asl_augmentation.ipynb](./course_content/tutorials/04a_asl_augmentation.ipynb) [04b_asl_predictions.ipynb](./course_content/tutorials/04b_asl_predictions.ipynb) |
| 05  | 预训练模型     | [slides_05.pptx](./course_content/slides/part5.pptx) | [05a_doggy_door.ipynb](./course_content/tutorials/05a_doggy_door.ipynb) [05b_corgi_door.ipynb](./course_content/tutorials/05b_corgi_door.ipynb)                       |
| 06  | 高级架构      | [slides_06.pptx](./course_content/slides/part6.pptx) | [06_nlp.ipynb](./course_content/tutorials/06_nlp.ipynb)                                                                                                               |

---

## 在 ModelScope Notebook 中运行

1. 在本网站上方点击"运行"或"查看和运行 Notebook"，按新版 Notebook 弹窗把项目复制到 `/mnt/workspace` 持久化存储，保留全部文件和目录结构。
2. 打开 `course_content/tutorials/` 中的课程 notebook，按 00、01、02、03、04a、04b、05a、05b、06 的顺序学习。
3. 初始化只需一行 `%cd "/mnt/workspace/Gallery: NVIDIA_Training_and_Certification_NVIDIA-DLI-Deep-Learning-ZH-ModelScope/course_content/tutorials"`，随后导入本课需要的 helper；不再自动下载项目或修改 sys.path。实际复制目录若被重命名，应同步调整该行路径。
4. 使用镜像预装库：PyTorch 2.13.0、TorchVision 0.28.0、Transformers 5.16.1、ModelScope 1.40.1 等。无需 pip 安装、降级或版本断言。
5. 模型和数据首次从 modelscope.cn 下载，后续使用 `tutorial_assets/` 缓存。Hugging Face/Kaggle/PyTorch 外部下载被替换，无外网备用下载路径。

原课程中的 `FIXME` / `TODO` 练习仍保留，须由学习者填写。04b 需要先完成 04a，生成 `model.pth`。`torch.compile` 默认关闭；如确需启用，设置 `DLI_USE_TORCH_COMPILE=1`。

---

## 验证与限制

[smoke_test.ipynb](https://github.com/VoyagerXvoyagerx/nvidia-dli-deep-learning-zh-modelscope/blob/main/smoke_test.ipynb) 用于检查三个数据集、VGG16 分类、BERT 掩码预测与问答前向推理。具体结果见 [VALIDATION.md](https://github.com/VoyagerXvoyagerx/nvidia-dli-deep-learning-zh-modelscope/blob/main/VALIDATION.md)。

课程的文档外链仅用于阅读；执行路径不依赖它们。完整训练未自动执行，原课程保留待填写练习。验证使用本地 CPU 环境；当前修改依据用户提供的云端镜像库清单；未在该云端镜像执行完整课程训练。

---

## 许可与变更

> 本项目改编（或再分发）自 NVIDIA Deep Learning Institute 开源课程《Fundamentals of Deep Learning（深度学习基础）》— 中文版。
>
> - **原始来源**：[NVDLI/fundamentals-of-deep-learning-zh · README.md](https://github.com/NVDLI/fundamentals-of-deep-learning-zh/blob/main/README.md?ncid=bn-prom-622541-modelscope)
> - **原始版权**：© NVIDIA Corporation

本项目内容采用双重许可：

- **源代码及 Notebook 代码单元格**：Apache License 2.0 — [全文](https://www.apache.org/licenses/LICENSE-2.0)
- **文档、Markdown、Notebook 非代码单元格及教学媒体**：CC-BY-4.0（署名 4.0 国际）— [全文](https://creativecommons.org/licenses/by/4.0/)

> ⚠️ 具体适用范围及要求**以原仓库为准**：[NVDLI/fundamentals-of-deep-learning-zh](https://github.com/NVDLI/fundamentals-of-deep-learning-zh/blob/main/README.md?ncid=bn-prom-622541-modelscope)

第三方媒体许可见 [THIRD_PARTY_NOTICES.md](https://github.com/VoyagerXvoyagerx/nvidia-dli-deep-learning-zh-modelscope/blob/main/THIRD_PARTY_NOTICES.md)。保留 `LICENSE`、`LICENSES/` 和第三方归属说明。本版新增 ModelScope 资源 helper、简化目录初始化和最小验证 notebook；替换模型/数据下载和本地读取逻辑。开头统一简化、02 的平台介绍改为 ModelScope，删除 notebook 的 SPDX 单元格，保留仓库许可证与第三方归属；其余课程正文和练习保留。详见 [适配改动报告](https://github.com/VoyagerXvoyagerx/nvidia-dli-deep-learning-zh-modelscope/blob/main/ADAPTATION_REPORT.md)。

---

## 开源课程

- [深度学习基础](https://github.com/NVDLI/fundamentals-of-deep-learning-zh?ncid=bn-prom-622541-modelscope)
- [NVIDIA 开源课程目录](https://www.nvidia.cn/training/open-source/?ncid=bn-prom-460536-modelscope)

## 更多资源

- [NVIDIA 培训和认证中文官网 >](https://www.nvidia.cn/training/?ncid=bn-prom-596593-modelscope)
- [NVIDIA 认证 >](https://www.nvidia.cn/training/certification/?ncid=bn-prom-860160-modelscope)
- [在线自主培训 >](https://www.nvidia.cn/training/self-paced-courses/?ncid=bn-prom-508293-modelscope)
- [讲师指导的培训班 >](https://www.nvidia.cn/training/instructor-led-workshops/?ncid=bn-prom-315129-modelscope)
