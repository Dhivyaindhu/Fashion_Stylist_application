import mediapipe as mp
import numpy as np

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose

def extract_body_features(image_np):
    """
    Extract normalized body measurements from a full-body image
    using MediaPipe Pose landmarks.

    Parameters:
        image_np (numpy.ndarray): RGB image array (H, W, 3)

    Returns:
        numpy.ndarray or None: Feature vector [shoulder, hip, torso, leg]
    """

    # Ensure image is RGB
    if image_np.shape[-1] != 3:
        return None

    with mp_pose.Pose(
        static_image_mode=True,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5
    ) as pose:

        results = pose.process(image_np)

        if not results.pose_landmarks:
            return None

        lm = results.pose_landmarks.landmark

        # Distance helper
        def dist(a, b):
            return np.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)

        # Key body measurements
        shoulder_width = dist(lm[11], lm[12])
        hip_width = dist(lm[23], lm[24])
        torso_height = dist(lm[11], lm[23])
        leg_length = dist(lm[23], lm[27])

        # Stack features
        features = np.array([
            shoulder_width,
            hip_width,
            torso_height,
            leg_length
        ], dtype=np.float32)

        # Normalize features (important for CNN stability)
        features = features / np.max(features)

        return features
