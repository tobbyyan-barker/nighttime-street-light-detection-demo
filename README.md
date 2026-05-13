# Nighttime Street Light Detection Demo

## 项目简介

本项目是一个基于 YOLO 的夜间道路路灯检测 Demo，主要用于展示目标检测模型在夜间道路场景中的检测效果。

用户可以通过网页端上传夜间道路图片，后端使用训练好的 YOLO 模型进行目标检测，并将检测结果返回到前端页面。前端会展示原始图片、检测结果图、检测目标数量、类别标签和置信度信息。

目前该 Demo 主要在本地环境运行，已经实现了从图片上传、后端模型推理到前端结果可视化展示的完整流程。

---

## 项目功能

- 支持上传 `.jpg`、`.jpeg`、`.png` 格式的图片
- 支持在网页端预览上传的原始图片
- 使用 YOLO 模型进行路灯目标检测
- 返回带有检测框、类别标签和置信度的结果图
- 展示检测目标数量和置信度列表
- 支持通过置信度阈值调整检测结果

---

## 技术栈

- 前端：HTML5 / CSS / JavaScript
- 后端：Flask API
- 模型：YOLO
- 图像处理：OpenCV
- 数据交互：FormData / JSON

---

## 项目结构

```text
yolo_demo/
├── app.py                    # Flask 后端入口，负责图片接收、模型推理和结果返回
├── best.pt                   # 训练好的 YOLO 模型权重，本仓库默认不上传
├── templates/
│   └── index.html            # 前端页面结构
└── static/
    ├── script.js             # 前端交互逻辑：图片预览、POST 请求和结果渲染
    ├── style.css             # 页面样式文件
    ├── uploads/              # 保存用户上传的原始图片
    └── results/              # 保存模型生成的检测结果图片
```
# 夜间道路路灯检测 Demo 项目文档

## 环境依赖

建议使用 **Python 3.10 或以上版本**。

### 主要依赖
text
flask
ultralytics
opencv-python
### 安装方式

#### 方式一：通过 requirements.txt 安装
```pip install -r requirements.txt```
#### 方式二：手动安装

```pip install flask ultralytics opencv-python```
---

## 运行方式

### 1. 克隆项目
```git clone https://github.com/tobbyyan-barker/nighttime-street-light-detection-demo.git```
cd nighttime-street-light-detection-demo
### 2. 准备模型权重

> ⚠️ 由于模型权重文件通常较大，`best.pt` 默认不上传到 GitHub。 后续会通过百度网盘上传

请将训练好的 YOLO 权重文件放在项目**根目录**下，并命名为：
best.pt
项目根目录结构示例：
yolo_demo/
├── app.py
├── best.pt
├── templates/
└── static/
### 3. 启动 Flask 服务

```python app.py```
启动成功后，在浏览器中打开：

👉 http://127.0.0.1:5000

即可使用本地网页 Demo。

---

## 使用流程

1. 打开本地网页 Demo  
2. 点击 **Choose Image** 上传夜间道路图片  
3. 调整 **置信度阈值**  
4. 点击 **Start Detection**  
5. 查看以下内容：
   - 原始图片
   - 检测结果图
   - 检测目标数量
   - 置信度列表

---

## 当前状态

✅ 已完成功能：

- YOLO 模型本地推理  
- Flask 后端接口搭建  
- 前端图片上传与预览  
- 检测结果图返回与展示  
- 检测目标数量和置信度信息展示  
- 本地 Demo 运行验证  

📌 当前 Demo **尚未部署到云服务器**，主要用于本地展示和项目复现。

---

## 后续计划

- ☁️ 将 Demo 部署到云服务器，开放在线访问链接  
- 🛡️ 增加上传文件大小限制，提升系统稳定性  
- 🎨 优化前端页面交互体验  
- 🌃 支持更多夜间道路场景测试  
- 🎥 尝试扩展短视频检测功能  

### 关于短视频检测的说明
后端可逐帧抽取视频图像，调用 YOLO 模型进行检测，再将检测后的图像帧重新合成为视频返回前端展示。  
考虑到服务器带宽、存储和推理成本，**视频上传大小将进行限制**。

---

## 项目说明

本项目主要用于展示 **夜间道路路灯检测任务** 中的以下流程：

- 数据处理
- 模型训练
- 误检分析
- Web Demo 搭建

### 项目重点

本项目不仅关注模型训练，还涵盖：

- 数据整理与标注  
- 模型训练与评估  
- Precision、Recall、mAP 等指标分析  
- 复杂背景下的误检和漏检分析  
- 前后端交互与模型推理展示  

### 项目收获

通过本项目，进一步理解了 **计算机视觉项目从数据、模型到应用展示的完整流程**。
