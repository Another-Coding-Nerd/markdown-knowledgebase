#!/bin/bash

# Remove input files already present in processed/.
# Handles both whole files and fmt_text.sh-split part files (basename-part-NNN.txt).
# A file is a duplicate if:
#   - processed/<file> exists (exact match), OR
#   - it's a part file and processed/<basename>.txt exists (processed before splitting), OR
#   - it's a part file and processed/<basename>-part-001.txt exists (processed as parts)

for file in *.txt; do
    [ -f "$file" ] || continue

    # Check exact match first
    if [ -f "processed/$file" ]; then
        echo "Removing duplicate: $file"
        rm "$file"
        continue
    fi

    # Check if this is a part file
    if [[ "$file" == *-part-[0-9][0-9][0-9].txt ]]; then
        basename="${file%%-part-*}"
        if [ -f "processed/${basename}.txt" ] || [ -f "processed/${basename}-part-001.txt" ]; then
            echo "Removing duplicate part: $file"
            rm "$file"
        fi
    fi
done
