from astropy.utils.misc import pizza

from .Yolo_Model import Yolo_Model
from .ROI import ROI
from typing import List
import  numpy as np
import cv2
class AI_Service:
    def __init__(self, region_of_interest:List[List]):
        self.Yolo = Yolo_Model()
        self.region_of_interest = np.array(region_of_interest)
        self.ROI = ROI(self.region_of_interest)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
    def main(self,frame):
        cv2.polylines(frame ,[self.region_of_interest],isClosed=True, color=(0, 255, 255), thickness=1)
        result = self.Yolo(frame=frame)
        frame = self.Yolo.draw_boxes_by_class(frame, result, 1)
        hands = result["hand"]
        scoopers = result["scooper"]
        violation = self.ROI.main(hands = hands, frame = frame, scooper = scoopers)
        cv2.putText(frame, f"Violation = {self.ROI.violation}", (100, 100), self.font, 3, color=(255, 0, 255), thickness=3)
        return  violation
