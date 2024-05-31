from flask import Flask, request, jsonify
import cv2
import os
import numpy as np
import json
import uuid
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return 'Welcome to my Flask application'



def extract_coordinates(image_data):
    nparr = nparr = np.frombuffer(image_data.read(), np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # image = cv2.imread(image_data)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    coordinates = {
        "unit": "cm",
        "layers": {
            "layer-1": {
                "id": "layer-1",
                "altitude": 0,
                "order": 0,
                "opacity": 1,
                "name": "default",
                "visible": True,
                "vertices": {},
                "lines": {},
                "holes": {},
                "areas": {}
            }
        },
        "grids": {
            "h1": {
                "id": "h1",
                "type": "horizontal-streak",
                "properties": {
                    "step": 20,
                    "colors": ["#808080", "#ddd", "#ddd", "#ddd", "#ddd"]
                }
            },
            "v1": {
                "id": "v1",
                "type": "vertical-streak",
                "properties": {
                    "step": 20,
                    "colors": ["#808080", "#ddd", "#ddd", "#ddd", "#ddd"]
                }
            }
        },
        "selectedLayer": "layer-1",
        "groups": {},
        "width": image.shape[1],
        "height": image.shape[0],
        "meta": {},
        "guides": {
            "horizontal": {},
            "vertical": {},
            "circular": {}
        }
    }
    processed_contours = set()
    for i, (contour, hier) in enumerate(zip(contours, hierarchy[0])):
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if cv2.contourArea(approx) < 100 or i in processed_contours:
            continue
        hole = hier[2]
        if hole != -1:
            continue
        contour_coordinates = [(int(point[0][0]), int(point[0][1])) for point in approx]
        vertex_ids = [str(uuid.uuid4()) for _ in range(len(contour_coordinates))]
        line_ids = [str(uuid.uuid4()) for _ in range(len(contour_coordinates))]
        for j, (x, y) in enumerate(contour_coordinates):
            vertex_id = vertex_ids[j]
            line_id = line_ids[j]
            next_j = (j + 1) % len(contour_coordinates)
            next_vertex_id = vertex_ids[next_j]
            next_line_id = line_ids[next_j]
            coordinates["layers"]["layer-1"]["vertices"][vertex_id] = {
                "id": vertex_id,
                "type": "",
                "prototype": "vertices",
                "name": "Vertex",
                "misc": {},
                "selected": False,
                "properties": {},
                "visible": True,
                "x": x,
                "y": coordinates["height"] - y,
                "lines": [line_id],
                "areas": []
            }
            is_wall_line, line_length = is_wall(contour_coordinates[j], contour_coordinates[next_j])
            if is_wall_line:
                coordinates["layers"]["layer-1"]["lines"][line_id] = {
                    "id": line_id,
                    "type": "wall",
                    "prototype": "lines",
                    "name": "Wall",
                    "misc": {},
                    "selected": False,
                    "properties": {
                        "height": {"length": 300},
                        "thickness": {"length": 20},
                        "textureA": "bricks",
                        "textureB": "bricks",
                        "length": {"length": line_length}
                    },
                    "visible": True,
                    "vertices": [vertex_id, next_vertex_id],
                    "holes": []
                }
            else:
                coordinates["layers"]["layer-1"]["lines"][line_id] = {
                    "id": line_id,
                    "type": "door",
                    "prototype": "lines",
                    "name": "Door",
                    "misc": {},
                    "selected": False,
                    "properties": {
                        "width": {"length": 80},
                        "height": {"length": 215},
                        "altitude": {"length": 0},
                        "thickness": {"length": 30},
                        "flip_orizzontal": False,
                        "length": {"length": line_length}
                    },
                    "visible": True,
                    "vertices": [vertex_id, next_vertex_id],
                    "holes": []
                }
        processed_contours.add(i)
        child = hier[2]
        while child != -1:
            epsilon_hole = 0.02 * cv2.arcLength(contours[child], True)
            approx_hole = cv2.approxPolyDP(contours[child], epsilon_hole, True)
            hole_coordinates = [(int(point[0][0]), int(point[0][1])) for point in approx_hole]
            vertex_ids_hole = [str(uuid.uuid4()) for _ in range(len(hole_coordinates))]
            line_ids_hole = [str(uuid.uuid4()) for _ in range(len(hole_coordinates))]
            for j, (x, y) in enumerate(hole_coordinates):
                vertex_id_hole = vertex_ids_hole[j]
                line_id_hole = line_ids_hole[j]
                coordinates["layers"]["layer-1"]["vertices"][vertex_id_hole] = {
                    "id": vertex_id_hole,
                    "type": "",
                    "prototype": "vertices",
                    "name": "Vertex",
                    "misc": {},
                    "selected": False,
                    "properties": {},
                    "visible": True,
                    "x": x,
                    "y": coordinates["height"] - y,
                    "lines": [line_id_hole],
                    "areas": []
                }
                next_j = (j + 1) % len(hole_coordinates)
                next_vertex_id_hole = vertex_ids_hole[next_j]
                next_line_id_hole = line_ids_hole[next_j]
                coordinates["layers"]["layer-1"]["lines"][line_id_hole] = {
                    "id": line_id_hole,
                    "type": "wall",
                    "prototype": "lines",
                    "name": "Wall",
                    "misc": {},
                    "selected": False,
                    "properties": {
                        "height": {"length": 300},
                        "thickness": {"length": 20},
                        "textureA": "bricks",
                        "textureB": "bricks"
                    },
                    "visible": True,
                    "vertices": [vertex_id_hole, next_vertex_id_hole],
                    "holes": []
                }
            processed_contours.add(child)
            child = hierarchy[0][child][0]
    return coordinates


@app.route('/process_image', methods=['POST'])
def process_image():
    print("hhhhhhhhhhhh")
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    try:
        # Process the image and extract coordinates
        coordinates = extract_coordinates(image)
        # Return the extracted coordinates as JSON
        output_json_path = "architectural_coordinates.json"
        with open(output_json_path, 'w') as json_file:
            json.dump(coordinates, json_file)
        return jsonify(coordinates)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def is_wall(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    angle_threshold = 10
    angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
    angle = angle if angle >= 0 else 180 + angle
    is_wall_line = abs(angle - 90) < angle_threshold or abs(angle - 180) < angle_threshold
    line_length = int(np.sqrt((x2 - x1)**2 + (y2 - y1)**2))
    return is_wall_line, line_length

def save_to_json(coordinates, output_json_path):
    with open(output_json_path, 'w') as json_file:
        json.dump(coordinates, json_file)

if __name__ == "__main__":
    # image_path = "abcd.jpg"
    # extracted_coordinates = extract_coordinates(image_path)
    # output_json_path = "architectural_coordinates.json"
    # save_to_json(extracted_coordinates, output_json_path)
    app.run(debug=True)