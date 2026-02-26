import cv2
import numpy as np
import sys
import os

def create_blinking_image_manual(input_path, output_path):
    image = cv2.imread(input_path)
    if image is None:
        print(f"Could not read {input_path}")
        return

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    eyes = eye_cascade.detectMultiScale(gray, 1.1, 4)

    # Sort eyes by Y coordinate to get the upper ones (actual eyes, not mouth/nose false positives)
    eyes = sorted(eyes, key=lambda e: e[1])
    
    # Take top 2 eyes
    main_eyes = eyes[:2]
    
    if len(main_eyes) < 2:
        print("Could not find two eyes properly.")
        return
        
    for (x, y, w, h) in main_eyes:
        print(f"Processing Eye: x={x}, y={y}, w={w}, h={h}")
        # Get skin color from just above the eye
        skin_y = max(0, y - int(h * 0.2))
        skin_x = x + w // 2
        
        # Sample average color around this point
        color_patch = image[skin_y-2:skin_y+2, skin_x-2:skin_x+2]
        avg_color = np.mean(color_patch, axis=(0,1))
        avg_color = (int(avg_color[0]), int(avg_color[1]), int(avg_color[2]))
        
        # We need to cover the eye itself
        cover_y1 = y + int(h * 0.2)
        cover_y2 = y + int(h * 0.8)
        cover_x1 = x + int(w * 0.1)
        cover_x2 = x + int(w * 0.9)
        
        # Draw ellipse/rectangle to cover eye with skin tone
        # Create an elliptical mask for softer blending
        center = (x + w//2, y + h//2)
        axes = (int(w*0.45), int(h*0.3))
        
        cv2.ellipse(image, center, axes, 0, 0, 360, avg_color, -1)
        
        # Draw closed eyelash line
        eyelash_color = (15, 15, 15)
        # Curve points
        curve_pts = np.array([
            [x + int(w*0.1), y + int(h*0.5)],
            [x + int(w*0.3), y + int(h*0.6)],
            [x + int(w*0.5), y + int(h*0.65)],
            [x + int(w*0.7), y + int(h*0.6)],
            [x + int(w*0.9), y + int(h*0.5)]
        ], np.int32)
        
        cv2.polylines(image, [curve_pts], False, eyelash_color, 2, cv2.LINE_AA)

    cv2.imwrite(output_path, image)
    print(f"Saved blinking image to {output_path}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_img = os.path.join(script_dir, "interviewer_woman.png")
    output_img = os.path.join(script_dir, "interviewer_woman_blink.png")
    create_blinking_image_manual(input_img, output_img)
