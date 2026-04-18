import pyzed.sl as sl
import cv2
import mediapipe as mp
import numpy as np
import csv
import os

def track_and_log():
    # Initialize ZED camera
    zed = sl.Camera()
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD720
    init_params.depth_mode = sl.DEPTH_MODE.NEURAL
    init_params.coordinate_units = sl.UNIT.MILLIMETER

    if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
        print("Failed to open ZED camera")
        exit()

    runtime_params = sl.RuntimeParameters()
    image = sl.Mat()
    point_cloud = sl.Mat()

    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)
    mp_draw = mp.solutions.drawing_utils

    # Prepare CSV log file
    log_file = "hand_coordinates.csv"
    if not os.path.exists(log_file):
        with open(log_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Frame", "X (mm)", "Y (mm)", "Z (mm)"])

    frame_count = 0

    try:
        while True:
            if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
                zed.retrieve_image(image, sl.VIEW.LEFT)
                zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)

                img = image.get_data()
                if img.shape[2] == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                results = hands.process(img_rgb)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        h, w, _ = img.shape
                        wrist = hand_landmarks.landmark[0]
                        cx, cy = int(wrist.x * w), int(wrist.y * h)

                        err, point = point_cloud.get_value(cx, cy)
                        if err == sl.ERROR_CODE.SUCCESS and np.isfinite(point[2]):
                            x, y, z = point[0], point[1], point[2]

                            # Log to CSV
                            with open(log_file, "a", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerow([frame_count, round(x, 2), round(y, 2), round(z, 2)])

                            # Display text on image
                            distance_text = f"X: {x:.1f} mm | Y: {y:.1f} mm | Z: {z:.1f} mm"
                            x_vals = [int(lm.x * w) for lm in hand_landmarks.landmark]
                            y_vals = [int(lm.y * h) for lm in hand_landmarks.landmark]
                            x_min, x_max = min(x_vals), max(x_vals)
                            y_min, y_max = min(y_vals), max(y_vals)

                            cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                            cv2.putText(img, distance_text, (x_min, y_min - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                            print(f"[Frame {frame_count}] Wrist 3D: X={x:.1f}, Y={y:.1f}, Z={z:.1f} mm")
                        else:
                            print(f"[Frame {frame_count}] Wrist detected, but depth unavailable.")
                else:
                    print(f"[Frame {frame_count}] No hand detected.")

                # Show image
                cv2.imshow("ZED | Hand Detection with 3D Coordinates", img)

                # Increment frame count
                frame_count += 1

            # Break on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nInterrupted by user.")

    finally:
        hands.close()
        cv2.destroyAllWindows()
        zed.close()
        print("Resources released. Coordinates saved to:", log_file)

if __name__ == "__main__":
    track_and_log()
