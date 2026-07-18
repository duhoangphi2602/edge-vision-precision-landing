#!/usr/bin/env python3
import os
import subprocess
import csv

def test_pipeline():
    print("Testing parser...")
    parsed_csv = "edge-vision-uav-landing/tests/fixtures/visdrone_mot_sample/parsed.csv"
    subprocess.run(["python3", "edge-vision-uav-landing/scripts/data_prep/visdrone_mot_parser.py", "--input", "edge-vision-uav-landing/tests/fixtures/visdrone_mot_sample/sample_annotation.txt", "--output", parsed_csv], check=True)
    
    print("Testing target selection...")
    target_csv = "edge-vision-uav-landing/tests/fixtures/visdrone_mot_sample/target.csv"
    subprocess.run(["python3", "edge-vision-uav-landing/scripts/data_prep/select_tracking_target.py", "--input", parsed_csv, "--output", target_csv], check=True)
    
    # Check output
    with open(target_csv, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    assert len(rows) == 3, f"Expected 3 rows, got {len(rows)}"
    for r in rows:
        assert int(r['target_id']) == 2, "Expected target_id 2 (nearest to center)"
        
    print("ALL TESTS PASSED: PIPELINE_VERIFIED_WITH_TEST_FIXTURE")

if __name__ == "__main__":
    test_pipeline()
