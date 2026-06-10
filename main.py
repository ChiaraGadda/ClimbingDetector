import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime
import os
import numpy as np
import time

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

cap = None  # globale

def get_point(landmarks, idx, w, h):
    lm = landmarks[idx]

    return np.array([
        lm.x * w,
        lm.y * h
    ])

def load_to_color(load):
    
    load = max(0, min(load, 100))

    if load < 26:
        r = int(255*load/26)
        g = 255
    else:
        r = 255
        g = int((255*load/26)-255)

    return (0, g, r)

def draw_limb(image, p1, p2, load):
    
    cv2.line(
        image,
        tuple(p1.astype(int)),
        tuple(p2.astype(int)),
        load_to_color(load),
        8
    )

def cont():
    global cap

    if cap is None or not cap.isOpened():
        print("Errore: video non aperto")
        return

    timestamp_file = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"analized/{timestamp_file}.avi"

    fourcc = cv2.VideoWriter_fourcc(*"XVID")

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 45

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(
        filename,
        fourcc,
        fps,
        (frame_width, frame_height)
    )

    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:
        while cap.isOpened():

            success, image = cap.read()

            if not success:
                break

            image = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2RGB
            )

            results = pose.process(image)

            image = cv2.cvtColor(
                image,
                cv2.COLOR_RGB2BGR
            )

            if results.pose_landmarks:

                h, w, _ = image.shape
                lm = results.pose_landmarks.landmark

                # --------------------
                # BRACCIA
                # --------------------

                L_SHOULDER = get_point(lm, 11, w, h)
                R_SHOULDER = get_point(lm, 12, w, h)

                L_ELBOW = get_point(lm, 13, w, h)
                R_ELBOW = get_point(lm, 14, w, h)

                L_WRIST = get_point(lm, 15, w, h)
                R_WRIST = get_point(lm, 16, w, h)

                # --------------------
                # GAMBE
                # --------------------

                L_HIP = get_point(lm, 23, w, h)
                R_HIP = get_point(lm, 24, w, h)

                L_KNEE = get_point(lm, 25, w, h)
                R_KNEE = get_point(lm, 26, w, h)

                L_ANKLE = get_point(lm, 27, w, h)
                R_ANKLE = get_point(lm, 28, w, h)

                # --------------------
                # CENTRO DEL CORPO
                # --------------------

                torso_center = (
                    L_SHOULDER +
                    R_SHOULDER +
                    L_HIP +
                    R_HIP
                ) / 4

                # --------------------
                # DISTANZE
                # --------------------

                left_hand_dist = np.linalg.norm(
                    torso_center - L_WRIST
                )

                right_hand_dist = np.linalg.norm(
                    torso_center - R_WRIST
                )

                left_foot_dist = np.linalg.norm(
                    torso_center - L_ANKLE
                )

                right_foot_dist = np.linalg.norm(
                    torso_center - R_ANKLE
                )

                support_sum = (
                    left_hand_dist +
                    right_hand_dist +
                    left_foot_dist +
                    right_foot_dist
                )

                if support_sum < 1:
                    support_sum = 1

                # --------------------
                # CARICHI %
                # --------------------

                left_arm_load = (
                    left_hand_dist /
                    support_sum
                ) * 100

                right_arm_load = (
                    right_hand_dist /
                    support_sum
                ) * 100

                left_leg_load = (
                    left_foot_dist /
                    support_sum
                ) * 100

                right_leg_load = (
                    right_foot_dist /
                    support_sum
                ) * 100

                # --------------------
                # DISEGNO COLORATO
                # --------------------

                draw_limb(
                    image,
                    L_SHOULDER,
                    L_ELBOW,
                    left_arm_load
                )

                draw_limb(
                    image,
                    L_ELBOW,
                    L_WRIST,
                    left_arm_load
                )

                draw_limb(
                    image,
                    R_SHOULDER,
                    R_ELBOW,
                    right_arm_load
                )

                draw_limb(
                    image,
                    R_ELBOW,
                    R_WRIST,
                    right_arm_load
                )

                draw_limb(
                    image,
                    L_HIP,
                    L_KNEE,
                    left_leg_load
                )

                draw_limb(
                    image,
                    L_KNEE,
                    L_ANKLE,
                    left_leg_load
                )

                draw_limb(
                    image,
                    R_HIP,
                    R_KNEE,
                    right_leg_load
                )

                draw_limb(
                    image,
                    R_KNEE,
                    R_ANKLE,
                    right_leg_load
                )

                # --------------------
                # BARICENTRO
                # --------------------

                cv2.circle(
                    image,
                    tuple(torso_center.astype(int)),
                    8,
                    (255, 255, 255),
                    -1
                )

                # --------------------
                # TESTO
                # --------------------

                cv2.putText(
                    image,
                    f"L Arm: {left_arm_load:.1f}%",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    load_to_color(left_arm_load),
                    2
                )

                cv2.putText(
                    image,
                    f"R Arm: {right_arm_load:.1f}%",
                    (20, 110),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    load_to_color(right_arm_load),
                    2
                )

                cv2.putText(
                    image,
                    f"L Leg: {left_leg_load:.1f}%",
                    (20, 140),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    load_to_color(left_leg_load),
                    2
                )

                cv2.putText(
                    image,
                    f"R Leg: {right_leg_load:.1f}%",
                    (20, 170),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    load_to_color(right_leg_load),
                    2
                )

                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
                )

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            cv2.putText(
                image,
                timestamp,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )

            out.write(image)

            cv2.imshow(
                "ClimbVision Pose",
                cv2.flip(image, 1)
            )

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
    cap = cv2.VideoCapture("media/video.mp4")
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
bg_cap = cv2.VideoCapture("media/wallpaper.mp4")


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