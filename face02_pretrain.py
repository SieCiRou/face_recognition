    """
    Pretrain a face recognition model.
    ----------------------------------------
    pip install opencv_contrib_python
    pip install opencv-python
    pip install deepface
    """
 import cv2
import numpy as np
from deepface import DeepFace

# 初始化人臉檢測器 (Haar Cascade 或 DNN)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def capture_and_recognize():
    cap = cv2.VideoCapture(0)
    print("開始辨識，按 'q' 退出")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces_detected = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        for (x, y, w, h) in faces_detected:
            face = frame[y:y+h, x:x+w]
            
            try:
                # 使用 DeepFace 進行辨識
                result = DeepFace.find(face, db_path="face_database", model_name="Facenet")
                
                if len(result) > 0:
                    name = result[0]["identity"]
                else:
                    name = "Unknown"

                # 顯示結果
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                
            except:
                pass

        cv2.imshow("Face Recognition", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_and_recognize()
