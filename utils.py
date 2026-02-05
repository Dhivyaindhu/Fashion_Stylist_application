import mediapipe as mp
import cv2
import numpy as np

mp_pose = mp.solutions.pose

def extract_body_features(image):
    pose = mp_pose.Pose(static_image_mode=True)
    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    if not results.pose_landmarks:
        return None

    lm = results.pose_landmarks.landmark

    def dist(a, b):
        return np.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)

    shoulder_width = dist(lm[11], lm[12])
    hip_width = dist(lm[23], lm[24])
    torso_height = dist(lm[11], lm[23])
    leg_length = dist(lm[23], lm[27])

    features = np.array([
        shoulder_width,
        hip_width,
        torso_height,
        leg_length
    ])

    return features
