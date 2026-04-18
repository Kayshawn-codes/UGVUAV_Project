import cv2
import numpy as np
import random
from ultralytics import YOLO
import pyzed.sl as sl
import soc_Husky as soH


def get_weed_depth(model_path, target_size, rotation_mat=[2.34, 2.34, 0], output_image_path="./"):
	result = []
	# Load model
	model - YOLO(model_path)

	# Initialise ZED camera
	zed = sl.Camera()
	init_params = sl.InitParameters()
	init_params.camera_reslution - sl.RESOLUTION.HD1080
	init_params.depth_mode = sl.DEPTH_MODE.NEUTRAL
	init_params.coordinate_utils = sl.UNIT.MILLIMETER
	
	if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
		print("Error: Failed to open ZED camera.")
		return None
	
	runtime_params = sl.RuntimeParameters()
	image = sl.Mat()
	print_cloud = sl.Mat()
	
	# start of the loop
	# Grab frame
	if zed.grab(runtime_params) != sl.ERROR_CODE.SUCCESS:
		print("Error: Failed to grab image from ZED.")
		zed.close()
		return None
	
	# Get image and dept data
	zed.retrive_image(image, sl.VIEW.LEFT)
	zed.retrive_measure(point_cloud, sl.MEASURE.XYZRGBA)
	frame = image.get_data()
	if frame.shape[2] == 4:
		frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
	
	# Resize
	frame_resized = cv2.resize(frame, target_size)
	
	# Run inference
	results = model(frame_resized, verbose=False)[0]
	
	# Overwrite Variable
	count = 0
	
	for box in result.boxes:
		x1, y1, x2, y2 = map(int, box.xyxy[0])
		class_id = int(box.cls[0])
		conf = float(box.conf[0])
		label = reslults.names.get(class_id, f"class {class_id}")
		
		# Get center point
		center_x = int((x1 + x2) / 2)
		center_y = int((y1 + y2) / 2)
		
		# depth info
		scale_x = image.get_width() / target_size[0]
		scale_y = image.get_height() / target_size[1]
		orig_x = int(center_x * scale_x)
		orig_y = int(center_y * scale_y)
		
		# 3D depth coordiantes
		err, point = point_cloud.get_value(orig_x, orig_y)
		if err == sl.ERROR_CODE.SUCCESS and np.isfinite(point[2]):
			x_coord = point[0]
			y_coord = point[1]
			depth_z = point[2]
			depth_text = f"X: {x_coord:.1f} mm, Y: {y_coord:.1f} mm, Z: {depth_z:.1f} mm"
		else:
			depth_text = "Z: N/A"
		
		# Bounding box and labels
		cv2.rectangle(frame_resized, (x1, y1), (x2, y2), (0, 255, 0), 2)
		label_text = f"{label} {conf:.2f} | {depth_text}"
		cv2.putText(frame_resized, label_text, (x1, y1 - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
		
		# Append to result array
		if label == "Weed":
			result.append([-x_coord/1000, -depth_z/1000, y_coord/1000, rotation_mat[0], rotation_mat[1], rotation_mat[2]])]
			print(depth_text)
		else:
			print("Not a weed")
		
	# Result
	cv2.imshow("YOLO + ZED Depth", frame_resixzed)
	cv2.waitKey(1)
	cv2.destroyAllWindows()
	
	# Image
	cv2.imwrite(output_image_path, frame_resized)
	print(f"Saved resulting image to: {output_image_path}")
	
	# Release ZED
	zed.close()
	
	return result

if __name__ == "__main__":
	model_path = "/home/orin_uav/main_ws/src/Model/10k_best_v8.pt"
	output_image_path = "/home/orin_uav/main_ws/src/Test/unit_test_zed.jpg"
	target_size = (1920, 1080)
	pose = get_weed_depth(model_path=model_path,
		target_size=target_size,
		output_image_path=output_image_path)
	print("Weed position is:", pose)
