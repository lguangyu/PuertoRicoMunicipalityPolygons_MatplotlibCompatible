#!/usr/bin/env python3

import argparse
import io
import json
import re
import sys
import xml.etree.ElementTree
import svgpath2mpl


def get_args(argv = None):
	ap = argparse.ArgumentParser()
	ap.add_argument("input", type = str, nargs = "?", default = "-",
		help = "input svg vector xml (default: stdin)")
	ap.add_argument("-o", "--output", type = str, default = "-",
		metavar = "json",
		help = "output json file (default: stdout)")
	ap.add_argument("--no-flip-vertical", action = "store_true",
		help = "do not flip vertical coordinates (default: off)")

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


class SimpleSVG(object):
	def __init__(self, svg_xml, *ka, **kw):
		super().__init__(*ka, **kw)
		self.svg_xml = svg_xml
		return

	@classmethod
	def from_file(cls, f):
		with get_fp(f, "r") as fp:
			svg_xml = xml.etree.ElementTree.parse(fp)
		new = cls(svg_xml)
		return new

	def get_svg_node(self):
		# return the svg root node and namespace
		for node in self.svg_xml.iter():
			m = re.match("({.*})?svg", node.tag)
			if m:
				namespace = m.group(1).strip("{}")
				break
		else:
			raise ValueError("no svg node found in provided xml")
		return node, namespace

	def get_svg_extend(self) -> dict:
		svg, namespace = self.get_svg_node()
		viewbox = [float(i) for i in svg.attrib["viewBox"].split(" ")]
		ret = dict(
			x		= viewbox[0],
			y		= viewbox[1],
			width	= viewbox[2],
			height	= viewbox[3],
		)
		return ret

	def get_svg_polygons(self, include_path = False) -> dict:
		svg, namespace = self.get_svg_node()
		ret = dict()
		for node in svg.findall("polygon", namespaces = { "": namespace }):
			p = [[float(v) for v in xy.split(",")]\
				for xy in node.attrib["points"].split(" ") if xy]
			ret[node.attrib["id"]] = p
		if include_path:
			for node in svg.findall("path", namespaces = { "": namespace }):
				p = svgpath2mpl.parse_path(node.attrib["d"])
				ret[node.attrib["id"]] = p.vertices.tolist()
		return ret

	def save_extend_and_polygon_json(self, f, flip_vertical = True, **kw):
		data = dict(
			extend = self.get_svg_extend(),
			polygons = self.get_svg_polygons(include_path = True),
		)
		if flip_vertical:
			h = data["extend"]["height"]
			# flip extend
			y = data["extend"]["y"]
			data["extend"]["y"] = 0
			for k, p in data["polygons"].items():
				for xy in p:
					xy[1] = h + y - xy[1]

		with get_fp(f, "w") as fp:
			json.dump(data, fp, sort_keys = True)
		return


def main():
	args = get_args()
	svg = SimpleSVG.from_file(args.input)
	svg.save_extend_and_polygon_json(args.output,
		flip_vertical = not args.no_flip_vertical)
	return


if __name__ == "__main__":
	main()

