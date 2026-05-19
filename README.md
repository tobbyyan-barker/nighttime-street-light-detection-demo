# Nighttime Street Light Detection Demo

## 项目简介

本项目是一个基于 YOLO 的夜间道路路灯检测 Demo，主要用于展示目标检测模型在夜间道路场景中的检测效果。

该Demo支持两种输入方式，图片检测和短视频检测:

### 1. 图片检测:
用户可以通过网页端上传夜间道路图片，后端使用训练好的 YOLO 模型进行目标检测，并将检测结果返回到前端页面。
前端会展示原始图片、检测结果图、检测目标数量、类别标签和置信度信息。

### 2. 短视频检测:
用户也可以上传大小不超过20MB的夜间道路短视频。
后端会先保存用户上传的视频，并读取视频总帧数和FPS(frames per second), 从而计算视频总时长。对视频总时长超过10s的视频，只取前10s进行检测。
随后，后端使用OpenCV按固定时间间隔抽帧，再逐帧调用YOLO模型进行检测，最终在前端以图片Gallery的形式展示视频抽帧后的检测结果。

目前该 Demo 主要在本地环境运行，已经实现了从图片/视频上传、后端模型推理到前端结果可视化展示的完整流程。

---

## Demo
### Video Detection Demo
![Video Detection Demo](assets/yolo-demo-video-formal-preview1.gif)

## 项目功能

### 图片检测功能
- 支持上传 `.jpg`、`.jpeg`、`.png` 格式的图片
- 支持在网页端预览上传的原始图片
- 使用 YOLO 模型进行路灯目标检测
- 返回带有检测框、类别标签和置信度的结果图
- 展示检测目标数量和置信度列表
- 支持通过置信度阈值调整检测结果

### 视频检测功能
- 支持上传大小不超过20MB的短视频文件进行检测。
- 后端使用OpenCV读取视频总帧数和FPS，并计算视频总时长。
- 对于总时长超过10s的视频，只截取前10s进行检测; 对于总时长不超过10s的视频,直接进行抽帧检测。
- 后端按照固定的时间间隔(FRAME_SAMPLE_INTERVAL_SEC)对视频进行抽帧检测。
- 默认抽帧频率是1FPS，即每秒抽一帧图片进行检测。
- 保存抽取出的每一帧原始图片。
- 对抽取出的每一帧调用YOLO模型进行推理。
- 保存每一帧的检测结果图。
- 前端以Gallery的形式展示视频检测结果，包括抽帧数量,总的检测框数量，每一帧的检测结果。
- 支持通过置信度阈值调整视频帧的检测结果。
---

## 技术栈

- 前端：HTML5 / CSS / JavaScript
- 后端：Flask API
- 模型：YOLO11s
- 图像和视频处理：OpenCV
- 数据交互：FormData / JSON

---

## 项目结构
```text
yolo_demo/
├── app.py # Flask 后端入口，负责图片/视频接收、模型推理和结果返回
├── best.pt # 训练好的 YOLO 模型权重（默认不上传）
├── requirements.txt # Python 依赖列表
├── templates/
│ └── index.html # 前端页面结构
└── static/
├── script.js # 前端交互逻辑：图片/视频上传、POST 请求和结果渲染
├── style.css # 页面样式文件
├── uploads/ # 保存用户上传的原始文件
│ └── videos/ # 保存用户上传的视频
├── frames/ # 保存视频抽帧后的图片
└── results/ # 保存模型生成的检测结果图片
└── video_frames/ # 保存视频帧检测后的结果图
```
---

## 环境依赖

建议使用 **Python 3.10 或以上版本**。

### 主要依赖
flask
ultralytics
opencv-python-headless

### 安装方式
#### 方式一：通过 requirements.txt 安装

```bash
pip install -r requirements.txt
```

#### 方式二：手动安装

```bash
pip install flask ultralytics opencv-python-headless
```
---

## 运行方式

### 1. 克隆项目
```bash
git clone https://github.com/tobbyyan-barker/nighttime-street-light-detection-demo.git
cd nighttime-street-light-detection-demo
```
### 2. 准备模型权重

> ⚠️ 由于模型权重文件通常较大，`best.pt` 默认不会上传到 GitHub。  
> 模型权重可通过网盘等方式单独提供。

