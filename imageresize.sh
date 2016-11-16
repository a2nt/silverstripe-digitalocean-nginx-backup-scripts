#!/bin/sh

#
# Resizes all images in current directory to max size 1900x1200
#

#echo "Resizing images to 1900x1200"


#for line in $(find . -iname '*.png'); do
#    echo "Resizing: $line"
#    mogrify -resize 1900x1200 -depth 8 -filter Triangle -define filter:support=2 -unsharp 0.25x0.08+8.3+0.045 -dither None -posterize 136 -quality 95 -define jpeg:fancy-upsampling=off -define png:compression-filter=5 -define png:compression-level=9 -define png:compression-strategy=1 -define png:exclude-chunk=all -interlace none -strip "$line"
#done

#for line in $(find . -iname '*.jpg'); do
#    echo "Resizing: $line"
#    mogrify -resize 1900x1200 -depth 8 -filter Triangle -define filter:support=2 -unsharp 0.25x0.08+8.3+0.045 -dither None -posterize 136 -quality 95 -define jpeg:fancy-upsampling=off -define png:compression-filter=5 -define png:compression-level=9 -define png:compression-strategy=1 -define png:exclude-chunk=all -interlace none -strip "$line"
#done

#for line in $(find . -iname '*.jpeg'); do
#    echo "Resizing: $line"
#    mogrify -resize 1900x1200 -depth 8 -filter Triangle -define filter:support=2 -unsharp 0.25x0.08+8.3+0.045 -dither None -posterize 136 -quality 95 -define jpeg:fancy-upsampling=off -define png:compression-filter=5 -define png:compression-level=9 -define png:compression-strategy=1 -define png:exclude-chunk=all -interlace none -strip "$line"
#done

#find . -name "*.png~" -delete
#find . -name "*.jpg~" -delete
#find . -name "*.jpeg~" -delete


#
# Optimize Images
#

find . -name "*.jpg" | xargs jpegoptim -vf
find . -name "*.JPG" | xargs jpegoptim -vf
find . -name "*.jpeg" | xargs jpegoptim -vf
find . -name "*.JPEG" | xargs jpegoptim -vf

find . -name "*.png" | xargs pngquant -v -f --ext .png
find . -name "*.PNG" | xargs pngquant -v -f --ext .PNG