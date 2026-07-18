import argparse
import imageio_ffmpeg as ffmpeg
import subprocess
import sys
import os

def parse_args():
    parser = argparse.ArgumentParser(description="Generate a human-viewable H.264 copy of a video.")
    parser.add_argument('--input', required=True, help="Path to input video file")
    parser.add_argument('--output', help="Path to output video file. Defaults to replacing .mp4 with _viewable.mp4")
    parser.add_argument('--codec', default='libx264', help="Video codec to use (default: libx264)")
    parser.add_argument('--pixel-format', default='yuv420p', help="Pixel format (default: yuv420p)")
    parser.add_argument('--crf', default='23', help="Constant Rate Factor (default: 23)")
    parser.add_argument('--preset', default='fast', help="Encoding preset (default: fast)")
    parser.add_argument('--overwrite', action='store_true', help="Overwrite output file if it exists")
    
    # Mutually exclusive group for export-viewable
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--export-viewable', action='store_true', help="Perform the export")
    group.add_argument('--no-export-viewable', action='store_false', dest='export_viewable', help="Do not perform the export (exit gracefully)")
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    if not args.export_viewable:
        print("Export viewable flag is false. Exiting without conversion.")
        sys.exit(0)
        
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist.")
        sys.exit(1)
        
    output_path = args.output
    if not output_path:
        output_path = args.input.replace('.mp4', '_viewable.mp4')
        if output_path == args.input:
            output_path += ".viewable.mp4"
            
    if os.path.exists(output_path) and not args.overwrite:
        print(f"Error: Output file {output_path} already exists. Use --overwrite to overwrite.")
        sys.exit(1)
        
    ffmpeg_exe = ffmpeg.get_ffmpeg_exe()
    
    cmd = [
        ffmpeg_exe,
        '-y' if args.overwrite else '-n',
        '-i', args.input,
        '-c:v', args.codec,
        '-pix_fmt', args.pixel_format,
        '-crf', str(args.crf),
        '-preset', args.preset,
        output_path
    ]
    
    print(f"Running ffmpeg conversion: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(f"Successfully exported viewable video to {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg conversion failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
