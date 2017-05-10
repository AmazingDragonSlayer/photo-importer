# Photo Importer #

This simple script is designed to help with importing photos from various sources into one directory with specific structure. 
It was created specifically to help with [Shotwell Photo Manager](https://wiki.gnome.org/Apps/Shotwell), cause I had trouble with importing photos from different directories in 0.22.0 version.

Script finds various dates in file, takes the oldest one and either moves or copies it to created directory structure.

## Usage ##

Usage is very simple:

_./pimport.py [options] [source] [destination]_

where:

__[source]__ - which files to include, it can be either a directory, or a path including filename pattern (use standard pathname expansion). When using pattern make sure to include quotes around parameter.
__[destination]__ - target directory in which year/month/day sub-directories structure will be created

also following options can be included before the source:

__-m__ - method, can be either cp for copy or mv (move)
__-o__ - overwrite - if included files can be overwritten if already exists at target location
__-r__ - recursive - processes _source_ recursively
