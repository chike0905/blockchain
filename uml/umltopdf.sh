#!/bin/sh
plantuml -svg ./${1%.*}.uml && inkscape ./${1%.*}.svg -A ./${1%.*}.pdf
rm ./${1%.*}.svg
