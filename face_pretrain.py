import face_recognition
import os
import numpy as np
import yaml

def train_face_recognition(dataset_path):
    known_face_encodings = []
    known_face_names = []

    for name in os.listdir(dataset_path):
        person_path = os.path.join(dataset_path, name)
        if os.path.isdir(person_path):
            for filename in os.listdir(person_path):
                if filename.endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(person_path, filename)
                    try:
                        image = face_recognition.load_image_file(image_path)
                        face_locations = face_recognition.face_locations(image)
                        if len(face_locations) > 0:
                            face_encoding = face_recognition.face_encodings(image, face_locations)[0]
                            known_face_encodings.append(face_encoding.tolist()) # Convert to list for YAML serialization
                            known_face_names.append(name)
                        else:
                            print(f"警告：在 {image_path} 中找不到人臉。")
                    except Exception as e:
                        print(f"讀取 {image_path} 時發生錯誤：{e}")

    return {"encodings": known_face_encodings, "names": known_face_names}

def save_to_yaml(data, output_path):
    with open(output_path, 'w') as outfile:
        yaml.dump(data, outfile)
    print(f"模型資料已儲存到 {output_path}")

if __name__ == "__main__":
    dataset_path = 'faces_dataset' # 將此路徑替換為您的資料集路徑
    output_yaml_path = 'trained_faces.yaml'

    trained_data = train_face_recognition(dataset_path)
    save_to_yaml(trained_data, output_yaml_path)