from ultralytics import YOLO
import cv2
import os
import math
import numpy as np
import shutil
from datetime import datetime

def backup_processed_images(input_folder):
    # Create backup folder with date
    date_str = datetime.now().strftime('%Y%m%d')
    backup_dir = os.path.join("app", "data4B", "backup", "input_images", date_str)
    
    # Create the backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Move all images to backup
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            source_path = os.path.join(input_folder, filename)
            dest_path = os.path.join(backup_dir, filename)
            try:
                shutil.move(source_path, dest_path)
                print(f"Moved {filename} to backup folder: {backup_dir}")
            except Exception as e:
                print(f"Error moving {filename}: {str(e)}")

def main():
    try:
        # Paths
        input_folder = "app/data4b/input_images"
        seg_output_folder = "app/data4B/output/segmentation"
        defect_output_folder = "app/data4b/output/defects"

        # Create output folders if they don't exist
        os.makedirs(seg_output_folder, exist_ok=True)
        os.makedirs(defect_output_folder, exist_ok=True)

        # Load models
        bundle_model = YOLO("app/data4b/models/bundle_best.pt")
        det_model = YOLO("app/data4b/models/best.pt")  # Adjust this path if necessary
        seg_model = YOLO("app/data4b/models/obj_best.pt")  # seg_best.pt

        # Object classes for detection
        classNames = ["bundle", "debris_fretting", "debris_proud_feature", "flow_stain", 
                     "hydriding", "scrapes", "sheath_breach"]

        # Process each image in the input folder
        for img_file in os.listdir(input_folder):
            img_path = os.path.join(input_folder, img_file)
            img = cv2.imread(img_path)

            if img is None:
                print(f"Error reading {img_file}. Skipping...")
                continue

            # Step 1: Run Bundle Detection to find the narrowest and shortest bounding box
            bundle_results = bundle_model(img, stream=True)

            smallest_box = None
            min_area = float('inf')

            for r in bundle_results:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cls = int(box.cls[0])

                    if classNames[cls] == "bundle":
                        width = x2 - x1
                        height = y2 - y1
                        area = width * height

                        if area < min_area:
                            min_area = area
                            smallest_box = (x1, y1, x2, y2)

            # Proceed if a bundle was detected
            if smallest_box:
                x1, y1, x2, y2 = smallest_box
                crop_img = img[y1:y2, x1:x2]

                # Step 2: Run Defect Detection within the bundle area
                defect_results = det_model(crop_img, stream=True)
                for r in defect_results:
                    for box in r.boxes:
                        cls = int(box.cls[0])
                        if classNames[cls] != "bundle":
                            box_x1, box_y1, box_x2, box_y2 = map(int, box.xyxy[0])
                            obj_x1, obj_y1 = x1 + box_x1, y1 + box_y1
                            obj_x2, obj_y2 = x1 + box_x2, y1 + box_y2
                            cv2.rectangle(img, (obj_x1, obj_y1), (obj_x2, obj_y2), (255, 0, 255), 3)
                            confidence = math.ceil((box.conf[0] * 100)) / 100
                            cv2.putText(img, f"{classNames[cls]} {confidence}", 
                                      (obj_x1, obj_y1 - 10),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                # Save the defect detection result
                defect_output_path = os.path.join(defect_output_folder, img_file)
                cv2.imwrite(defect_output_path, img)

                # Step 3: Run Segmentation within the bundle area
                seg_results = seg_model(img)
                segmented_img = img.copy()

                for result in seg_results:
                    annotated_img = result.plot()
                    annotated_img = cv2.cvtColor(annotated_img, cv2.COLOR_RGB2BGR)
                    mask = annotated_img[y1:y2, x1:x2]
                    segmented_img[y1:y2, x1:x2] = cv2.addWeighted(
                        segmented_img[y1:y2, x1:x2], 0.5, mask, 0.5, 0
                    )

                # Save the segmentation result
                seg_output_path = os.path.join(seg_output_folder, img_file)
                cv2.imwrite(seg_output_path, segmented_img)

            else:
                print(f"No bundle detected in {img_file}. Skipping segmentation and defect detection.")

        print("Processing complete.")
        backup_processed_images(input_folder)
        print("Image backup completed successfully")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()