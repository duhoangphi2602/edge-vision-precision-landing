import argparse
import os
import time
import yaml
import json
import subprocess
import sys

def add_standard_args(parser: argparse.ArgumentParser):
    parser.add_argument('--input', type=str, help='Input canonical video path')
    parser.add_argument('--config', type=str, help='Path to YAML configuration')
    parser.add_argument('--output-root', type=str, default='runs', help='Root directory for output runs')
    parser.add_argument('--run-id', type=str, help='Optional run ID. If not provided, timestamp is used.')
    parser.add_argument('--max-frames', type=int, default=0, help='Max frames to process (0 = all if not --duration-sec)')
    parser.add_argument('--duration-sec', type=float, default=0.0, help='Max duration to process in seconds')
    parser.add_argument('--process-full-video', action='store_true', help='Force processing full video (overrides max-frames/duration-sec)')
    parser.add_argument('--export-viewable', action='store_true', help='Export H.264 viewable copy at the end')
    parser.add_argument('--overwrite', action='store_true', help='Allow overwriting existing run directory')
    return parser

def create_run_dir(args, mission_id: str):
    run_id = args.run_id if args.run_id else time.strftime("%Y%m%d_%H%M%S")
    if os.path.basename(args.output_root.rstrip("/")) == mission_id or os.path.basename(os.path.dirname(args.output_root.rstrip("/"))) == mission_id:
        run_dir = os.path.join(args.output_root, run_id)
    else:
        run_dir = os.path.join(args.output_root, mission_id, run_id)
    
    if os.path.exists(run_dir) and not args.overwrite:
        print(f"Error: Run directory {run_dir} already exists. Use --overwrite.", file=sys.stderr)
        sys.exit(1)
        
    os.makedirs(run_dir, exist_ok=True)
    return run_dir, run_id

def save_run_metadata(run_dir: str, args, config_data: dict, command: str, env_vars: dict = None):
    # Save resolved config
    if config_data is not None:
        with open(os.path.join(run_dir, 'resolved_config.yaml'), 'w') as f:
            yaml.dump(config_data, f)
            
    # Save command
    with open(os.path.join(run_dir, 'command.txt'), 'w') as f:
        f.write(command + '\n')
        
    # Save environment
    with open(os.path.join(run_dir, 'environment.txt'), 'w') as f:
        f.write(json.dumps(env_vars or {}, indent=2))

def get_frame_limit(args, fps: float):
    if args.process_full_video:
        return float('inf')
    if args.max_frames > 0:
        return args.max_frames
    if args.duration_sec > 0:
        return int(args.duration_sec * fps)
    return float('inf') # Default to full if nothing specified

def export_viewable_copy(raw_mp4_path: str):
    script_path = os.path.join(os.path.dirname(__file__), '../../../tools/video/create_viewable_copy.py')
    cmd = ['python3', script_path, '--input', raw_mp4_path, '--export-viewable']
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to export viewable copy for {raw_mp4_path}: {e}")
