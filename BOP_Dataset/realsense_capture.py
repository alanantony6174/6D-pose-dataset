import pyrealsense2 as rs
import numpy as np
import cv2
import os
import json

# --- Configuration ---
# IMPORTANT: Update these paths/values for your setup
DATASET_PATH = "6D_Dataset" # Base path to your dataset
SPLIT_NAME = "train"                              # 'train', 'val', 'test', etc.
SCENE_NUM = 1                                   # The scene number you are currently capturing

# Output directories based on configuration
scene_dir = os.path.join(DATASET_PATH, SPLIT_NAME, f"{SCENE_NUM:06d}")
rgb_dir = os.path.join(scene_dir, "rgb")
depth_dir = os.path.join(scene_dir, "depth")

# Ensure directories exist
os.makedirs(rgb_dir, exist_ok=True)
os.makedirs(depth_dir, exist_ok=True)
print(f"Saving data to: {scene_dir}")

# --- RealSense Setup ---
pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting specific configurations
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))
print(f"Connecting to: {device_product_line}")

# Configure streams (adjust resolution/fps as needed, check available modes first)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30) # BGR8 for direct OpenCV saving

# --- Start Streaming ---
profile = pipeline.start(config)
print("Streaming started.")

# --- Get Camera Intrinsics and Depth Scale ---
# Intrinsics are based on the *color* stream profile because we align depth TO color
color_profile = profile.get_stream(rs.stream.color)
color_intrinsics = color_profile.as_video_stream_profile().get_intrinsics()

# Camera matrix (K) in the required format [fx, 0, cx, 0, fy, cy, 0, 0, 1]
cam_K = [color_intrinsics.fx, 0, color_intrinsics.ppx,
         0, color_intrinsics.fy, color_intrinsics.ppy,
         0, 0, 1]
print(f"Camera Intrinsics (K): {cam_K}")

# Get the depth sensor's scale (converts raw depth pixel values to *meters*)
depth_sensor = profile.get_device().first_depth_sensor()
sdk_depth_scale = depth_sensor.get_depth_scale()
print(f"RealSense SDK Depth Scale: {sdk_depth_scale} (meters per unit)")

# CRITICAL: Calculate the depth scale required by the annotation tool (mm per unit)
# Annotation tool expects: raw_depth_pixel * json_depth_scale = depth_in_mm
# RealSense provides: raw_depth_pixel * sdk_depth_scale = depth_in_meters
# Therefore: json_depth_scale = sdk_depth_scale * 1000.0
json_depth_scale = sdk_depth_scale * 1000.0
print(f"Depth Scale for scene_camera.json: {json_depth_scale} (mm per unit)")


# --- Alignment ---
# Create an align object.
# rs.align allows us to perform alignment of depth frames to others frames' viewpoint (e.g., color)
align_to = rs.stream.color
align = rs.align(align_to)
print("Depth frames will be aligned to color frames.")

# --- Capture Loop ---
frame_count = 0
scene_camera_data = {} # Dictionary to store camera info for each captured frame

print("\n--- Ready to Capture ---")
print(" Press [SPACE] to capture and save the current frame.")
print(" Press [ESC] to quit.")

try:
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()

        # Align the depth frame to color frame
        aligned_frames = align.process(frames)

        # Get aligned frames
        aligned_depth_frame = aligned_frames.get_depth_frame() # aligned_depth_frame is a 640x480 depth image
        color_frame = aligned_frames.get_color_frame()

        # Validate that both frames are valid
        if not aligned_depth_frame or not color_frame:
            print("Frames missing, skipping...")
            continue

        # Convert images to numpy arrays suitable for OpenCV
        depth_image = np.asanyarray(aligned_depth_frame.get_data()) # Raw uint16 depth values
        color_image = np.asanyarray(color_frame.get_data()) # BGR image

        # --- Visualization (Optional, but helpful) ---
        # Apply colormap on depth image for display
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        # Stack images horizontally
        images_display = np.hstack((color_image, depth_colormap))
        # Show images
        cv2.namedWindow('Live RGB | Depth Colormap', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Live RGB | Depth Colormap', images_display)
        # --- End Visualization ---

        key = cv2.waitKey(1) # Check for key press

        # --- Frame Saving Logic ---
        if key == ord(' '): # SPACE bar pressed
            img_id_str = f"{frame_count:06d}" # Format as 000000, 000001, ...
            rgb_filename = os.path.join(rgb_dir, img_id_str + ".png")
            depth_filename = os.path.join(depth_dir, img_id_str + ".png")

            # Save RGB image using OpenCV
            cv2.imwrite(rgb_filename, color_image)

            # Save Depth image using OpenCV
            # IMPORTANT: Save the raw 16-bit depth values directly.
            cv2.imwrite(depth_filename, depth_image.astype(np.uint16))

            print(f"Saved Frame {frame_count}: {rgb_filename} and {depth_filename}")

            # Store camera info for this specific frame in the dictionary
            scene_camera_data[str(frame_count)] = {
                 "cam_K": cam_K,
                 "depth_scale": json_depth_scale # Use the calculated scale for mm
            }

            frame_count += 1 # Increment frame counter ONLY when saved

        elif key == 27: # ESC key pressed
            print("ESC pressed, exiting capture loop...")
            break

finally:
    # --- Stop streaming and save camera info ---
    pipeline.stop()
    print("Streaming stopped.")
    cv2.destroyAllWindows() # Close visualization window

    # Save the scene_camera.json file containing info for all captured frames
    camera_info_path = os.path.join(scene_dir, "scene_camera.json")
    if scene_camera_data: # Only save if at least one frame was captured
        with open(camera_info_path, 'w') as f:
            # Use indent for pretty printing the JSON file
            json.dump(scene_camera_data, f, indent=4)
        print(f"Saved camera info for {frame_count} frames to: {camera_info_path}")
    else:
        print("No frames were captured, scene_camera.json not saved.")

print(f"\nCapture process for Scene {SCENE_NUM} finished.")