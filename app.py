from flask import Flask, render_template, request, jsonify
from ultralytics import YOLO
import os
import uuid
import cv2

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
RESULT_FOLDER = "static/results"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# 定义常量 目的: 限制用户上传的视频大小和时长(考虑到服务器带宽和计算资源的限制) 视频长度小于10s 视频大小小于20MB 
# 本demo: 大小超限 --- 直接拒绝 时长超限 --- 只处理前10s 并返回warning提示
MAX_VIDEO_SIZE_MB = 20
MAX_DURATION_SEC = 10

# 加载 YOLO 模型
model = YOLO("best.pt")

#自定义画框函数 自定义绘制检测框
def draw_boxes_conf_only(image_path, result, save_path):
    """
    自定义绘制检测框：
    - 只在框上显示置信度，比如 0.68
    - 不显示 class name，比如 street light
    """
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Failed to read image: {image_path}")

    for box in result.boxes:
        # 取检测框坐标
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

        # 取置信度，只显示置信度
        confidence = float(box.conf[0])
        label = f"{confidence:.2f}"

        # 蓝色框：OpenCV 使用 BGR，所以 (255, 0, 0) 是蓝色
        box_color = (255, 0, 0)
        text_color = (255, 255, 255)

        # 框线粗细
        cv2.rectangle(image, (x1, y1), (x2, y2), box_color, 2)

        # 标签样式
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness = 1

        text_size, _ = cv2.getTextSize(label, font, font_scale, thickness)
        text_w, text_h = text_size

        # 标签位置：默认放在框的左上角上方
        text_x = x1
        text_y = y1 - 6

        # 如果文字会超出图片顶部，就放到框内部
        if text_y - text_h - 4 < 0:
            text_y = y1 + text_h + 6

        # 画蓝色文字背景
        cv2.rectangle(
            image,
            (text_x, text_y - text_h - 4),
            (text_x + text_w + 6, text_y + 3),
            box_color,
            -1
        )

        # 写置信度
        cv2.putText(
            image,
            label,
            (text_x + 3, text_y - 2),
            font,
            font_scale,
            text_color,
            thickness,
            cv2.LINE_AA
        )

    cv2.imwrite(save_path, image)

# 首页接口: 打开网页 
@app.route("/") # app.route("/") 表示网页根路径
# render_template("index.html") 自动取这个文件夹里面找: templates/index.html
def index():
    return render_template("index.html")


# 检测接口/predict 定义了/predict的接口， 他只接受post请求
# 为什么是post: 前端要上传图片，图片属于比较大的数据，用post
@app.route("/predict", methods=["POST"])
def predict():
    #检查有没有上传图片
    #request.file 是 Flask 用来接受上传文件的地方
    # 为什么是"image" 呢?  前端formDATA("image") 前端传的是image,后端也用image接
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    #取出上传的图片 从前端上传的数据里取出那张图片
    file = request.files["image"]

    #防止用户没有选择文件/文件名为空
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # 保存上传图片
    #ext这一步: 取后缀名
    ext = os.path.splitext(file.filename)[1]
    #生成一个文件名 (用uuid可以避免重名)
    image_name = f"{uuid.uuid4().hex}{ext}"
    #拼接成完整的保存路径
    image_path = os.path.join(UPLOAD_FOLDER, image_name)
    #
    file.save(image_path)

    # 读取置信度阈值，默认 0.5 (如果前端传了conf,用前端的 没传，默认0.5)
    conf = float(request.form.get("conf", 0.5))

    # YOLO 推理
    results = model.predict(
        source=image_path,
        conf=conf,
        save=False
    )

    #model.predict() --- 返回列表
    result = results[0] #单张图片的检测结果 

    #生成结果图路经
    result_name = f"result_{image_name}"
    result_path = os.path.join(RESULT_FOLDER, result_name)

    # 自定义画框：只显示置信度，不显示 street light
    draw_boxes_conf_only(image_path, result, result_path)

    # 提取检测信息
    detections = []
    for box in result.boxes:
        cls_id = int(box.cls[0])
        class_name = model.names[cls_id]
        confidence = float(box.conf[0])

        detections.append({
            "class_name": class_name,
            "confidence": round(confidence, 3)
        })

    return jsonify({
        "original_image": "/" + image_path,
        "result_image": "/" + result_path,
        "count": len(detections),
        "detections": detections
    })

