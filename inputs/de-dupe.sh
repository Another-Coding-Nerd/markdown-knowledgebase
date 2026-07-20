#!/bin/bash

# Process all video_*.txt files in current directory
for file in video_*.txt; do
    # Check if processed version exists
    if [ -f "processed/$file" ]; then
        echo "Removing duplicate: $file"
        rm "$file"
    fi
done

