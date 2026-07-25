#!/bin/bash

LINES_PER_FILE=100
OVERLAP_LINES=10

for file in *.txt; do
  if [ ! -f "$file" ]; then
    continue
  fi

  # Skip already-split files
  if [[ "$file" == *-part-[0-9][0-9].txt ]]; then
    continue
  fi

  # Check if wrapping is needed
  chars=$(wc -c < "$file")
  lines=$(wc -l < "$file")
  lines=${lines:-0}

  if [ "$lines" -gt 0 ]; then
    avg=$((chars / lines))
  else
    avg=$chars
  fi

  # Reflow if lines are long
  if [ "$avg" -gt 150 ]; then
    fmt -w 100 "$file" > "$file.wrapped"
    working_file="$file.wrapped"
  else
    working_file="$file"
  fi

  total_lines=$(wc -l < "$working_file")

  # If file fits in one segment, reflow in place and move on
  if [ "$total_lines" -le "$LINES_PER_FILE" ]; then
    if [ "$working_file" = "$file.wrapped" ]; then
      mv "$file.wrapped" "$file"
    fi
    continue
  fi

  # Split into overlapping segments
  basename="${file%.txt}"
  line_num=1
  file_count=1
  overlap_buffer=""

  while IFS= read -r line; do
    output_file=$(printf "%s-part-%02d.txt" "$basename" "$file_count")

    if [ ! -f "$output_file" ]; then
      if [ -n "$overlap_buffer" ]; then
        printf '%s\n' "$overlap_buffer" > "$output_file"
      else
        touch "$output_file"
      fi
    fi

    echo "$line" >> "$output_file"

    if [ $((line_num % LINES_PER_FILE)) -eq 0 ] && [ "$line_num" -lt "$total_lines" ]; then
      overlap_buffer=$(tail -n "$OVERLAP_LINES" "$output_file")
      file_count=$((file_count + 1))
    fi

    line_num=$((line_num + 1))
  done < "$working_file"

  # Clean up
  [ -f "$file.wrapped" ] && rm "$file.wrapped"
  rm "$file"
done
