import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime
import os

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

cap = None  # globale

def cont():
    global cap

    if cap is None or not cap.isOpened():
        print("Errore: video non aperto")
        return

    # ---- crea nome file con data e ora ----
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"webcam/{timestamp}.avi"

    # ---- codec e writer ----
    fourcc = cv2.VideoWriter_fourcc(*"XVID")

    fps = 60.0
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(filename, fourcc, fps, (frame_width, frame_height))

    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:

        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
            )
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cv2.putText(
                image,
                timestamp,
                (10, 30),  # posizione in alto a sinistra
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),  # verde
                2,
                cv2.LINE_AA
            )

            # ---- Mette le scritte nel video ----
            out.write(image)

            cv2.imshow("ClimbVision Pose", cv2.flip(image, 1))

            if cv2.waitKey(5) & 0xFF == 27:
                break

    cap.release()
    out.release()
    cv2.destroyAllWindows()


def cam():
    global cap
    cap = cv2.VideoCapture(1)
    cont()


def fi():
    global cap
    cap = cv2.VideoCapture("video.mp4")
    cont()


# ---------------- GUI ----------------

finestra = tk.Tk()
# centrato rispetto allo schermo
finestra.update_idletasks()
l = 600
a = 400

x = (finestra.winfo_screenwidth() // 2) - (l // 2)
y = (finestra.winfo_screenheight() // 2) - (a // 2)

finestra.geometry(f"{l}x{a}+{x}+{y}")


finestra.title("ClimbVision – AI Climbing Pose Analyzer")
finestra.geometry("600x400")
finestra.resizable(False, False)

# sfondo
canvas = tk.Canvas(finestra, width=600, height=400, highlightthickness=0)
canvas.pack(fill="both", expand=True)

bg_label = canvas.create_image(0, 0, anchor="nw")

# video background
bg_cap = cv2.VideoCapture("wallpaper.mp4")


def animate_bg():
    ret, frame = bg_cap.read()

    if not ret:
        bg_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = bg_cap.read()

    frame = cv2.resize(frame, (l, a))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    img = ImageTk.PhotoImage(Image.fromarray(frame))

    canvas.img = img
    canvas.itemconfig(bg_label, image=img)

    finestra.after(15, animate_bg)


animate_bg()


# ---------------- OVERLAY UI ----------------

frame = tk.Frame(finestra, bg="#000000")
frame.place(relx=0.5, rely=0.5, anchor="center")

title = tk.Label(
    frame,
    text="GaddaClimbVision",
    font=("Helvetica", 26, "bold"),
    fg="white",
    bg="black"
)
title.pack(pady=5)

subtitle = tk.Label(
    frame,
    text="AI Analyzer for Climbing",
    font=("Helvetica", 12),
    fg="#cccccc",
    bg="black"
)
subtitle.pack(pady=5)

style = ttk.Style()
style.theme_use("clam")

btn1 = ttk.Button(frame, text="📷 Webcam", command=cam)
btn1.pack(pady=10, ipadx=10)

btn2 = ttk.Button(frame, text="🎥 Video", command=fi)
btn2.pack(pady=10, ipadx=10)

finestra.mainloop()