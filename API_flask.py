from flask import Flask, request, jsonify, send_file
import cv2
import numpy as np
import sqlite3
import pandas as pd
from deepface import DeepFace
from datetime import datetime

app = Flask(__name__)

# 初始化 SQLite 資料庫
conn = sqlite3.connect("employees.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, name TEXT, photo TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY, employee_id INTEGER, time TEXT)")
conn.commit()

@app.route("/register", methods=["POST"])
def register_employee():
    data = request.json
    name = data["name"]
    image_path = f"face_database/{name}.jpg"

    with open(image_path, "wb") as f:
        f.write(np.array(data["image"]).tobytes())

    cursor.execute("INSERT INTO employees (name, photo) VALUES (?, ?)", (name, image_path))
    conn.commit()
    
    return jsonify({"message": "註冊成功"})

@app.route("/recognize", methods=["POST"])
def recognize():
    image = request.json["image"]
    result = DeepFace.find(img_path=image, db_path="face_database", model_name="Facenet")

    if len(result) > 0:
        employee_name = result[0]["identity"]
        employee_id = cursor.execute("SELECT id FROM employees WHERE name=?", (employee_name,)).fetchone()[0]

        # 記錄打卡時間
        cursor.execute("INSERT INTO attendance (employee_id, time) VALUES (?, ?)", (employee_id, datetime.now()))
        conn.commit()
    else:
        employee_name = "未知"

    return jsonify({"name": employee_name})

@app.route("/export", methods=["GET"])
def export_excel():
    start_date = request.args.get("start")
    end_date = request.args.get("end")

    df = pd.read_sql_query(f"SELECT employees.id, employees.name, attendance.time FROM employees JOIN attendance ON employees.id = attendance.employee_id WHERE time BETWEEN '{start_date}' AND '{end_date}'", conn)

    excel_path = "attendance_report.xlsx"
    df.to_excel(excel_path, index=False)
    return send_file(excel_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
