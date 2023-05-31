#!/usr/bin/env python3

"""
AHumanIBelieve's Wizard Tower generator
"""

import sys
from glm import ivec2, ivec3
import numpy as np

from gdpc import __url__, Editor, Block, Box, Transform, geometry
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.transform import rotatedBoxTransform, flippedBoxTransform
from gdpc.vector_tools import Y, addY, dropY, line3D, circle, fittingCylinder
from gdpc.geometry import placeBox, placeCuboid


# The minimum build area size in the XZ-plane for this example.
MIN_BUILD_AREA_SIZE = ivec2(10, 10)
wallPalette = [Block(id) for id in 3*["stone_bricks"] + ["cobblestone", "polished_andesite"]]


# Create an editor object.
# The Editor class provides a high-level interface to interact with the Minecraft world.
editor = Editor(buffering=True)


# Check if the editor can connect to the GDMC HTTP interface.
try:
    editor.checkConnection()
except InterfaceConnectionError:
    print(
        f"Error: Could not connect to the GDMC HTTP interface at {editor.host}!\n"
        "To use GDPC, you need to use a \"backend\" that provides the GDMC HTTP interface.\n"
        "For example, by running Minecraft with the GDMC HTTP mod installed.\n"
        f"See {__url__}/README.md for more information."
    )
    sys.exit(1)


# Get the build area.
try:
    buildArea = editor.getBuildArea()
except BuildAreaNotSetError:
    print(
        "Error: failed to get the build area!\n"
        "Make sure to set the build area with the /setbuildarea command in-game.\n"
        "For example: /setbuildarea 0 0 0 50 319 0"
    )
    sys.exit(1)


# Check if the build area is large enough in the XZ-plane.
if any(dropY(buildArea.size) < MIN_BUILD_AREA_SIZE):
    print(
        "Error: the build area is too small for this example!\n"
        f"It should be at least {tuple(MIN_BUILD_AREA_SIZE)} blocks large in the XZ-plane."
    )
    sys.exit(1)


print("Loading world slice...")
buildRect = buildArea.toRect()
platformRect = buildRect.centeredSubRect((51,50))
placeBox(editor, platformRect.toBox(100,  1), wallPalette)
print("placed floor")
placeBox(editor, platformRect.toBox(101, 100), Block("air")) # Clear some space
print("removed blocking air")
worldSlice = editor.loadWorldSlice(buildRect)
print("World slice loaded!")

geometry.placeRectOutline(editor, buildRect, 100, Block("glwstone"))

print("placed outline")

heightmap = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
meanHeight = np.mean(heightmap)
groundCenter = addY(buildRect.center, meanHeight)



cylinder = fittingCylinder(
    groundCenter + ivec3(-10, 0, -10),
    groundCenter + ivec3( 10, 40, 10),
    tube=True
)
cylinderInside = fittingCylinder(
    groundCenter + ivec3(-9, 0, -9),
    groundCenter + ivec3( 9, 40, 9),
    tube=False
)

editor.placeBlock(cylinder, wallPalette)
editor.placeBlock(cylinderInside, Block("air"))
print("placed tower at")
