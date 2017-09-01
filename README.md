# MTA Extract

The purpose of this script is to create spataial datasets from the New York MTA GTFS using ArcPy. This data includes:

* Subway Station Points
* Subway Route Lines
* Bus Stop Points
* Bus Route Lines

## Directions
1. In the command line change the directory to the location of the mta_extract.pyv

```
    cd Your\Directory\mta_extract.py
```

2. Run the script as seen below. The first half is call the python.exe location. The second half is the Python script.

```
    C:\Python27\ArcGIS10.4\python.exe mta_extract.py
```

3. When the script is done you will have new zip files of these datasets in the directory where the mta_features.py is stored.

## Notes
* Some datasets the MTA provide will be incomplete or missing connections. Use at your own risk.
