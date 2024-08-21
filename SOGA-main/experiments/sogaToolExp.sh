#!/bin/sh

for exp in "prune" "branch" "var" "cmp" "par"
do
	$(python3 reproduce.py --exp $exp --smoke)
done