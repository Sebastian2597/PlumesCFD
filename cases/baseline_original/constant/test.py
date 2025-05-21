import os

def read_points(filepath):
    """Reads points from the points file."""
    points = []
    with open(filepath, 'r') as file:
        lines = file.readlines()
        for line in lines[20:]:  # Skip the header (typically 20 lines in OpenFOAM points file)
            if line.strip() == ')':
                break
            point = list(map(float, line.strip("()\n").split()))
            points.append(point)
    return points

def read_faces(filepath):
    """Reads faces from the faces file."""
    faces = []
    with open(filepath, 'r') as file:
        lines = file.readlines()
        for line in lines[20:]:  # Skip the header (typically 20 lines in OpenFOAM faces file)
            line = line.strip()
            if line.strip() == ')':
                break
            line = line.replace('(', '').replace(')', '').strip()  # Clean the line
            if line:
                face = list(map(int, line.split()))
                faces.append(face)
    return faces

def read_owner(filepath):
    """Reads owner from the owner file."""
    owner = []
    with open(filepath, 'r') as file:
        lines = file.readlines()
        for line in lines[20:]:  # Skip the header (if any)
            line = line.strip()
            # Skip lines that are empty or comments
            if not line or line.startswith('//'):
                continue
            if line.strip() == ')' or line.strip() == '(':
                continue  # Skip any parentheses lines
            if line:  # Make sure the line is not empty
                owner.append(int(line.strip()))
    return owner

def read_neighbour(filepath):
    """Reads neighbour from the neighbour file."""
    neighbour = []
    with open(filepath, 'r') as file:
        lines = file.readlines()
        for line in lines[20:]:  # Skip the header (if any)
            line = line.strip()
            # Skip lines that are empty or comments
            if not line or line.startswith('//'):
                continue
            if line.strip() == ')' or line.strip() == '(':
                continue  # Skip any parentheses lines
            if line:  # Make sure the line is not empty
                neighbour.append(int(line.strip()))
    return neighbour


def write_geo_script(points, faces, filepath="output.geo"):
    """Writes points and faces to a Gmsh .geo script."""
    with open(filepath, 'w') as geo_file:
        geo_file.write("// Gmsh script generated from OpenFOAM polyMesh data\n\n")
        
        # Write points
        for i, point in enumerate(points):
            geo_file.write(f"Point({i+1}) = {{{point[0]}, {point[1]}, {point[2]}, 1.0}};\n")
        
        geo_file.write("\n// Lines from faces\n")
        
        # Write lines (edges from faces)
        line_id = 1
        line_loops = []
        for face in faces:
            loop = []
            for j in range(len(face)):
                p1 = face[j] + 1  # OpenFOAM index to Gmsh index
                p2 = face[(j + 1) % len(face)] + 1
                geo_file.write(f"Line({line_id}) = {{{p1}, {p2}}};\n")
                loop.append(line_id)
                line_id += 1
            line_loops.append(loop)
        
        # Write line loops and surfaces
        geo_file.write("\n// Surfaces\n")
        for i, loop in enumerate(line_loops):
            geo_file.write(f"Line Loop({i+1}) = {{{', '.join(map(str, loop))}}};\n")
            geo_file.write(f"Plane Surface({i+1}) = {{{i+1}}};\n")
    
    print(f"Gmsh script generated at {filepath}")

# Paths to OpenFOAM polyMesh files
polyMesh_dir = "./polyMesh"
points_path = os.path.join(polyMesh_dir, "points")
faces_path = os.path.join(polyMesh_dir, "faces")
owner_path = os.path.join(polyMesh_dir, "owner")
neighbour_path = os.path.join(polyMesh_dir, "neighbour")

# Read data from polyMesh files
points = read_points(points_path)
faces = read_faces(faces_path)
owner = read_owner(owner_path)
neighbour = read_neighbour(neighbour_path)

# Generate Gmsh script
write_geo_script(points, faces, filepath="output.geo")
