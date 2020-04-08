#!/bin/bash

WINDOW_SIZES=(2 5 10 15)
TESTS=('concreteness' 'valence' 'imageability' 'body_object_interaction')

for size in ${WINDOW_SIZES[@]};
do
    for test_kind in ${TESTS[@]};
    do
        python investigate.py --test ${test_kind} --window_size ${size} &
    done
done
