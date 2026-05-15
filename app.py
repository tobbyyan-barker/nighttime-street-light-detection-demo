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

# 加载 YOLO 模型
model = YOLO("best.pt")

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

    # 生成画框后的图片
    plotted_img = result.plot()

    #生成结果图路经
    result_name = f"result_{image_name}"
    result_path = os.path.join(RESULT_FOLDER, result_name)

    # 保存结果图 (图片数组---图片文件)
    cv2.imwrite(result_path, plotted_img)

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

    #创建抽帧保存文件夹 可以给YOLO模型读取
    frame_dir = "static/frames"
    os.makedirs(frame_dir,exist_ok=True)

    #打开视频 (用Opencv的capture函数)
    capture = cv2.VideoCapture(video_path)

    # 安全措施: 判断视频是否能打开
    if not capture.isOpened():
        return jsonify({"error": "can't open this video"}),400

    #获得原始视频的特性: 比如30FPS表示 每1s 30帧 因为cv2只认帧数 不会认秒数 为了把秒数转换成帧数
    original_frame = capture.get(cv2.CAP_PROP_FPS) 

    # 防止 FPS 读取失败
    if original_frame <= 0:
        original_frame = 30

    #这个人为更改 每几秒抽帧一帧 换成帧--- 每60帧里面抽一帧  
    fps_interval = 1 # 每一秒抽一帧

    #这个是计算每多少帧里面抽一帧 --- 把秒---帧
    frame_interval = max(1, int(original_frame * fps_interval))

    #然后循环从视频里抽取帧 (cv2只能一帧一帧按顺序抽取)
    frame_id = 0  #便于标记原始视频对应的帧
    save_id = 0 # 标记我们要存储的帧的编号
    saved_list = [] #便于存储我们需要的图片/帧的路径

    #无限循环 这个次数不好判断 用while
    #循环作用: 逐帧读取视频
    while True:
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
        # 生成画框后的图片 result.plot() 会返回画框后的图片
        plotted_img = result.plot()
        #生成result_name, 后面生成result_path时要用
        #os.path.basename表示的时提取frame_path最后一部分文件名
        result_name = os.path.basename(frame_path)
        result_path = os.path.join(result_dir,result_name)

        # 保存检测后的图片
        cv2.imwrite(result_path,plotted_img)

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
        "video_path": "/" + video_path,
        "fps": original_frame,
        "frame_interval": frame_interval,
        "frame_count": len(saved_list),
        #预测框的数量
        "count": total_count,
        "results": all_results
    })

#启动flask服务 debug=true --- 调试模式 debug=false (开发模式)
if __name__ == "__main__":
    app.run(debug=True)