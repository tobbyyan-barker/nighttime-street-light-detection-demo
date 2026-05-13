const imageInput = document.getElementById("imageInput");
const detectBtn = document.getElementById("detectBtn");
const originalPreview = document.getElementById("originalPreview");
const resultPreview = document.getElementById("resultPreview");
const statusText = document.getElementById("statusText");
const countText = document.getElementById("countText");
const resultList = document.getElementById("resultList");
const confInput = document.getElementById("confInput");
const confValue = document.getElementById("confValue");

let selectedFile = null;

//置信度滑动条拖动逻辑: 置信度条被拖动--- 触发input 然后这里读取confInput.vale的值 并保留两位小数 最后html更新这个值
confInput.addEventListener("input", () => {
  confValue.textContent = Number(confInput.value).toFixed(2);
});

//图片上传和预览 这一整块负责：用户选择图片后, 显示原图预览，并重置旧结果
//4.1: 监听用户选择图片: 当用户选择图片后，触发change事件，执行里面的代码
imageInput.addEventListener("change", () => {
  // 取出第一张上传的图片 这里只上传一张 只取第一张
  selectedFile = imageInput.files[0];
  // selectFile 表示当前用户上传的图片 后面点击检测按钮时，会用这个selectFile 上传给flask
  if (!selectedFile) {
    return;
  }

  // 生成原图预览地址： 给本地图片临时生成一个浏览器可以显示的URL
  const imageURL = URL.createObjectURL(selectedFile);
  
  originalPreview.src = imageURL;
  // 把上传图片显示出来
  originalPreview.style.display = "block";

  // 清空上一轮检测结果图
  resultPreview.src = "";
  resultPreview.style.display = "none";

  // 重置检测数量和列表
  countText.textContent = "0";  // 改文字
  resultList.innerHTML = "";    

  // 更新状态提示
  statusText.textContent = "Image selected. Ready to detect.";
});

detectBtn.addEventListener("click", async () => {
  if (!selectedFile) {
    alert("Please choose an image first.");
    return;
  }

  const formData = new FormData();
  formData.append("image", selectedFile);
  formData.append("conf", confInput.value);

  //更新状态为检测中
  statusText.textContent = "Detecting... Please wait.";

  // try...catch 处理正常检测和错误(异常检测)
  // try 里面放入任何可能出错的代码 中间有一步出错 就进入catch  显示错误信息
  try {
    // fetch 调用flask后端
    const response = await fetch("/predict", {
      method: "POST",
      body: formData
    });

    //接收flask 返回的json数据
    const data = await response.json();
    // 这几行是调试用的
    console.log(data);
    console.log(data.count)
    console.log(data.message)

    // 检测后端是否相应成功
    if (!response.ok) {
      throw new Error(data.error || "Detection failed.");
    }

    // 显示检测结果图
    resultPreview.src = data.result_image + "?t=" + new Date().getTime();
    resultPreview.style.display = "block";

    // 更新检测数量
    countText.textContent = data.count;

    // 清空旧的结果列表 每次新检测前，先把旧结果列表清空
    resultList.innerHTML = "";

    if (data.detections.length === 0) {
      resultList.innerHTML = "<li>No object detected.</li>";
    } else {
      data.detections.forEach((item, index) => {
        const li = document.createElement("li");
        li.textContent = `${index + 1}. ${item.class_name} - confidence: ${item.confidence}`;
        resultList.appendChild(li);
      });
    }

    statusText.textContent = "Detection completed.";
  } catch (error) {
    statusText.textContent = "Error: " + error.message;
  }
});