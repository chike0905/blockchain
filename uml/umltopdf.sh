#!/bin/sh
# uml to pdf
plantuml -svg ./${1%.*}.uml && inkscape ./${1%.*}.svg -A ./${1%.*}.pdf
rm ./${1%.*}.svg
# uml to png for Readme
plantuml ./${1%.*}.uml
