# Geospatial Polygon Processor

This repository contains the implementation of a Flask-based web application that processes polygons using geospatial data and allows for creating lawnmower paths within them.

## Description

The web application leverages various Python packages like `geopy`, `shapely`, `geopandas`, and `flask` to process, calculate and render geospatial information. 

Key functionalities of the repository include:

1. **Coordinate Graph Calculation**: The `CoordinateGraph` class allows for converting a pair of latitude-longitude coordinates into a difference of meters from the origin. This is crucial for establishing a consistent metric system for further calculations.

2. **Polygon Processing**: The `PolygonProcessor` class takes a list of coordinates, constructs a polygon using them, and then processes it to create a lawnmower path (back-and-forth motion) inside the polygon. The lawnmower path is constructed by creating horizontal lines across the polygon, alternating in direction for each row.

3. **Translation to Behavior File**: The application can translate the calculated coordinates into a `LAWNMOWER` behavior file. This file defines waypoints for a path that can be followed by an autonomous agent.

4. **Flask Server**: The Flask server (`app.py`) receives polygon data from the front end, processes it, and returns the corresponding lawnmower path. It can log the polygon coordinates received and process them. The server also handles browser launching, with the help of Python's multiprocessing library.

5. **Front End**: The front end (`index.html`) allows users to draw polygons on a map and send the polygon's coordinates to the server. After the server has processed the coordinates and generated the lawnmower path, the path is rendered on the map. It also logs the width and height of the processed polygon.

## Installation

Before running the application, you'll need to install the required Python packages. You can do this by running the following command:

```bash
pip install flask shapely geopandas geopy
