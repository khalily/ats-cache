#!/bin/bash

for x in {1..10}
do
    {
        ./gen_urls2.py all_hosts.txt 2000000 > gen_extra_urls_$x
    }&
done

echo 'gen usls ...'
wait

