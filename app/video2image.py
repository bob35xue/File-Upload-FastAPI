import cv2
import os
import shutil
from datetime import datetime

def create_backup_folder():
    # Create backup folder with date
    date_str = datetime.now().strftime('%Y%m%d')
    backup_dir = os.path.join("app", "data4B", "backup", "uploads", date_str)
    
    # Create the backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    return backup_dir

def extract_frames(video_path, output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

     # Get video filename without extension
    video_filename = os.path.splitext(os.path.basename(video_path))[0]
    
    # Read the video
    video = cv2.VideoCapture(video_path)
    
    # Get video properties
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    print(frame_count)
    # Calculate frame interval (extract 1 frame per second)
    frame_interval = int(fps)
    print( frame_interval)
    count = 0
    frame_number = 0
    
    while True:
        success, frame = video.read()
        if not success:
            break
            
        # Save frame at intervals
        if count % frame_interval == 0:
            # frame_path = os.path.join(output_folder, f'frame_{frame_number:04d}.jpg')
            # New naming convention: videoname_frameXXXX.jpg
            frame_path = os.path.join(output_folder, f'{video_filename}_frame_{frame_number:04d}.jpg')

            cv2.imwrite(frame_path, frame)
            frame_number += 1
            print()
            
        count += 1
    
    video.release()
    return frame_number

def process_videos():
    uploads_dir = "uploads"
    output_dir = "app/data4B/input_images"
    backup_dir = create_backup_folder()
    
    # Process all mp4 files in uploads directory
    for filename in os.listdir(uploads_dir):
        if filename.endswith(".mp4"):
            video_path = os.path.join(uploads_dir, filename)
            try:
                # Extract frames
                frames_extracted = extract_frames(video_path, output_dir)
                print(f"Extracted {frames_extracted} frames from {filename}")
                
                # Move video file to backup folder
                backup_path = os.path.join(backup_dir, filename)
                shutil.move(video_path, backup_path)
                print(f"Moved {filename} to backup folder: {backup_dir}")
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    process_videos()