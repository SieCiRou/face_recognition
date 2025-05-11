document.getElementById("captureButton").addEventListener("click", async () => {
    const video = document.getElementById("video");
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL("image/jpeg");  // 轉換為 Base64
    const response = await fetch("/recognize", {
        method: "POST",
        body: JSON.stringify({ image: imageData }),
        headers: { "Content-Type": "application/json" }
    });

    const data = await response.json();
    document.getElementById("name").innerText = data.name;
});

document.getElementById("exportButton").addEventListener("click", () => {
    const start = document.getElementById("startDate").value;
    const end = document.getElementById("endDate").value;

    window.location.href = `/export?start=${start}&end=${end}`;
});
