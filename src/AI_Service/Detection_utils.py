import cv2
from typing import Dict
class Detection_utils:
    @staticmethod
    def show_result(frame, frame_prediction: list, to_show:Dict[str]):
        font = cv2.FONT_HERSHEY_SIMPLEX
        for prediction in frame_prediction['objects']:
            if prediction['label'] in to_show.keys():
                cv2.rectangle(frame,prediction['bbox'][0:2] , prediction['bbox'][2:] , color = to_show[prediction['label']] , thickness=3 )
                cv2.putText(frame,str(prediction['label']),prediction['bbox'][0:2],font, 2,color =  to_show[prediction['label']])