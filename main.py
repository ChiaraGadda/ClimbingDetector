import cv2
import mediapipe as mp

# setup
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

print("Scegli sorgente video:")
print("1 - Webcam")
print("2 - Video file (.mp4)")

choice = input("Inserisci scelta (1/2): ")

if choice == "1":
    cap = cv2.VideoCapture(0)  # webcam
    print("Webcam avviata...")

elif choice == "2":
    video_path = input("Inserisci nome file video (es: video.mp4): ")
    cap = cv2.VideoCapture(video_path)
    print(f"Video caricato: {video_path}")

else:
    print("Scelta non valida")
    exit()

if not cap.isOpened():
    print("Errore: impossibile aprire la sorgente video")
    exit()

with mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as pose:

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Fine video o frame non disponibile")
            break

        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
        )

        cv2.imshow('MediaPipe Pose Estimation', cv2.flip(image, 1))

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()