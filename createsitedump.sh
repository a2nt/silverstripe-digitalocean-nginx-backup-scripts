#!/bin/sh

# Creates MySQL dump
# args:
# $1 sites path
# $2 site name
# $3 mysql username
# $4 mysql password

cd $1
mysqldump -u$3 -p$4 $2 > $2.sql