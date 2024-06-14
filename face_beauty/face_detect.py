import cv2
import mediapipe as mp
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

def get_face_key_point(img):
  with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
    results = face_detection.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    if not results.detections:
      return None
    annotated_image = img.copy()
    r,w,c =img.shape
    for detection in results.detections:
      left_eye =mp_face_detection.get_key_point(detection, mp_face_detection.FaceKeyPoint.LEFT_EYE)
      right_eye =mp_face_detection.get_key_point(detection, mp_face_detection.FaceKeyPoint.RIGHT_EYE)
      left_eye_pos = [int(left_eye.x * w), int(left_eye.y * r)]
      right_eye_pos = [int(right_eye.x * w), int(right_eye.y * r)]
      return  left_eye_pos,right_eye_pos
