import tkinter as tk
from tkinter import Label, Button
from backend import start_cameras_and_analyze, upload_image_to_firebase
import threading
from PIL import Image, ImageTk
import os
import time
import cv2

# Variables globales
current_frame1 = None
current_frame2 = None

def update_camera_labels(frame1, frame2, camera_labels):
    global current_frame1, current_frame2
    # Convertir las imágenes de OpenCV a un formato que Tkinter pueda usar
    current_frame1 = frame1.copy()
    current_frame2 = frame2.copy()

    image1 = Image.fromarray(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))
    image2 = Image.fromarray(cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB))

    # Redimensionar las imágenes
    image1 = image1.resize((400, 400), Image.ANTIALIAS)
    image2 = image2.resize((400, 400), Image.ANTIALIAS)

    # Convertir a PhotoImage
    photo1 = ImageTk.PhotoImage(image1)
    photo2 = ImageTk.PhotoImage(image2)

    # Actualizar las etiquetas
    camera_labels[0].config(image=photo1)
    camera_labels[0].image = photo1  # Necesario para evitar que el garbage collector elimine la imagen
    camera_labels[1].config(image=photo2)
    camera_labels[1].image = photo2

def save_images(status_label, folder_name):
    global current_frame1, current_frame2
    if current_frame1 is not None and current_frame2 is not None:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        
        # Guardar imágenes
        cam1_path = f'captures/camera1_{timestamp}.png'
        cam2_path = f'captures/camera2_{timestamp}.png'

        if not os.path.exists('captures'):
            os.makedirs('captures')

        cv2.imwrite(cam1_path, current_frame1)
        cv2.imwrite(cam2_path, current_frame2)

        # Subir imágenes a Firebase
        upload_image_to_firebase(cam1_path, folder_name)
        upload_image_to_firebase(cam2_path, folder_name)

        # Actualizar etiqueta de estado en la interfaz
        status_label.config(text="Imágenes guardadas y subidas a Firebase.")
    else:
        status_label.config(text="No hay imágenes para guardar.")

def start_analysis_thread(status_label, camera_labels):
    analysis_thread = threading.Thread(target=start_cameras_and_analyze, args=(status_label, camera_labels))
    analysis_thread.start()

def create_gui():
    root = tk.Tk()
    root.title("Navarro Ortopedia")

    # Frame para datos del paciente
    data_frame = tk.Frame(root)
    data_frame.pack(pady=20)

    Label(data_frame, text="Paso").grid(row=0, column=0)
    Label(data_frame, text="Talla").grid(row=1, column=0)
    Label(data_frame, text="Altura").grid(row=2, column=0)
    Label(data_frame, text="Actividad / Deporte").grid(row=3, column=0)

    # Campos de entrada
    paso_entry = tk.Entry(data_frame)
    talla_entry = tk.Entry(data_frame)
    altura_entry = tk.Entry(data_frame)
    actividad_entry = tk.Entry(data_frame)

    paso_entry.grid(row=0, column=1)
    talla_entry.grid(row=1, column=1)
    altura_entry.grid(row=2, column=1)
    actividad_entry.grid(row=3, column=1)

    # Botones
    start_button = Button(root, text="Iniciar Análisis", command=lambda: start_analysis_thread(status_label, camera_labels))
    start_button.pack(pady=10)

    save_button = Button(root, text="Guardar Capturas", command=lambda: save_images(status_label, "captures"))
    save_button.pack(pady=10)

    close_button = Button(root, text="Cerrar", command=root.quit)
    close_button.pack(pady=10)

    status_label = Label(root, text="Listo para iniciar el análisis.")
    status_label.pack(pady=10)

    # Frame para mostrar las cámaras
    camera_frame = tk.Frame(root)
    camera_frame.pack(pady=20)

    # Etiquetas para mostrar las cámaras
    camera_labels = [Label(camera_frame), Label(camera_frame)]
    camera_labels[0].pack(side=tk.LEFT, padx=10)
    camera_labels[1].pack(side=tk.LEFT, padx=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