请将训练好的 YOLO 权重文件放在项目**根目录**下，并命名为：
```text
best.pt
```
项目根目录结构示例：
```text
yolo_demo/
├── app.py
├── best.pt
├── templates/
└── static/
```
### 3. 启动本地Flask 服务

在本地开发或调试时，可以直接运行:

```bash
python app.py
```
启动成功后，用户可在浏览器中打开：

👉 http://127.0.0.1:5000

即可使用本地网页 Demo。

### 4. 服务器部署运行
在云服务器上，本项目使用Gunicorn 作为WSGI服务，并通过systemd后台管理Gunicorn的运行状态:

```bash
systemctl start yolo_demo
systemctl status yolo_demo
```

注: 此命令中,yolo_demo表示systemd的服务名。
注: yolo_demo 不是一个额外的软件，而是本项目部署过程自定义的名称。在systemd中，yolo_demo.service 用来后台管理 Gunicorn 服务；
    在 Nginx 中，sites-available/yolo_demo 是站点反向代理配置文件。二者名称相同只是为了便于识别和管理，实际运行的是 Flask + YOLO 推理服务。

如果服务正常运行，状态中会显示:
```text
Active: active (running)
```

本项目服务器部署链路如下:
```text
用户通过浏览器访问网站: (http://公网IP）
            ↓
用户请求转发到Nginx的80端口
            ↓
Nginx作为反向代理，将请求转发到http://127.0.0.1:5000
            ↓
Gunicorn 在本机http://127.0.0.1:5000上加载python app.py项目里的名为app的Flask对象
            ↓
Flask后端接收图片上传请求, 并调用YOLO模型进行目标检测
            ↓
检测结果通过后端接口返回给前端页面进行展示
```

## 使用流程

### 图片检测教程

1. 打开本地网页 Demo  
2. 点击 **Choose Image** 上传夜间道路图片  
3. 调整 **置信度阈值**  
4. 点击 **Start Detection**  
5. 查看以下内容：
   - 原始图片
   - 检测结果图
   - 检测目标数量
   - 置信度列表

### 视频检测流程

1. 打开本地网页Demo
2. 点击 **Choose Video** 上传夜间道路短视频
3. 调整 **置信度阈值**
4. 点击 **Start Video Detection**
5. 后端自动完成视频保存，抽帧和逐帧YOLO检测，
6. 后端完成视频处理后，返回 JSON 格式的检测结果，包括：
   - **视频处理状态信息**
   - **视频文件路径**
   - **视频文件大小**
   - **视频总时长**
   - **实际处理时长**
   - **原视频 FPS**
   - **抽帧间隔**
   - **抽帧数量**
   - **视频帧检测到的目标总数**
   - **每一帧的检测结果列表**

7. 前端根据后端返回的数据展示视频检测结果：
   - **Video Size**：视频文件大小
   - **Video Duration**：视频总时长
   - **Processed Duration**：实际参与检测的视频时长
   - **Extracted Frames**：抽帧数量
   - **Total Detected Objects**：视频帧检测到的目标总数
   - **Video Detection Results**：逐帧检测结果图 Gallery

### 视频检测实现逻辑

视频检测并不是直接将完整视频输入YOLO模型，而是先使用OpenCV将视频拆分成若干个关键帧，再对抽出的每一帧作为图片输入YOLO模型进行检测。

后端处理流程如下:
```text
上传视频
→ Flask通过request.files["video"] 来接收文件
→ 检查视频文件大小，限制上传文件不超过 20MB
→ 将视频保存到/static/uploads/videos
→ 使用cv2.VideoCapture方法打开视频文件
→ 获取原始视频FPS和总帧数
→ 根据原始视频FPS和总帧数计算视频总时长
→ 如果视频时长超过10秒，只处理前10秒；否则处理完整视频
→ 设置抽帧时间间隔 FRAME_SAMPLE_INTERVAL_SEC，本项目默认为 1，即每 1 秒抽取 1 帧
→ 将抽帧频率转换为帧间隔 frame_interval
→ 按 frame_interval 从视频中抽取帧图片
→ 保存抽帧图片到/static/frames
→ 对每一帧调用YOLO模型进行目标检测
→ 使用自定义绘图函数生成检测结果图，在图中主要展示检测框和置信度信息
→ 将类别，置信度信息等详细信息整理为结构化结构，交由右侧Result区域展示
→ 用JSON格式打包抽帧数量，视频帧检测到的目标总数和逐帧检测结果图给前端
→ 前端根据JSON数据以Gallery的形式渲染统计卡片和检测结果
```

