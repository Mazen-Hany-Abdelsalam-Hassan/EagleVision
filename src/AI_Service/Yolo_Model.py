import os
from ultralytics import YOLO
import numpy as np
import  torch
from Helper import Settings , get_setting
import cv2
class Yolo_Model:
    def __init__(self):
        self.env = get_setting()
        parent_dir = os.path.dirname(os.path.dirname(__file__))
        model_dir = os.path.join(parent_dir, "YOLO_Model")
        for filename in os.listdir(model_dir):
            if filename.endswith(".pt"):
                self.model = os.path.join(model_dir, filename)
                break
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = YOLO(self.model).to(device=device)
        self.ClassMapping =  {0: "hand", 1: "person", 2: "pizza", 3: "scooper"}
        self.color_config =   {
    "scooper": (255, 255, 255),
    "hand": (255, 0, 0),
    "person": (0, 0, 255),
    "pizza": (0, 255, 0)
}

    def filter_boxes_by_class(self , prediction_classes, boxes ):
        """
        Filters prediction boxes into separate lists by class.

        Args:
            prediction_classes (list): List of predicted class indices.
            boxes (list): List of boxes corresponding to predictions.
            class_mapping (dict): Mapping from class index to class name.

        Returns:
            dict: A dictionary where keys are class names and values are lists of boxes.
        """
        # Initialize empty lists for each class name
        filtered = {class_name: [] for class_name in self.ClassMapping.values()}

        # Fill the lists
        for cls, box in zip(prediction_classes, boxes):
            class_name = self.ClassMapping.get(cls)
            if class_name:
                filtered[class_name].append(box)

        return filtered

    def draw_boxes_by_class(self, image, filtered_boxes, thickness=2):
        """
        Draws boxes on the image for each class in filtered_boxes using given color_config.

        Args:
            image (np.ndarray): Image to draw on.
            filtered_boxes (dict): {class_name: [boxes]}
            thickness (int): Thickness of rectangle lines.

        Returns:
            np.ndarray: Image with drawn boxes.
        """
        for class_name, boxes in filtered_boxes.items():
            color = self.color_config.get(class_name, (255, 255, 255))  # default to white if not found
            for box in boxes:
                x1, y1, x2, y2 = box
                cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
                cv2.putText(image, class_name, (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
        return image

    def __call__(self, frame:np.array):
        result = self.model.predict(source=frame , conf= self.env.MODEL_CONF , iou=self.env.MODEL_IOU
                                    )[0]
        boxes = result.boxes
        prediction_classes = boxes.cls.cpu().numpy().astype(int).tolist()
        boxes_coord = boxes.xyxy.cpu().numpy().astype(int).tolist()
        return  self.filter_boxes_by_class(prediction_classes=prediction_classes ,
                                           boxes = boxes_coord )




