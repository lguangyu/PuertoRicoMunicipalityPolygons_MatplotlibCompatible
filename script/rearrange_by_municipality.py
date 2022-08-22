#!/usr/bin/env python3

import argparse
import collections
import io
import json
import numpy
import sys


def get_args(argv = None):
	ap = argparse.ArgumentParser()
	ap.add_argument("input", type = str, nargs = "?", default = "-",
		help = "input json file parsed from svg (default: stdin)")
	ap.add_argument("-o", "--output", type = str, default = "-",
		metavar = "json",
		help = "output json file (default: stdout)")
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
	if args.output == "-":
		args.output = sys.stdout
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
				ret[k] = v
	return ret


def polygon_area(xys):
	x, y = numpy.asarray(xys).T
	area = 0.5 * numpy.abs(
		numpy.dot(x, numpy.roll(y, 1)) - numpy.dot(y, numpy.roll(x, 1))
	)
	return area


def save_municipality_rearranged_json(f, polygons, trans_table):
	o = dict(metadata = dict(extend = polygons["extend"]))
	o["municipality"] = dict()
	for k, v in polygons["polygons"].items():
		if k not in trans_table:
			municip_ascii, municip_full = k, k
		elif len(trans_table[k]) == 1:
			municip_ascii = trans_table[k][0]
			municip_full = municip_ascii
		else:
			municip_ascii, municip_full = trans_table[k][:2]

		if municip_ascii not in o["municipality"]:
			o["municipality"][municip_ascii] = dict(displayname = municip_full,
				polygon = list())
		o["municipality"][municip_ascii]["polygon"].append(v)
	# sort each municipality polygo by descending area
	for v in o["municipality"].values():
		v["polygon"].sort(key = polygon_area, reverse = True)
	# save json
	with open(f, "w") as fp:
		json.dump(o, fp, sort_keys = True)
	return 


def main():
	args = get_args()
	polygons = load_json(args.input)
	trans_table = read_translation_table(args.polygon_id_translation_table)
	save_municipality_rearranged_json(args.output, polygons, trans_table)
	return


if __name__ == "__main__":
	main()

