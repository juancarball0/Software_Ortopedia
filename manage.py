import cv2
import numpy as np
import firebase_admin
from firebase_admin import credentials, storage
import os
import time  # Para generar timestamps únicos

# Inicializa Firebase
cred = credentials.Certificate('credenciales.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ortopedia-d21f4-default-rtdb.firebaseio.com/',
    'storageBucket': 'ortopedia-d21f4.appspot.com'
})

def upload_image_to_firebase(image_path, folder_name):
    bucket = storage.bucket()
    blob = bucket.blob(f"{folder_name}/{os.path.basename(image_path)}")
    blob.upload_from_filename(image_path)
    print(f"Imagen {image_path} subida exitosamente a Firebase Storage en la carpeta {folder_name}.")

def process_image(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
    binary_frame = cv2.adaptiveThreshold(blurred_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    contours, _ = cv2.findContours(binary_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_frame = frame.copy()
    cv2.drawContours(contour_frame, contours, -1, (0, 255, 0), 2)
    pressure_map = detect_pressure_areas(gray_frame)
    return contour_frame, binary_frame, contours, pressure_map

def detect_pressure_areas(gray_frame):
    normalized_frame = cv2.normalize(gray_frame, None, 0, 255, cv2.NORM_MINMAX)
    heatmap = cv2.applyColorMap(normalized_frame, cv2.COLORMAP_JET)
    return heatmap

def measure_foot_dimensions(contours):
    if len(contours) > 0:
        contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        x, y, w, h = cv2.boundingRect(contour)
        return w, h, area, perimeter
    return None

def start_cameras_and_analyze():
    cap1 = cv2.VideoCapture(0)
    cap2 = cv2.VideoCapture(1)

    if not cap1.isOpened() or not cap2.isOpened():
        print("Error al abrir las cámaras.")
        return

    while True:
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()

        if not ret1 or not ret2:
            print("Error al capturar imágenes de las cámaras.")
            break

        # Procesar las imágenes de ambas cámaras
        contour_frame1, binary_frame1, contours1, pressure_map1 = process_image(frame1)
        contour_frame2, binary_frame2, contours2, pressure_map2 = process_image(frame2)

        dimensions1 = measure_foot_dimensions(contours1)
        dimensions2 = measure_foot_dimensions(contours2)

        if dimensions1:
            width1, height1, area1, perimeter1 = dimensions1
            cv2.putText(contour_frame1, f"Ancho: {width1}px", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            cv2.putText(contour_frame1, f"Alto: {height1}px", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            cv2.putText(contour_frame1, f"Area: {area1}px^2", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        if dimensions2:
            width2, height2, area2, perimeter2 = dimensions2
            cv2.putText(contour_frame2, f"Ancho: {width2}px", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            cv2.putText(contour_frame2, f"Alto: {height2}px", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            cv2.putText(contour_frame2, f"Area: {area2}px^2", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        # Mostrar las imágenes procesadas de ambas cámaras
        cv2.imshow("Imagen Original - Camara 1", frame1)
        cv2.imshow("Contornos - Camara 1", contour_frame1)
        cv2.imshow("Mapa de Presión - Camara 1", pressure_map1)

        cv2.imshow("Imagen Original - Camara 2", frame2)
        cv2.imshow("Contornos - Camara 2", contour_frame2)
        cv2.imshow("Mapa de Presión - Camara 2", pressure_map2)

        key = cv2.waitKey(1) & 0xFF

        # Generar nueva carpeta cada vez que se presiona 'c'
        if key == ord('c'):
            # Crear un folder único basado en el timestamp cada vez que se guarda
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            folder_name = f"paciente_{timestamp}"

            if not os.path.exists('captures'):
                os.makedirs('captures')

            cam1_original_path = f'./captures/foot_cam1_original_{timestamp}.png'
            cam1_contour_path = f'./captures/foot_cam1_contours_{timestamp}.png'
            cam1_pressure_path = f'./captures/foot_cam1_pressure_{timestamp}.png'

            cam2_original_path = f'./captures/foot_cam2_original_{timestamp}.png'
            cam2_contour_path = f'./captures/foot_cam2_contours_{timestamp}.png'
            cam2_pressure_path = f'./captures/foot_cam2_pressure_{timestamp}.png'

            # Guardar imágenes de ambas cámaras
            cv2.imwrite(cam1_original_path, frame1)
            cv2.imwrite(cam1_contour_path, contour_frame1)
            cv2.imwrite(cam1_pressure_path, pressure_map1)

            cv2.imwrite(cam2_original_path, frame2)
            cv2.imwrite(cam2_contour_path, contour_frame2)
            cv2.imwrite(cam2_pressure_path, pressure_map2)

            print("Imágenes capturadas de ambas cámaras y guardadas localmente.")

            # Subir imágenes a Firebase, dentro del folder del paciente
            upload_image_to_firebase(cam1_original_path, folder_name)
            upload_image_to_firebase(cam1_contour_path, folder_name)
            upload_image_to_firebase(cam1_pressure_path, folder_name)

            upload_image_to_firebase(cam2_original_path, folder_name)
            upload_image_to_firebase(cam2_contour_path, folder_name)
            upload_image_to_firebase(cam2_pressure_path, folder_name)

        # Salir al presionar 'q'
        if key == ord('q'):
            break

    # Liberar las cámaras y cerrar las ventanas
    cap1.release()
    cap2.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_cameras_and_analyze()
