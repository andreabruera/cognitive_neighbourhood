#!/bin/bash

WINDOW_SIZES=(2 5 10 15)
#WINDOW_SIZES=(2)

for size in ${WINDOW_SIZES[@]};
do
    python positive_pointwise_mutual_information.py --window_size ${size} &
done
