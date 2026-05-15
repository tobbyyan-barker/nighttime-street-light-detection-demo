const imageInput = document.getElementById("imageInput");
const videoInput = document.getElementById("videoInput");

const detectBtn = document.getElementById("detectBtn");
const detectVideoBtn = document.getElementById("detectVideoBtn");

const originalPreview = document.getElementById("originalPreview");
const resultPreview = document.getElementById("resultPreview");

const statusText = document.getElementById("statusText");
const countText = document.getElementById("countText");
const resultList = document.getElementById("resultList");

const confInput = document.getElementById("confInput");
const confValue = document.getElementById("confValue");

const frameCountText = document.getElementById("frameCountText");
const videoCountText = document.getElementById("videoCountText");
const videoGallery = document.getElementById("videoGallery");

let selectedFile = null;
let selectedVideoFile = null;

// 置信度滑动条拖动逻辑
confInput.addEventListener("input", () => {
  confValue.textContent = Number(confInput.value).toFixed(2);
});

// 图片上传和预览
imageInput.addEventListener("change", () => {
  selectedFile = imageInput.files[0];

  if (!selectedFile) {
    return;
  }

  const imageURL = URL.createObjectURL(selectedFile);

  originalPreview.src = imageURL;
  originalPreview.style.display = "block";

  resultPreview.src = "";
  resultPreview.style.display = "none";

  countText.textContent = "0";
  resultList.innerHTML = "";

  statusText.textContent = "Image selected. Ready to detect.";
});

// 视频上传逻辑
videoInput.addEventListener("change", () => {
  selectedVideoFile = videoInput.files[0];

  if (!selectedVideoFile) {
    return;
  }

  frameCountText.textContent = "0";
  videoCountText.textContent = "0";
  videoGallery.innerHTML = "";

  statusText.textContent = "Video selected. Ready to detect.";
});

// 图片检测按钮
detectBtn.addEventListener("click", async () => {
  if (!selectedFile) {
    alert("Please choose an image first.");
    return;
  }

  const formData = new FormData();
  formData.append("image", selectedFile);
  formData.append("conf", confInput.value);

  statusText.textContent = "Detecting image... Please wait.";

  try {
    const response = await fetch("/predict", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    console.log(data);

    if (!response.ok) {
      throw new Error(data.error || "Image detection failed.");
    }

    resultPreview.src = data.result_image + "?t=" + new Date().getTime();
    resultPreview.style.display = "block";

    countText.textContent = data.count;

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

    statusText.textContent = "Image detection completed.";
  } catch (error) {
    statusText.textContent = "Error: " + error.message;
  }
});

// 视频检测按钮
detectVideoBtn.addEventListener("click", async () => {
  if (!selectedVideoFile) {
    alert("Please choose a video first.");
    return;
  }

  const formData = new FormData();
  formData.append("video", selectedVideoFile);
  formData.append("conf", confInput.value);

  statusText.textContent = "Detecting video... This may take a while.";

  frameCountText.textContent = "0";
  videoCountText.textContent = "0";
  videoGallery.innerHTML = "";

  try {
    const response = await fetch("/predict_video", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    console.log(data);

    if (!response.ok) {
      throw new Error(data.error || "Video detection failed.");
    }

    frameCountText.textContent = data.frame_count;
    videoCountText.textContent = data.count;

    if (!data.results || data.results.length === 0) {
      videoGallery.innerHTML = "<p>No frames were extracted from this video.</p>";
      statusText.textContent = "Video detection completed, but no frame was extracted.";
      return;
    }

    data.results.forEach((item, index) => {
      const card = document.createElement("div");
      card.className = "video-frame-card";

      const img = document.createElement("img");
      img.src = item.result_path + "?t=" + new Date().getTime();
      img.alt = `Video detection result frame ${index + 1}`;

      const title = document.createElement("p");
      title.innerHTML = `<strong>Frame ${index + 1}</strong>`;

      const count = document.createElement("p");
      count.textContent = `Detected objects: ${item.count}`;

      const details = document.createElement("p");

      if (!item.detections || item.detections.length === 0) {
        details.textContent = "No object detected.";
      } else {
        const detectionText = item.detections
          .map((det, detIndex) => {
            return `${detIndex + 1}. ${det.class_name} (${det.confidence})`;
          })
          .join(" | ");

        details.textContent = detectionText;
      }

      card.appendChild(img);
      card.appendChild(title);
      card.appendChild(count);
      card.appendChild(details);

      videoGallery.appendChild(card);
    });

    statusText.textContent = "Video detection completed.";
  } catch (error) {
    statusText.textContent = "Error: " + error.message;
  }
});

