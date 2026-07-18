import imageio_ffmpeg
import subprocess
import sys

if len(sys.argv) < 2:
    print("Usage: python3 convert_h264.py <input_video.mp4>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = input_file.replace(".mp4", "_viewable.mp4")

exe = imageio_ffmpeg.get_ffmpeg_exe()
print(f"Converting {input_file} to H.264 format...")
subprocess.run([exe, '-y', '-i', input_file, '-vcodec', 'libx264', '-pix_fmt', 'yuv420p', output_file], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
print(f"Done! You can now view: {output_file}")
