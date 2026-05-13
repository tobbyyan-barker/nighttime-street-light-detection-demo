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

#启动flask服务 debug=true --- 调试模式 debug=false (开发模式)
if __name__ == "__main__":
    app.run(debug=True)