@app.route("/predict_video", methods=["POST"])
def predict_video():
    #检查这个"video"字段是否在前端传过来的formData里面
    if "video" not in request.files:
        return jsonify({"error": "no video file upload"}),400
    #前端传递的字段是"video" 后端用request files接收视频
    video = request.files["video"]
    # 看一下视频的文件名是否为空字符串 为空字符串 不保存 返回前端叫用户命名:
    # 空字符串: "" 空格: " "
    if video.filename == "":
        return jsonify({"error": "no selected files"}),400
    
    #后端建立保存视频的文件夹 os.makedirs建立保存视频的文件夹
    #路径也要加引号 也是字符串
    upload_dir = "static/uploads/videos"
    os.makedirs(upload_dir,exist_ok=True)
    
    #视频的实际路径 = 视频文件夹 + 图片的名字 成功保存视频
    video_path= os.path.join(upload_dir,video.filename)
    video.save(video_path)

    #读取视频文件的大小: os.path.getsize(返回单位是 bytes)
    video_size_bytes = os.path.getsize(video_path) #返回的只是bytes
    #1KB = 1024bytes,  1MB = 1024KB  1MB = 1024*1024 bytes 
    video_size_mb = video_size_bytes / (1024 * 1024)
    #判断
    if video_size_mb > MAX_VIDEO_SIZE_MB:
        os.remove(video_path)
        return jsonify({
            "error": (
                f"The uploaded video is {video_size_mb:.1f}MB. " 
                f"Please upload a video smaller than {MAX_VIDEO_SIZE_MB}MB."
            )
        }),400

    #创建抽帧保存文件夹 可以给YOLO模型读取
    frame_dir = "static/frames"
    os.makedirs(frame_dir,exist_ok=True)

    #打开视频 (用Opencv的capture函数)
    capture = cv2.VideoCapture(video_path)

    # 安全措施: 判断视频是否能打开
    if not capture.isOpened():
        return jsonify({"error": "can't open this video"}),400

    #获得原始视频的特性: 比如30FPS表示 每1s 30帧 因为cv2只认帧数 不会认秒数 为了把秒数转换成帧数
    original_frame_per_second = capture.get(cv2.CAP_PROP_FPS) 
    total_frames = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    
    # 防止 FPS 读取失败
    if original_frame_per_second <= 0:
        original_frame_per_second = 30

    #计算原始视频时长: 原始视频时长=视频总帧数(frame) / 视频FPS(frame_per_second)
    duration_sec = total_frames / original_frame_per_second

    #错误信息提示 --- 针对时长大的视频
    warning_message = None
    #如果原始视频时长大于10s 只截取前10s 并返回warning
    if duration_sec > MAX_DURATION_SEC:
        max_frames = int(original_frame_per_second * MAX_DURATION_SEC)
        warning_message = (
            f"The uploaded video is {duration_sec:.1f}s long. "
            f"To reduce server inference cost, only the first {MAX_DURATION_SEC}s are processed."
        )
    else:
        max_frames = int(total_frames)
    
    #这个人为更改 每几秒抽帧一帧 换成帧--- 每60帧里面抽一帧  
    FRAME_SAMPLE_INTERVAL_SEC = 1 # 每一秒抽一帧

    #这个是计算每多少帧里面抽一帧 --- 把秒---帧
    frame_interval = max(1, int(original_frame_per_second * FRAME_SAMPLE_INTERVAL_SEC))

    #然后循环从视频里抽取帧 (cv2只能一帧一帧按顺序抽取)
    frame_id = 0  #便于标记原始视频对应的帧
    save_id = 0 # 标记我们要存储的帧的编号
    saved_list = [] #便于存储我们需要的图片/帧的路径

    #无限循环 这个次数不好判断 用while
    #循环作用: 逐帧读取视频
    while frame_id < max_frames:
        # 这句的话 就是从视频里一帧一帧的读 返回是否读到帧(ret变量) 以及当前对应的frame
       ret, frame = capture.read()
       #当ret不是1 即ret 不是true的时候 说明循环停止
       if not ret:
          break

       #表示每个frame_interval取一帧
       if frame_id % frame_interval ==0:
          #save_id 直接对应当前帧的id
          save_id = frame_id
          #frame的路径是static/frame/frame_0001.jpg (我是想写这个)
          #:04d 这里的: 表示的是至少占4位 不足补0
          #f"{1:.4d}" --- 不规范 只是碰巧能跑 这种写法的.4d 只是保留小数点后4位 适合浮点数用 整数不支持这个写法
          frame_path = os.path.join(frame_dir,f"frame_{save_id:04d}.jpg")
          #保存图片到frame_path路径下
          #注意: 这个frame是opencv读出来的图像数组，不是flask上传上来的文件对象
          #所以不能用.save()
          #cv2.imwrite(frame_path,frame) --- 保存openCV读取出来的一帧图片
          cv2.imwrite(frame_path,frame)
          #保存这个路径到static/frame文件夹里
          saved_list.append(frame_path)

       frame_id += 1
    
    #用完释放资源
    capture.release()

    # 读取前端传来的置信度阈值，默认 0.5 (如果前端传了conf,用前端的 没传，默认0.5)
    conf = float(request.form.get("conf", 0.5))

    #新建保存模型画框后的图片的文件夹
    result_dir = "static/results/video_frames"
    os.makedirs(result_dir,exist_ok=True)

    # 提取所有抽帧图片的检测信息 以及检测框的数量
    all_results = []
    total_count = 0

    # YOLO 推理 然后把每一张在saved_list里面保存的图片喂给YOLO 让YOLO跑预测
    for frame_path in saved_list:
        # yolo 推理
        results = model.predict(source=frame_path,conf=conf,save=False)
        #提取结果图
        result = results[0]
        #生成result_name, 后面生成result_path时要用
        #os.path.basename表示的时提取frame_path最后一部分文件名
        result_name = os.path.basename(frame_path)
        result_path = os.path.join(result_dir,result_name)

        #自定义画框: 只显示置信度 不显示字段street light
        draw_boxes_conf_only(frame_path, result, result_path)

        # 提取每张抽帧图片的检测信息
        detections = []
        #提取检测信息 一张图片可能有很多个预测框 都要提取出来
        for box in result.boxes:
            cls_id = int(box.cls[0])
            class_name = model.names[cls_id]
            confidence = float(box.conf[0])
            detections.append({
                "class_name": class_name,
                "confidence": round(confidence, 3)
            })
        
        box_count = len(detections)
        total_count += box_count

        all_results.append({
            "frame_path": "/" + frame_path,
            "result_path": "/" + result_path,
            "count": box_count,
            "detections": detections
        })

    #返回所有帧的结果
    return jsonify({
        "message": "video processed successfully",
        "warning": warning_message,
        "video_path": "/" + video_path,
        "video_size_mb": round(video_size_mb,2),
        "video_duration_sec": round(duration_sec,2),
        "processed_duration_sec": min(round(duration_sec, 2), MAX_DURATION_SEC),
        "fps": original_frame_per_second,
        "frame_interval": frame_interval,
        "frame_count": len(saved_list),
        #预测框的数量
        "count": total_count,
        "results": all_results
    })

#启动flask服务 debug=true --- 调试模式 debug=false (开发模式)
if __name__ == "__main__":
    app.run(debug=True)