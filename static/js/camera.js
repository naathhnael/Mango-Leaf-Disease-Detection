const video = document.getElementById('video');
const captureBtn = document.getElementById('captureBtn');
const canvas = document.getElementById('canvas');
const cameraForm = document.getElementById('cameraForm');
const cameraInput = document.getElementById('cameraInput');

// Aktifkan kamera
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => video.srcObject = stream)
  .catch(err => alert("Tidak bisa mengakses kamera: " + err));

// Tangkap gambar dan kirim ke Flask
captureBtn.addEventListener('click', () => {
  const context = canvas.getContext('2d');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  context.drawImage(video, 0, 0);

  canvas.toBlob(blob => {
    const file = new File([blob], "capture.jpg", { type: "image/jpeg" });
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    cameraInput.files = dataTransfer.files;
    cameraForm.submit();
  }, "image/jpeg");
});
