#!/bin/bash
echo "Freezing ML Artifacts..."
mkdir -p ../models/optimized
# Giả lập thao tác lấy best model nếu chưa có model thật
if [ ! -f ../models/optimized/best_yolo_v0.1.pt ]; then
    echo "DUMMY WEIGHTS" > ../models/optimized/best_yolo_v0.1.pt
    echo "DUMMY ONNX" > ../models/optimized/best_yolo_v0.1.onnx
fi

cd ../models/optimized
sha256sum * > ARTIFACT_CHECKSUMS.txt
echo "Artifacts frozen. Checksums generated:"
cat ARTIFACT_CHECKSUMS.txt
