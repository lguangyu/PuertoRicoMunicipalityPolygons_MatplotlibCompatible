#!/bin/bash

mkdir -p .process

# first, parse the svg into json
./script/parse_svg.py \
	-o .process/polygon.json \
	proto/Locator-map-Puerto-Rico-Aguadilla.svg

# second, visualize the polygons
./script/plot_parsed_json.py \
	-p .process/polygon.png \
	.process/polygon.json

# now it's time to do manual work. use the visualized image to identify
# the municipality of each polygon id
# the result should be a 2-column, tab-delimited table, with the 1-st column
# listing all polygon ids and the second for the corresponding municipalities
# for example:
#polygon3133_1_	adjuntas	Adjuntas
#polygon3135_1_	aguada	Aguada
#polygon3137_1_	aguadilla	Aguadilla
#polygon3139_1_	aguas_buenas	Aguas Buenas
#polygon3141_1_	aibonito	Aibonito
#...

# finally rearrange the polygons by municipality
# in this example the manually refined 2-column table from above step is
# .process/polygon_municip_translation_table.tsv
./script/rearrange_by_municipality.py \
	-o puerto_rico_municipality.json \
	-T .process/polygon_municip_translation_table.tsv \
	.process/polygon.json

# visualize it
./plot_example.py
