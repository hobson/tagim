#!/usr/bin/env bash
# reformat the Kaggle hospital prediction data tables

FN="$1"
OFN="$1.tsv"
cp -f "$FN" "$OFN"
sed -i -r -e 's/([01]?[0-9]+)-\s*([01]?[0-9]+) month[s]?/\1\t\2/g' "$OFN"
sed -i -r -e 's/,/\t/g' "${OFN}"
sed -i -r -e 's/\t7[+]/\t10/g' "$OFN"
sed -i -r -e 's/\tY([1234])/\t\1\t/g' "$OFN"
echo "$OFN"
