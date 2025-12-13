from flask import Flask, render_template, request, jsonify
import os
import cv2
from ultralytics import YOLO
import shutil
import time

# ==========================================
# KONFIGURASI
# ==========================================
app = Flask(__name__, template_folder="web_skripsi", static_folder="static")

UPLOAD_FOLDER = os.path.join("static", "uploads")
RESULT_FOLDER = os.path.join("static", "results")
MODEL_PATH = "runs/detect/mango_finetune_phaseC_final/weights/best.pt"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Ambang batas confidence minimal
CONF_THRESHOLD = 0.68

# ==========================================
# PENGETAHUAN PENYAKIT INDEX
# ==========================================
disease_info = {
    "Anthracnose": {
        "cause": "Infeksi jamur Colletotrichum gloeosporioides.",
        "treatment": "Pangkas daun terinfeksi & semprot fungisida berbahan tembaga."
    },
    "Bacterial Canker": {
        "cause": "Infeksi bakteri Xanthomonas campestris.",
        "treatment": "Gunakan bakterisida & tingkatkan sanitasi kebun."
    },
    "Cutting Weevil": {
        "cause": "Serangan kumbang penggerek daun.",
        "treatment": "Gunakan insektisida kontak & pemangkasan daun rusak."
    },
    "Die Back": {
        "cause": "Infeksi jamur Botryodiplodia theobromae.",
        "treatment": "Pangkas cabang mati & gunakan fungisida sistemik."
    },
    "Gall Midge": {
        "cause": "Larva lalat kecil menyerang jaringan daun.",
        "treatment": "Gunakan insektisida sistemik & sanitasi daun gugur."
    },
    "Healthy": {
        "cause": "Daun sehat tanpa tanda penyakit.",
        "treatment": "Tidak diperlukan perawatan khusus."
    },
    "Powdery Mildew": {
        "cause": "Jamur Oidium mangiferae.",
        "treatment": "Semprot fungisida sulfur atau kalium karbonat."
    },
    "Sooty Mould": {
        "cause": "Pertumbuhan jamur jelaga akibat serangan hama penghasil honeydew.",
        "treatment": "Basmi hama penyebab & bersihkan permukaan daun."
    }
}

# ==========================================
# LOAD YOLO SEKALI SAJA
# ==========================================
model = YOLO(MODEL_PATH)
print("✅ Model YOLO berhasil dimuat.")

# ==========================================
# ROUTE HALAMAN UTAMA
# ==========================================
@app.route('/')
def index():
    return render_template('index.html')

# ==========================================
# ROUTE DETEKSI GAMBAR
# ==========================================
@app.route('/detect', methods=['POST'])
def detect():

    if 'image' not in request.files:
        return jsonify({"error": "Tidak ada file yang dikirim."})

    file = request.files['image']

    filename = f"img_{int(time.time())}.jpg"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Bersihkan hasil sebelumnya
    if os.path.exists(RESULT_FOLDER):
        shutil.rmtree(RESULT_FOLDER)
    os.makedirs(RESULT_FOLDER, exist_ok=True)

    # Jalankan YOLO
    results = model.predict(source=file_path, conf=0.01, save=False)  
    result = results[0]

    annotated = result.plot()
    output_path = os.path.join(RESULT_FOLDER, filename)
    cv2.imwrite(output_path, annotated)

    predictions = []

    for box in result.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])

        # FILTER BERDASARKAN CONFIDENCE
        if conf < CONF_THRESHOLD:
            continue

        class_name = model.names[cls_id]

        predictions.append({
            "name": class_name,
            "confidence": conf,
            "cause": disease_info.get(class_name, {}).get("cause", "-"),
            "treatment": disease_info.get(class_name, {}).get("treatment", "-")
        })

    # Jika tidak ada prediksi yang valid → kirim pesan error
    if len(predictions) == 0:
        return jsonify({
            "error": "Harap input gambar daun mangga dan pastikan objek jelas."
        })

    return jsonify({
        "image_url": f"/static/results/{filename}",
        "predictions": predictions
    })

# ==========================================
# RUN FLASK
# ==========================================
if __name__ == '__main__':
    app.run(debug=True)
