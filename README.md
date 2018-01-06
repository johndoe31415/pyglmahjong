# pyglmahjong
This is an OpenGL-based Mahjong implementation written in Python. I've created
this a few years back and it's playable, but not really finished. Recently I
wanted to play Mahjong again and noticed that, while this was quite a lot of
work, I've never published any of it. Therefore I did some very rough cleaning
up and push it onto GitHub in the hope that it will be useful. [Here's a
screenshot](https://johndoe31415.github.io/pyglmahjong/).

# Challenges
It is surprisingly difficult to create a Mahjong board that is guaranteed to be
solvable, yet isn't *easy* to solve.  That is, if the approach is to simply
create the board in reverse order of playing, it is guaranteed to be solvable
and the algorithm for creating the board is extremely efficient, but it will
usually result in boards which are trivial to solve.  Randomized boards are
quite often non-solvable. The approach that I take is to randomize boards and
then use a backtracking algorithm to determine if the board is solvable. That
is costly (hence startup takes quite some time), but works. In the future it
would be possible to pre-enumerate certain seeds that are known to be solvable
and skip the check.

# Credits
Some of the tile art (namely the one that looks good) is taken from [Gnome
Mahjongg](https://git.gnome.org//browse/gnome-mahjongg/) which, in turn, took
their art from the absolutely [beautiful smooth-tileset created by Jim
Evins](https://github.com/jimevins/smooth-tileset). The Mahjong board layouts
were also copied from Gnome Mahjongg. Some of the artwork has been drawn by
myself (season and flower tiles, white dragon tile, circle suit).  Some of the
tiles (namely the flower tiles) have been inspired (but were re-created) by
[JShisen](http://www.admoore.de/javashisen/jsdownload.html). The OpenGL code,
in particular the shaders, are based on the excellent [OpenGL tutorial of
opengl-tutorial.org](http://www.opengl-tutorial.org/beginners-tutorials/tutorial-8-basic-shading/).

# License
GNU General Public License v3.
