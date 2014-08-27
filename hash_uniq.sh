#!/bin/bash

if [[ -z $1 ]] || [[ -z $2 ]];then
    echo "usage: ./hash_uniq.sh input_file output_file"
    exit 1
fi

./hash_split.py $1 100 _part_

echo $?

for file in $1_part_*
do
    echo "$file"
    {
        sort -u $file > sort_$file
    }&
done

wait

sort -m sort_* > $2

rm -f *_part_*
rm -f sort_*

