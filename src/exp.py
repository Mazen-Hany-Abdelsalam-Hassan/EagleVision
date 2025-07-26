from AI_Service.Yolo_Model import Yolo_Model
import cv2
model = Yolo_Model()

video_path = r"C:\Users\Mazen\Desktop\video\Sah w b3dha ghalt (3).mp4"
cap = cv2.VideoCapture(video_path)
while cap.isOpened():
    ret, frame = cap.read()
    frame = cv2.resize(frame, (960, 608))
    # Run detection (predict returns a list of results; take first)
    result = model(frame)
    frame = model.draw_boxes_by_class(frame,result,1)
    print(result)
    cv2.imshow('ma',frame)
    cv2.waitKey(0)
    break


