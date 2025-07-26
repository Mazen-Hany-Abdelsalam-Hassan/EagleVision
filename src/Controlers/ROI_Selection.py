from copy import deepcopy
import cv2
import numpy as np

class ROI_Selection:
    def __init__(self, image: np.array):
        self.points = []
        self.image = image

    def mouse_callback(self, event, x, y, flags, param):
        image_copy = deepcopy(self.image)
        if event == cv2.EVENT_LBUTTONDOWN:
            self.points.append((x, y))

        elif event == cv2.EVENT_RBUTTONDOWN:
            self.points.pop()

        elif event == cv2.EVENT_MOUSEMOVE:
            mouse_pos = (x, y)
            cv2.circle(image_copy, mouse_pos, 2, (255, 0, 255), 1)
            if len(self.points) >= 1:
                cv2.line(image_copy, mouse_pos, self.points[-1], (255, 0, 255), 1)

        for i in range(len(self.points)):
            cv2.circle(image_copy, self.points[i], 2, (255, 0, 255), 1)
        if len(self.points) >= 2:
            for i in range(0, len(self.points) - 1):
                cv2.line(image_copy, self.points[i], self.points[i + 1], (255, 0, 255), 1)
        cv2.imshow('image', image_copy)

    def main(self):
        cv2.imshow('image', self.image)
        cv2.setMouseCallback('image', self.mouse_callback)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return self.points



