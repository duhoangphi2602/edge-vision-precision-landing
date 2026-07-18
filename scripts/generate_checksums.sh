#!/bin/bash
cd "$(dirname "$0")/../releases/v1.0"
echo "Generating checksums..."
find . -type f -not -name "checksums.txt" -exec md5sum {} \; > checksums.txt
echo "Checksums generated successfully."