其中，抽帧逻辑的核心思想是将“按秒抽帧”转换为“按帧间隔抽帧”。例如，若原视频 FPS 为 30，且设置 `FRAME_SAMPLE_INTERVAL_SEC = 1`，则每隔约 30 帧抽取 1 帧用于检测。
为了避免图像中类别文字与多个检测框重叠，本项目没有直接使用 YOLO 默认的 `result.plot()` 可视化方式，而是通过**自定义绘图逻辑**在检测图中保留更清晰的检测框和置信度信息，并将类别等详细结果放在右侧 Result 区域展示。

## 当前状态

✅ 已完成功能：

### 图片检测

- YOLO 模型本地推理
- Flask 后端接口搭建
- 前端图片上传与预览
- 图片检测结果图返回与展示
- 检测目标数量、类别和置信度信息展示

### 视频检测

- 视频上传功能
- 上传文件大小限制
- OpenCV 视频读取与抽帧
- 视频帧 YOLO 批量检测
- 视频检测统计信息返回
- 视频检测结果 Gallery 展示

### 本地运行

- 本地 Demo 运行验证
- 已完成从图片/视频上传、后端推理到前端结果展示的完整流程


📌 当前 Demo **已完成云服务器的部署**，可通过公网IP进行在线访问。
部署环境采用 Alibaba Cloud ECS + Ubuntu 22.04，后端使用 Flask 提供推理接口，Gunicorn作为WSGI服务，加载app.py文件
里名为app的Flask对象，systemd负责后台管理Gunicorn,Nginx作为反向代理对外提供web访问。
---

- ☁️ 已部署至阿里云 ECS 云服务器，支持公网访问  
- 🚀 使用 Gunicorn 运行 Flask 后端服务  
- 🔁 使用 systemd 管理后端进程，支持后台运行与服务重启  
- 🌐 使用 Nginx 进行反向代理，将公网 80 端口请求转发至本机 Flask 服务  
- 🧠 支持上传夜间道路图片，并返回 YOLO 路灯检测结果 


## 后续计划
  
- 🎨 优化前端页面交互体验和检测结果展示方式
- 🎥 将视频帧检测结果进一步合成为检测后视频  
- 🌃 补充远距离小目标、遮挡路灯和复杂光源场景样本 
- 🔍 增加误检/漏检案例自动整理功能
- 🤖 探索 Agent 辅助误检分析与数据优化建议生成 

### 关于短视频检测的说明
当前版本已支持本地短视频上传与抽帧检测。考虑到云服务器的带宽、存储空间和模型推理成本，后续部署到服务器后，视频上传大小和处理时长可能会进一步限制。

因此，视频检测功能目前主要用于展示“上传视频 → 后端抽帧 → 逐帧检测 → 前端 Gallery 展示”的完整流程，而不是实时视频流检测。

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
- YOLO模型训练与评估  
- Precision、Recall、mAP 等指标分析  
- 复杂背景下的误检和漏检分析  
- Flask后短推理和前端页面交互
- 图片上传,模型推理，检测结果可视化显示
- 视频抽帧结果与结果Gallery显示
- 云服务器部署与公网访问配置
- Gunicorn，systemd和Nginx 组成的基础部署链路实践  

### 项目收获

通过本项目，进一步理解了 **计算机视觉项目从数据、模型到应用展示的完整流程**。

本项目不仅完成了 YOLO 模型训练与图片检测 Demo，还进一步扩展到了视频检测场景。通过视频上传、OpenCV 抽帧、YOLO 逐帧推理和前端 Gallery 展示，初步构建了一个面向夜间道路场景的目标检测工程闭环。

在视频测试过程中也发现，模型对近距离和中距离清晰路灯具有较稳定的检测能力，但对远距离小目标、遮挡目标和复杂光源干扰场景仍有提升空间。这为后续数据集补充、漏检和误检分析提供了明确方向。

在部署方面，本项目已部署至云服务器，并使用Gunicorn加载app.py文件里名为app的Flask对象，从而运行Flask后端服务, systemd进行后台Gunicorn管理, Nginx作为反向代理把用户的请求转发到本地5000端口(http://127.0.0.1:5000)。通过这一过程，我初步理解了 AI 模型从本地推理Demo到公网在线服务的部署流程，也认识到工程化部署中端口管理、虚拟环境、服务管理和反向代理的重要性。
