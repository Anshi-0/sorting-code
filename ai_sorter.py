import cv2
import numpy as np
import time
from enum import Enum
import random

# Mechatronics components (virtualized)
class ObjectColor(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
    UNKNOWN = 4

class VirtualConveyor:
    def __init__(self):
        self.position = 0
        self.speed = 0.5  # units/frame
        self.objects = []
        
    def add_object(self, color):
        self.objects.append({
            "color": color,
            "position": 0,
            "id": random.randint(1000, 9999)
        })
    
    def update(self):
        self.position += self.speed
        for obj in self.objects:
            obj["position"] += self.speed
        return [obj for obj in self.objects if obj["position"] < 100]  # Remove objects past 100 units

class VirtualActuator:
    def __init__(self):
        self.position = 0  # 0=closed, 1=open
        self.target = 0
    
    def set_position(self, pos):
        self.target = pos
        
    def update(self):
        # Simulate mechanical movement delay
        if self.position < self.target:
            self.position += 0.1
        elif self.position > self.target:
            self.position -= 0.1
        return self.position

# AI Color Detector (using OpenCV)
class AIColorDetector:
    def __init__(self):
        self.lower_red = np.array([0, 100, 100])
        self.upper_red = np.array([10, 255, 255])
        self.lower_green = np.array([40, 100, 100])
        self.upper_green = np.array([80, 255, 255])
        self.lower_blue = np.array([100, 100, 100])
        self.upper_blue = np.array([140, 255, 255])
        
    def detect(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # AI-based color masks
        mask_red = cv2.inRange(hsv, self.lower_red, self.upper_red)
        mask_green = cv2.inRange(hsv, self.lower_green, self.upper_green)
        mask_blue = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
        
        # Determine dominant color
        red_pixels = cv2.countNonZero(mask_red)
        green_pixels = cv2.countNonZero(mask_green)
        blue_pixels = cv2.countNonZero(mask_blue)
        
        if red_pixels > green_pixels and red_pixels > blue_pixels:
            return ObjectColor.RED
        elif green_pixels > red_pixels and green_pixels > blue_pixels:
            return ObjectColor.GREEN
        elif blue_pixels > red_pixels and blue_pixels > green_pixels:
            return ObjectColor.BLUE
        else:
            return ObjectColor.UNKNOWN

# Main System
class AutomatedSorter:
    def __init__(self):
        self.conveyor = VirtualConveyor()
        self.gate = VirtualActuator()
        self.detector = AIColorDetector()
        self.target_color = ObjectColor.RED
        self.sorted_counts = {color: 0 for color in ObjectColor}
        
        # Create virtual camera input (synthetic data)
        self.cap = self.create_virtual_camera()
        
    def create_virtual_camera(self):
        # Generate test images with colored rectangles
        def generate_frame():
            frame = np.zeros((300, 400, 3), dtype=np.uint8)
            color = random.choice([
                (0, 0, 255),   # Red
                (0, 255, 0),    # Green
                (255, 0, 0)     # Blue
            ])
            cv2.rectangle(frame, (50, 50), (350, 250), color, -1)
            return frame
        return generate_frame
        
    def run(self):
        cv2.namedWindow("Automated Sorter", cv2.WINDOW_NORMAL)
        
        while True:
            # 1. Mechatronics: Sensor Input
            frame = self.cap()
            color = self.detector.detect(frame)
            
            # 2. Control System
            if color == self.target_color:
                self.gate.set_position(1)  # Open gate
                self.sorted_counts[color] += 1
            else:
                self.gate.set_position(0)  # Close gate
                
            # 3. Actuator Update
            gate_pos = self.gate.update()
            
            # 4. Mechanical System Update
            active_objects = self.conveyor.update()
            
            # Visualization
            vis = np.zeros((400, 600, 3), dtype=np.uint8)
            
            # Draw conveyor
            cv2.rectangle(vis, (50, 150), (550, 200), (200, 200, 200), -1)
            
            # Draw objects
            for obj in active_objects:
                x = int(50 + obj["position"] * 5)
                color_map = {
                    ObjectColor.RED: (0, 0, 255),
                    ObjectColor.GREEN: (0, 255, 0),
                    ObjectColor.BLUE: (255, 0, 0)
                }
                cv2.circle(vis, (x, 175), 15, color_map.get(obj["color"], (255, 255, 255)), -1)
            
            # Draw gate
            gate_x = 400  # Sensor position
            gate_open = int(175 - gate_pos * 50)
            cv2.line(vis, (gate_x, 175), (gate_x, gate_open), (0, 255, 255), 3)
            
            # Draw sensor
            cv2.circle(vis, (gate_x, 175), 8, (0, 255, 255), 2)
            
            # Display info
            cv2.putText(vis, f"Target: {self.target_color.name}", (20, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(vis, f"Sorted: {self.sorted_counts}", (20, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow("Automated Sorter", vis)
            
            # Add new objects randomly
            if random.random() < 0.03:
                self.conveyor.add_object(random.choice([
                    ObjectColor.RED, 
                    ObjectColor.GREEN, 
                    ObjectColor.BLUE
                ]))
            
            # Key controls
            key = cv2.waitKey(30)
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.target_color = ObjectColor.RED
            elif key == ord('g'):
                self.target_color = ObjectColor.GREEN
            elif key == ord('b'):
                self.target_color = ObjectColor.BLUE
        
        cv2.destroyAllWindows()

# Run the system
if __name__ == "__main__":
    print("Starting Automated Sorting System with AI...")
    sorter = AutomatedSorter()
    sorter.run()