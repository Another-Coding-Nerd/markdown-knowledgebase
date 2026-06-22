#!/bin/bash

for file in *.txt; do
  if [ -f "$file" ]; then
    fmt -w 100 "$file" > "$file.tmp" && mv "$file.tmp" "$file"
  fi
done
