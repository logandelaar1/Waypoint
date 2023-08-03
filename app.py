from flask import Flask, render_template, request, jsonify
from shapely.geometry import Polygon as SPolygon, LineString
import geopandas as gpd
from geopy import Point
from geopy.distance import geodesic
def translate():
	relative_coords = open("meter_coords.txt", "r")
	points = relative_coords.readlines()

	output_behavior = open("LAWNMOWER", "w")

	output_behavior.write("Behavior = BHV_Waypoint\n")
	output_behavior.write("{\n")
	output_behavior.write("  name         = lawnmower\n")
	output_behavior.write("  pwt          = 100\n")
	output_behavior.write("  condition    = \n")
	output_behavior.write("  speed = 1\n")
	output_behavior.write("  capture_radius = 3\n")
	output_behavior.write("  slip_radius = 7\n")
	output_behavior.write("  lead = 10\n")
	output_behavior.write("  lead_damper = 5\n")
	output_behavior.write("  repeat = forever\n")

	output_behavior.write("  points = pts={")


	index = 0
	for point in points:
		x = round(float(point.split(",", 1)[0]), 2)
		y = round(float(point.split(",", 1)[1]), 2)
		
		if index == 0:
			output_behavior.write(str(x) + "," + str(y))
		else:
			output_behavior.write(":" + str(x) + "," + str(y))
		
		index += 1

	output_behavior.write("}\n")

	output_behavior.write("}\n")
class CoordinateGraph:
    def __init__(self, origin_lat, origin_long):
        self.origin = Point(origin_lat, origin_long)

    def calculate_difference(self, lat, long):
        destination = Point(lat, long)
        
        # Calculate difference in latitude (North/South direction)
        lat_diff = geodesic((self.origin.latitude, self.origin.longitude), 
                            (destination.latitude, self.origin.longitude)).meters
        if destination.latitude < self.origin.latitude:
            lat_diff = -lat_diff
    
        # Calculate difference in longitude (East/West direction)
        long_diff = geodesic((self.origin.latitude, self.origin.longitude), 
                             (self.origin.latitude, destination.longitude)).meters
        if destination.longitude < self.origin.longitude:
            long_diff = -long_diff
        
        return long_diff, lat_diff

    def process_file(self, file_name, output_file_name):
        with open(file_name, 'r') as file:
            with open(output_file_name, 'w') as outfile:
                for line in file:
                    # Parsing the coordinates
                    parts = line.split(',')
                    longitude = float(parts[0].split(': ')[1].strip())
                    latitude = float(parts[1].split(': ')[1].strip())

                    x, y = self.calculate_difference(latitude, longitude)

                    outfile.write(f"{x},{y}\n")

class PolygonProcessor:
    def __init__(self, coords):
        self.coords = [(coord['lng'], coord['lat']) for coord in coords]
        self.process_polygon()

    def process_polygon(self):
        shapely_polygon = SPolygon(self.coords)
        buffered_polygon = shapely_polygon.buffer(-0.00005)  # Adjusted for degrees

        step = 0.00016  # Adjusted for degrees
        x_min, y_min, x_max, y_max = buffered_polygon.bounds

        x_min += step
        x_max -= step
        y_min += step
        y_max -= step

        lines = []
        direction = 'right'
        y = y_min
        while y <= y_max:
            
            if direction == 'right':
                lines.append(LineString([(x_min, y), (x_max, y)]))
                direction = 'left'
            else:
                lines.append(LineString([(x_max, y), (x_min, y)]))
                direction = 'right'
            y += step

        lines_gdf = gpd.GeoDataFrame(geometry=lines, crs='EPSG:4326')
        self.clipped = gpd.clip(lines_gdf, buffered_polygon)
        

            

    def get_path_points(self):
        # Function to get all points in a LineString
        def process_line_points(geom):
            xs, ys = geom.xy
            return [{"lng": x, "lat": y} for x, y in zip(xs, ys)]

        path_points = []
        for geom in self.clipped.geometry:
            if geom.geom_type == 'LineString':
                path_points.extend(process_line_points(geom))
        with open('step.txt', 'w') as f:
            for i in path_points:
                # write each point on a new line
                f.write(f"Longitude: {i['lng']}, Latitude: {i['lat']}\n")
        graph = CoordinateGraph(41.34928, -74.063645)  
        graph.process_file('step.txt', 'meter_coords.txt') 
        translate()
        return path_points


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log_polygon', methods=['POST'])
def log_polygon():
    data = request.get_json()
    polygon_coords = data['polygon_coords']

    # Save the coordinates to a .txt file
    with open('coordinates.txt', 'w') as f:
        for coord in polygon_coords:
            lng, lat = coord['lng'], coord['lat']
            f.write(f"Longitude: {lng}, Latitude: {lat}\n")
    
    return 'success', 200

@app.route('/process_polygon', methods=['POST'])
def process_polygon():
    data = request.get_json()
    polygon_coords = data['polygon_coords']
    processor = PolygonProcessor(polygon_coords)

    path_points = processor.get_path_points()
    width = max([coord['lng'] for coord in path_points]) - min([coord['lng'] for coord in path_points])
    height = max([coord['lat'] for coord in path_points]) - min([coord['lat'] for coord in path_points])

    return jsonify({"path_points": path_points, "width": width, "height": height}), 200

if __name__ == '__main__':
    app.run(debug=True)
