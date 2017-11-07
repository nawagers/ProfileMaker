# ProfileMaker
Guidebook making software for plotting GPX Waypoints on a Track's elevation profile

A python script that generates PNG images of each page of a guide book. No UI or documentation built yet and output is still fairly buggy. The script is mostly implemented though, so it will indeed generate data. Sample output provided.


* Clean up your track files to remove stops or spurious points
* Move waypoints onto the track where it branches if they are off trail
* Add text to the comment field of the waypoint, add the letter for each service in the description field
* Copy NET.ini, update its name, edit the filenames to use inside
* Change the .ini location in the first few lines of ProfileBuilder.py
