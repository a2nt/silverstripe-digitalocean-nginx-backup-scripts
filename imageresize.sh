#!/bin/sh

#
# Resizes all images in current directory to max size 1900x1200
#

echo "Resizing images to 1900x1200"


for line in $(find . -iname '*.png'); do
    echo "Resizing: $line"
    mogrify -resize 1900x1200 "$line"
done

for line in $(find . -iname '*.jpg'); do
    echo "Resizing: $line"
    mogrify -resize 1900x1200 "$line"
done

for line in $(find . -iname '*.jpeg'); do
    echo "Resizing: $line"
    mogrify -resize 1900x1200 "$line"
done

find . -name "*.png~" -delete
find . -name "*.jpg~" -delete
find . -name "*.jpeg~" -delete