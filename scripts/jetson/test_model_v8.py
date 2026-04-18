import cv2
import random
from ultralytics import YOLO

# --- CONFIGURATION ---
model_path = "/home/orin_uav/main_ws/src/Model/10k_best_v8.pt"
input_video_path = "/home/orin_uav/main_ws/src/Test/PXL_20241029_172300458.mp4"
output_image_path = "/home/orin_uav/main_ws/src/Test/random_frame_inference.jpg"
target_size = (1920, 1080)  # Width, Height
# ----------------------

try:
    # Load YOLOv8 model
    model = YOLO(model_path)

    # Open video
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video file: {input_video_path}")
        exit()

    # Get total number of frames
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames == 0:
        print("Error: No frames found in the video.")
        cap.release()
        exit()

    # Pick one random frame
    random_frame_index = random.randint(0, total_frames - 1)
    print(f"Running inference on frame {random_frame_index} of {total_frames}")

    # Seek to that frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame_index)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Error: Could not read the selected frame.")
        exit()

    # Resize to 1920x1080
    frame = cv2.resize(frame, target_size)

    # Run inference
    results = model(frame, verbose=False)[0]

    # Draw detections (no confidence filter)
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        class_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = results.names.get(class_id, f"class {class_id}")

        # Draw box and label
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Display the frame with interruptible waitKey
    cv2.imshow("Random Frame Inference", frame)
    try:
        while True:
            if cv2.waitKey(100) != -1:
                break
    except KeyboardInterrupt:
        print("Process interrupted by user during display.")
    finally:
        cv2.destroyAllWindows()

    # Save the result
    cv2.imwrite(output_image_path, frame)
    print(f"Saved inference result to: {output_image_path}")

except KeyboardInterrupt:
    print("Process interrupted by user.")
    cv2.destroyAllWindows()
