#!/usr/bin/env python3

import json
import matplotlib
import matplotlib.figure
import matplotlib.patches
import matplotlib.pyplot
import numpy
import sys


# read data from the json
with open("./puerto_rico_municipality.json", "r") as fp:
	data = json.load(fp)
extent = data["metadata"]["extent"]
municipality = data["municipality"]


# draw a figure with exact aspect ratio we want
figure = matplotlib.figure.Figure()
fig_width_inch = 8
fig_height_inch = fig_width_inch / extent["width"]\
	* extent["height"]
figure.set_size_inches(fig_width_inch, fig_height_inch)

# add an axes that fills the entire figure canvas without showing axes
axes = figure.add_axes([0.0, 0.0, 1.0, 1.0])
for sp in axes.spines.values():
	sp.set_visible(False)
axes.tick_params(
	left	= False, labelleft = False,
	right	= False, labelright = False,
	bottom	= False, labelbottom = False,
	top		= False, labeltop = False,
)

# draw each municipality
for k, v in municipality.items():
	# plot municipality polygon(s)
	poly = v["polygon"]
	for xys in poly: # each municipality may have more than one polygon
		p = matplotlib.patches.Polygon(xys, linestyle = "-", linewidth = 1.0,
			edgecolor = "#a0a0a0", facecolor = "#d0d0d0")
		axes.add_patch(p)

	# add a label to each municipality
	# we use v[0] as the "main polygon" for each municipality since they have
	# been sorted by area in descending order in puerto_rico_municipality.json
	xy = (numpy.min(poly[0], axis = 0) + numpy.max(poly[0], axis = 0)) / 2
	axes.text(*xy, v["displayname"], fontsize = 6,
		horizontalalignment = "center", verticalalignment = "center")

# set the axes extent so we can see the map
axes.set_xlim(extent["x"], extent["x"] + extent["width"])
axes.set_ylim(extent["y"], extent["y"] + extent["height"])

# save figure
figure.savefig("example.png", dpi = 300)
matplotlib.pyplot.close()

