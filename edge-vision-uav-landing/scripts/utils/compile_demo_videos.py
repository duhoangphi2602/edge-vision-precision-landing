import os
import glob
import imageio

def images_to_video(image_folder, video_name, fps=30):
    images = sorted(glob.glob(os.path.join(image_folder, "*.jpg")))
    if not images:
        return
        
    writer = imageio.get_writer(video_name, fps=fps, macro_block_size=1)
    for img_path in images:
        writer.append_data(imageio.imread(img_path))
    writer.close()

if __name__ == "__main__":
    out_dir = "edge-ai-training/datasets/processed/derived_videos"
    os.makedirs(out_dir, exist_ok=True)
    
    clean_dir = "edge-ai-training/datasets/raw/visdrone/v2019_mot_val/VisDrone2019-MOT-val/sequences/uav0000137_00458_v"
    print("Compiling CLEAN video...")
    images_to_video(clean_dir, os.path.join(out_dir, "clean_visdrone_viewable.mp4"))
    
    faults_dir = "edge-ai-training/datasets/processed/derived_faults"
    for fault_folder in glob.glob(os.path.join(faults_dir, "uav0000137_00458_v_*")):
        fault_name = os.path.basename(fault_folder).replace("uav0000137_00458_v_", "")
        print(f"Compiling {fault_name.upper()} video...")
        images_to_video(fault_folder, os.path.join(out_dir, f"{fault_name}_visdrone_viewable.mp4"))
        
    print(f"Done! All videos compiled in {out_dir}")
