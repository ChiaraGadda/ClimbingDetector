import cv2
import mediapipe as mp
import tkinter as tk

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

cap = None  # globale

def cont():
    global cap

    if cap is None or not cap.isOpened():
        print("Errore: video non aperto")
        return

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

            cv2.imshow("Pose", cv2.flip(image, 1))

            if cv2.waitKey(5) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()


def cam():
    global cap
    cap = cv2.VideoCapture(0)
    print("Webcam avviata")
    cont()


def fi():
    global cap
    cap = cv2.VideoCapture("video.mp4")
    print("Video caricato")
    cont()


# GUI
finestra = tk.Tk()
finestra.title("Seleziona sorgente")

frame = tk.Frame(finestra)
frame.pack()

tk.Label(frame, text="Seleziona la fonte").pack()

tk.Button(frame, text="Webcam", command=cam).pack()
tk.Button(frame, text="Video mp4", command=fi).pack()

finestra.mainloop()