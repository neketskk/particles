#!/bin/bash
RENDER_ID=1

DIST=lognormal
LOC=0.5
SHAPE=0.7
N=40

# create a directory for this distribution
CLASS=${DIST}-loc${LOC}-shape${SHAPE}
mkdir -p ${CLASS}

mkdir -p ${CLASS}/particles
PARTICLESPATH=${CLASS}/particles/particles${RENDER_ID}.json

mkdir -p ${CLASS}/renders
RENDERPATH=/C:/Desktop/Diplom/DeCost-Holm_Data-in-Brief/${CLASS}/renders/particles${RENDER_ID}.png

for i in $(seq 1 10000); do
    PARTICLESPATH=${CLASS}/particles/particles${i}.json
    RENDERPATH=/C:/Desktop/Diplom/DeCost-Holm_Data-in-Brief/${CLASS}/renders/particles${i}.png
# sample ground truth particle sizes from the given distribution
    python generate_sample.py -n ${N} --textfile ${PARTICLESPATH} --distribution ${DIST} --loc ${LOC} --shape ${SHAPE}
    PARTICLESPATH=${PARTICLESPATH} RENDERPATH=${RENDERPATH} blender -b --python blender_powder.py
done

# render powder image using blender
# blender script takes 'arguments' as environment variables (limitation of blender's python interface)

#PARTICLESPATH=${PARTICLESPATH} RENDERPATH=${RENDERPATH} blender -b --python blender_powder.py
