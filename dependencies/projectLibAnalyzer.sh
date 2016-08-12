#!/usr/bin/env bash

usage() { echo "Usage: $0 [-p path to python project] [-d name of file for results]" 1>&2; exit 1; }

while getopts ":p:d:" o; do
    case "${o}" in
        p)
            p=${OPTARG}
            ;;
        d)
            d=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done

if [ -z "${p}" ] || [ -z "${d}" ]; then
    usage
fi

r=$(pwd)/"raw"$d
d=$(pwd)/$d
#r="/home/adelina/cern/analysis/raw"$d
#d="/home/adelina/cern/analysis/"$d

echo "Searching for modules in project: " $p
sfood-imports $p > $r
echo "Raw project modules are saved in: " $r
cat $r | grep -v lib/python2.7 | cut -d':' -f3 |cut -d'.' -f1| sort -u > $d
echo "Analyzing modules..."
python3 projectLibAnalyzer.py -p $d