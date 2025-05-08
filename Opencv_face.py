import cv2
import sqlite3
import numpy as np
import pickle
import io
import base64
from flask import Flask, request, jsonify, send_from_directory
from PIL import Image
import cv2.face
import logging

app = Flask(__name__)

# 設定日誌
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 資料庫檔案路徑
DATABASE_FILE = r'C:\Users\690\Dev\02_TEST\OpenCV_20250508\member_database.db'

# 初始化臉部偵測器和辨識器
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
recognizer = cv2.face_LBPHFaceRecognizer.create()

def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            membership_level TEXT,
            face_encoding BLOB
        )
    ''')
    conn.commit()
    conn.close()

def insert_member(member_id, name, face_encoding):
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO members (member_id, name, face_encoding) VALUES (?, ?, ?)",
                        (member_id, name, sqlite3.Binary(face_encoding)))
        conn.commit()
        return cursor.lastrowid   # 返回新插入的 id
    except sqlite3.Error as e:
        logger.error(f"資料庫操作錯誤: {e}")
        if "UNIQUE constraint failed" in str(e):
            return jsonify({'status': 'error', 'message': f'會員已註冊：會員編號 {member_id} 已存在'})
        return jsonify({'status': 'error', 'message': f'資料庫儲存失敗: {str(e)}'})
    finally:
        if conn:
            conn.close()

def get_member_by_id(db_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT member_id, name FROM members WHERE id = ?", (db_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def load_all_members():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, face_encoding FROM members")
    members = cursor.fetchall()
    conn.close()
    return members

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    member_id = data['member_id']
    name = data['name']
    image_data = data['image'].split(',')[1]   # 移除 "data:image/jpeg;base64," 前綴

    # 解碼圖片
    try:
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))
        frame = np.array(image)
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        # 偵測臉部
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
    except Exception as e:
        logger.error(f"圖片處理錯誤: {e}")
        return jsonify({'status': 'error', 'message': '圖片處理失敗'})

    if len(faces) == 0:
        return jsonify({'status': 'error', 'message': '未偵測到臉部'})

    face_samples = []
    for (x, y, w, h) in faces:
        face_roi = gray[y:y + h, x:x + w]
        face_samples.append(face_roi)

    if face_samples:
        new_id = insert_member(member_id, name, pickle.dumps(face_samples))
        if isinstance(new_id, dict):   # 如果是錯誤訊息
            return new_id
        logger.info(f"註冊成功，新會員 ID: {new_id}")

        # 重新訓練模型
        members = load_all_members()
        if members:
            ids = np.array([m[0] for m in members])
            face_encodings = [pickle.loads(m[1]) for m in members]
            recognizer.train(face_encodings, ids)
            recognizer.save('recognizer.yml')
            logger.info("模型已重新訓練")
        return jsonify({'status': 'success', 'message': f'會員 {name} ({member_id}) 註冊成功'})
    return jsonify({'status': 'error', 'message': '註冊失敗'})

@app.route('/recognize', methods=['POST'])
def recognize():
    data = request.json
    image_data = data['image'].split(',')[1]

    try:
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))
        frame = np.array(image)
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
    except Exception as e:
        logger.error(f"圖片處理錯誤: {e}")
        return jsonify({'status': 'error', 'message': '圖片處理失敗'})

    if len(faces) == 0:
        return jsonify({'status': 'error', 'message': '未偵測到臉部'})

    try:
        recognizer.read('recognizer.yml')
    except cv2.error:
        logger.error("辨識模型尚未訓練")
        return jsonify({'status': 'error', 'message': '辨識模型尚未訓練，請先註冊會員'})

    for (x, y, w, h) in faces:
        face_roi = gray[y:y + h, x:x + w]
        id_, conf = recognizer.predict(face_roi)
        logger.debug(f"辨識結果 - ID: {id_}, 信心值: {conf}")
        if conf < 80:   # 放寬信心閾值
            member = get_member_by_id(id_)
            if member:
                return jsonify({'status': 'success', 'name': member[1], 'member_id': member[0], 'confidence': conf})
        return jsonify({'status': 'error', 'message': '無法辨識'})

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/.well-known/appspecific/com.chrome.devtools.json')
def chrome_devtools():
    return jsonify({}), 200   # 返回空的 JSON，消除 404 錯誤

if __name__ == "__main__":
    init_db()
    app.run(debug=True)