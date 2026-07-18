import yaml

with open('assets/videos/manifests/VIDEO_ASSET_MANIFEST.yaml', 'r') as f:
    manifest = yaml.safe_load(f)

# Update aruco_id0_landing_v1
for asset in manifest['assets']:
    if asset['asset_id'] == 'aruco_id0_landing_v1':
        asset['role'] = 'deterministic_regression_fixture'
        asset['final_demo'] = False
        if 'roles' in asset:
            del asset['roles']
            
# Add missing synthetic_car_tracking
synthetic_car = {
    'asset_id': 'synthetic_car_tracking',
    'mission_ids': ['P1-B'],
    'role': 'deterministic_regression_fixture',
    'final_demo': False,
    'path': 'assets/videos/base/p1b_vehicle_tracking/synthetic_car_tracking.mp4',
    'source': 'Synthetic generation',
    'license': 'Internal/Synthetic',
    'duration': 30.0,
    'fps': 30,
    'resolution': '640x480',
    'codec': 'mp4v',
    'sha256': '59f3706fcb9ce301b788ef38d8130dbeb7f4e3a653bb51fc0003d3de2838f5a6',
    'type': 'base',
    'parent_asset': None,
    'status': 'active'
}
manifest['assets'].append(synthetic_car)

# Add wrong_marker and no_marker
wrong_marker = {
    'asset_id': 'aruco_wrong_marker_v1',
    'mission_ids': ['P1-A'],
    'role': 'deterministic_regression_fixture',
    'final_demo': False,
    'path': 'assets/videos/base/p1a_aruco_landing/aruco_wrong_marker_v1.mp4',
    'source': 'Synthetic generation script (marker_id=1)',
    'license': 'Internal/Synthetic',
    'duration': 30.0,
    'fps': 30,
    'resolution': '640x480',
    'codec': 'mp4v',
    'sha256': 'ea847c6ad1ce244a3e080a4e7aff1b3dfcd66b67537b7a70639853a1cb1b0d3a',
    'type': 'base',
    'parent_asset': None,
    'status': 'active'
}
no_marker = {
    'asset_id': 'aruco_no_marker_v1',
    'mission_ids': ['P1-A'],
    'role': 'deterministic_regression_fixture',
    'final_demo': False,
    'path': 'assets/videos/base/p1a_aruco_landing/aruco_no_marker_v1.mp4',
    'source': 'Synthetic generation script (no marker)',
    'license': 'Internal/Synthetic',
    'duration': 30.0,
    'fps': 30,
    'resolution': '640x480',
    'codec': 'mp4v',
    'sha256': '384e14368120d79c38d81b91fe161be09ac3b9ad4c1f4dd2121d9699fbebfe98',
    'type': 'base',
    'parent_asset': None,
    'status': 'active'
}
manifest['assets'].append(wrong_marker)
manifest['assets'].append(no_marker)

# Update derived_assets status
if 'derived_assets' in manifest:
    for key, val in manifest['derived_assets'].items():
        val['status'] = 'permanently_deleted'
        val['deletion_reason'] = 'legacy_synthetic_faults_cleared_for_real_world_data'

with open('assets/videos/manifests/VIDEO_ASSET_MANIFEST.yaml', 'w') as f:
    yaml.dump(manifest, f, sort_keys=False)
