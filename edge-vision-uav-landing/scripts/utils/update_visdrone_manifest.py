import os, glob
from ruamel.yaml import YAML

manifest_path = 'assets/videos/manifests/VIDEO_ASSET_MANIFEST.yaml'
yaml = YAML()
yaml.preserve_quotes = True

with open(manifest_path, 'r') as f:
    manifest = yaml.load(f)

# Thêm base asset
if not any(a.get('asset_id') == 'visdrone_uav0000137_00458_v' for a in manifest['assets']):
    manifest['assets'].append({
        'asset_id': 'visdrone_uav0000137_00458_v',
        'mission_ids': ['P1-B'],
        'role': 'real_world_base',
        'path': 'edge-ai-training/datasets/raw/visdrone/v2019_mot_val/VisDrone2019-MOT-val/sequences/uav0000137_00458_v',
        'source': 'VisDrone2019-MOT-val',
        'type': 'base',
        'status': 'active'
    })

faults_dir = 'edge-ai-training/datasets/processed/derived_faults/sequences'
for fault_folder in glob.glob(os.path.join(faults_dir, "uav0000137_00458_v_*")):
    fault_name = os.path.basename(fault_folder).replace("uav0000137_00458_v_", "")
    derived_id = f"visdrone_{fault_name}"
    
    if 'derived_assets' not in manifest:
        manifest['derived_assets'] = {}
        
    if derived_id not in manifest['derived_assets']:
        manifest['derived_assets'][derived_id] = {
            'filename': os.path.basename(fault_folder),
            'format': 'image_sequence',
            'mission_id': 'P1-B',
            'parent_asset': 'visdrone_uav0000137_00458_v',
            'fault_type': fault_name,
            'status': 'active'
        }

with open(manifest_path, 'w') as f:
    yaml.dump(manifest, f)

print("Đã đăng ký VisDrone vào VIDEO_ASSET_MANIFEST.yaml thành công!")
