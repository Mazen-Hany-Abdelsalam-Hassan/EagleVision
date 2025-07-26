import cv2
import numpy as np


class ROI:
    HandFromROIThreshold = 20
    HandToScooperThreshold = 40
    ScooperToROIThreshold = 80
    TimeToRecordViolation = 30

    @staticmethod
    def filter_scooper(forbidden_area, scoopers):
        """
        This method use to filter any scooper inside a specific area
        parameters :
        scoopers: Bounding box represent the scoopers
        forbidden_area : Area which we damp the detection of the model for the scoopers
        """
        outside_ROI_scooper = []
        for scooper in scoopers:
            scooper_center = ROI.FindCenter(scooper)
            if not ROI.IsInside(forbidden_area, scooper_center):
                outside_ROI_scooper.append(scooper)
        return outside_ROI_scooper

    @staticmethod
    def IsInside(ROI, center):
        """
        Identify if the hand located inside ROI
        parameters:
        ROI:np.array
        center:tuple
        return
        True if hand lies inside ROI
        False if hand outside ROI
        """
        test = cv2.pointPolygonTest(ROI, center, False)
        return test >= 0

    @staticmethod
    def FindCenter(bbox):
        """
        Find the center of the bounding box
        params: bbox
        returns :

        (xc , yc)
        """
        x_min, y_min, x_max, y_max = bbox
        return int((x_min + x_max) / 2), int((y_min + y_max) / 2)


    @staticmethod
    def FindDistance(p1, p2):
        """
        Find the Euclidean distance between two points.

        Parameters:
        - p1: First point as a list or tuple [x1, y1]
        - p2: Second point as a list or tuple [x2, y2]

        Returns:
        - float: Euclidean distance between p1 and p2
        """
        return np.linalg.norm(np.array(p1) - np.array(p2))

    @staticmethod
    def FindDistanceROI(ROI, point):
        """
        Calculate the shortest signed distance between a point and the ROI contour.

        Parameters:
        - ROI: np.array of shape (n, 2) or (n, 1, 2), representing the polygon contour.
        - point: tuple (x, y), the target point.

        Returns:
        - float: Signed distance from the point to the contour.
                 Positive if inside, negative if outside, 0 if on the edge.
        """
        return abs(cv2.pointPolygonTest(ROI, point, True))

    def __init__(self, ROI):

        self.ROI = ROI
        # Value to track
        self.violation = 0
        self.frame_out = 0
        ### Flags
        self.HAND_INSIDE = False
        self.HAND_OUTSIDE = False
        self.PRE_VIOLATION = False

    def main(self, hands, frame, scooper):
        self.HandInsideROI(hands, frame)
        self.HandOutside(hands, frame)
        return self.Logic(scooper, frame)

    def HandInsideROI(self, hands, frame):
        """
        This method is Used to Raise HAND_INSIDE , PRE_VIOLATION
        """
        for hand in hands:
            hand_center = ROI.FindCenter(hand)
            inside = ROI.IsInside(self.ROI, hand_center)
            if inside:
                cv2.rectangle(frame, hand[0:2], hand[2:], (255, 255, 100), 2)
                self.HAND_INSIDE = True
                self.HAND_OUTSIDE = False
                self.PRE_VIOLATION = True
            else:
                self.HAND_INSIDE = False

    def HandOutside(self, hands, frame):
        for hand in hands:
            hand_center = ROI.FindCenter(hand)
            inside = ROI.IsInside(self.ROI, hand_center)

            distance_from_ROI = ROI.FindDistanceROI(self.ROI, hand_center)
            distance_thresh = distance_from_ROI <= ROI.HandFromROIThreshold
            if not inside and distance_thresh and self.PRE_VIOLATION:
                self.HAND_OUTSIDE = True
                cv2.circle(frame, hand_center, 1, (255, 255, 255))

    def Logic(self, scoopers, frame):
        filtered_scoopers = ROI.filter_scooper(self.ROI, scoopers)
        if self.HAND_OUTSIDE:
            for filtered_scooper in filtered_scoopers:
                filtered_scooper_center = ROI.FindCenter(filtered_scooper)
                #distance = ROI.FindDistanceROI(self.ROI, filtered_scooper_center)
                nearby_scooper = ROI.FindDistanceROI(self.ROI, filtered_scooper_center) < ROI.ScooperToROIThreshold
                # cv2.putText(frame,f"distance = {distance}",(300,100),font, 4,color = (255 , 0,255),thickness = 8)
                if nearby_scooper:
                    cv2.rectangle(frame, filtered_scooper[0:2], filtered_scooper[2:4], (0, 0, 255), 3)
                    self.PRE_VIOLATION = False
                    self.frame_out = 0
                    self.HAND_OUTSIDE = False

                    return None

            self.frame_out += 1
            if self.frame_out == ROI.TimeToRecordViolation:
                self.violation += 1
                self.frame_out = 0
                self.PRE_VIOLATION = False
                self.HAND_OUTSIDE = False
                return "Violation"
            return None
        return None




