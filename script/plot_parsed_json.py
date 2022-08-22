#!/usr/bin/env python3

import argparse
import io
import json
import math
import matplotlib
import matplotlib.patches
import matplotlib.pyplot
import numpy
import sys


class PosInt(int):
	def __new__(cls, *ka, **kw):
		new = super().__new__(cls, *ka, **kw)
		if new <= 0:
			raise ValueError("PosInt must be positive")
		return new


def get_args(argv = None):
	ap = argparse.ArgumentParser()
	ap.add_argument("input", type = str, nargs = "?", default = "-",
		help = "input json file parsed from svg (default: stdin)")
	ap.add_argument("-p", "--plot", type = str, default = "-",
		metavar = "png",
		help = "output image (default: stdout)")
	ap.add_argument("--dpi", type = PosInt, default = 300,
		metavar = "int",
		help = "dpi of output image (default: 300)")
	ap.add_argument("-T", "--polygon-id-translation-table", type = str,
		metavar = "tsv",
		help = "3-column tsv to map polygon id in <input> into human-"
			"recognizable names if provided; the 2nd column is intended for "
			"programming uses which is recommended to use ascii only without "
			"special characters; the 3rd column is intended for display at the "
			"front-end")

	# parse and refine args
	args = ap.parse_args(argv)
	if args.input == "-":
		args.input = sys.stdin
	if args.plot == "-":
		args.plot = sys.stdout.buffer
	return args


def get_fp(f, *ka, factory = open, **kw):
	if isinstance(f, io.IOBase):
		ret = f
	elif isinstance(f, str):
		ret = factory(f, *ka, **kw)
	else:
		raise TypeError("first argument must be type str or valid file handle, "
			"got '%s'" % type(f).__name__)
	return ret


def load_json(f):
	with get_fp(f, "r") as fp:
		ret = json.load(fp)
	return ret


def read_translation_table(f) -> dict:
	ret = dict()
	if f:
		with get_fp(f, "r") as fp:
			for line in fp:
				k, *v = line.rstrip("\r\n").split("\t")
				if (not v) or (not v[0]):
					continue
				ret[k] = v[-1] # use the last one
	return ret


def setup_layout(extend) -> dict:
	fig_width	= extend["width"]
	fig_height	= extend["height"]
	fig_diag	= math.sqrt(fig_width ** 2 + fig_height ** 2)

	fig_diag_inch	= 12
	fig_width_inch	= fig_width / fig_diag * fig_diag_inch
	fig_height_inch	= fig_height / fig_diag * fig_diag_inch

	layout = dict()

	# create figure
	figure = matplotlib.figure.Figure()
	figure.set_size_inches(fig_width_inch, fig_height_inch)
	layout["figure"] = figure

	# create axes
	axes = figure.add_axes([0, 0, 1, 1])
	layout["axes"] = axes

	# apply axes style
	axes = layout["axes"]
	for sp in axes.spines.values():
		sp.set_visible(False)
	axes.tick_params(
		left	= False, labelleft = False,
		right	= False, labelright = False,
		bottom	= False, labelbottom = False,
		top		= False, labeltop = False,
	)

	return layout


def plot(png, data, dpi = 300, trans_table = None):
	extend = data["extend"]
	if trans_table is None:
		trans_table = dict()

	layout = setup_layout(extend)
	figure = layout["figure"]

	# plot polygons
	axes = layout["axes"]
	for k, p in data["polygons"].items():
		patch = matplotlib.patches.Polygon(p, clip_on = False, linestyle = "-",
			linewidth = 1.0, edgecolor = "#a0a0a0", facecolor = "#d0d0d0",
			zorder = 2)
		axes.add_patch(patch)
		# add text label for manual refine
		xy = (numpy.max(p, axis = 0) + numpy.min(p, axis = 0)) / 2
		axes.text(*xy, trans_table.get(k, k), fontsize = 4,
			horizontalalignment = "center", verticalalignment = "center")

	# misc
	axes.set_xlim(extend["x"], extend["x"] + extend["width"])
	axes.set_ylim(extend["y"], extend["y"] + extend["height"])

	# save fig and clean up
	figure.savefig(png, dpi = dpi)
	matplotlib.pyplot.close()
	return


def main():
	args = get_args()
	data = load_json(args.input)
	trans_table = read_translation_table(args.polygon_id_translation_table)
	plot(args.plot, data, dpi = args.dpi, trans_table = trans_table)
	return


if __name__ == "__main__":
	main()

