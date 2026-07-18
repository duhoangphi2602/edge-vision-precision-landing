#!/bin/bash
set -e

SEQ_DIR="../edge-ai-training/datasets/raw/visdrone/v2019_mot_val/VisDrone2019-MOT-val/sequences/uav0000086_00000_v"
IN_DIR="data/input"
OUT_DIR="data/output"
mkdir -p $IN_DIR $OUT_DIR

echo "1. Sinh ra cac video bi rung tu anh goc VisDrone..."
python3 scripts/generate_shaky_videos.py --seq $SEQ_DIR --outdir $IN_DIR

echo "seq_id,avg_jitter_original,avg_jitter_stabilized,lock_rate" > $OUT_DIR/comparison.csv

for level in original low med high; do
   echo "=========================================="
   echo "2. Phan tich video goc (Rung lac cap do: $level)"
   
   RES1=$(python3 src/stabilizer_analyzer.py --input $IN_DIR/seq_${level}.mp4 --outdir $OUT_DIR/seq_${level})
   JITTER_ORIGINAL=$(echo "$RES1" | grep -oP 'Average Trajectory Jitter: \K[0-9.]+')
   
   echo "3. Phan tich lai video DA CHONG RUNG de xem con rung bao nhieu..."
   RES2=$(python3 src/stabilizer_analyzer.py --input $OUT_DIR/seq_${level}/stabilized.mp4 --outdir $OUT_DIR/seq_${level}/re_eval)
   JITTER_STAB=$(echo "$RES2" | grep -oP 'Average Trajectory Jitter: \K[0-9.]+')
   
   echo "seq_${level},$JITTER_ORIGINAL,$JITTER_STAB,PENDING_VALIDATION" >> $OUT_DIR/comparison.csv
   
   echo "4. Chay YOLO Tracking tren video GOC ($level)..."
   python3 scripts/track_and_annotate.py --input $IN_DIR/seq_${level}.mp4 --output $OUT_DIR/seq_${level}/tracking_original.mp4
   
   echo "5. Chay YOLO Tracking tren video DA CHONG RUNG ($level)..."
   python3 scripts/track_and_annotate.py --input $OUT_DIR/seq_${level}/stabilized.mp4 --output $OUT_DIR/seq_${level}/tracking_stabilized.mp4
done

echo "Batch evaluation complete. Results saved to $OUT_DIR/comparison.csv"
