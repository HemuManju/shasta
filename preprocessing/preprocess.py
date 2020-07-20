import os
from pathlib import Path

# import matplotlib.pyplot as plt, mpld3

# import networkx as nx
# import osmnx as ox


def preprocess():
    # Save OSMNX graph
    # G = ox.graph_from_xml('map.som', simplify=True, bidirectional='walk')
    # G = nx.convert_node_labels_to_integers(G)
    # fig, ax = ox.plot_graph(G)
    # lat_lon = G.nodes[]

    # tooltip = mpld3.plugins.PointLabelTooltip(fig, labels=list(data.label))
    # mpld3.plugins.connect(fig, tooltip)

    # mpld3.save_html(fig, "./out.html")

    # Create the 3D world from the map.osm file
    os.system(
        "java -jar OSM2World.jar --config texture_config.properties -i map.osm -o map.obj"  # noqa
    )

    # Use the blender to bake the texture
    blender_path = "/Applications/blender.app/Contents/MacOS/blender"
    os.system(blender_path + " --background  --python bake_texture.py")

    # Tidy up things and move the files to respective folders
    print('---------------------------------------')
    name = input("Please provide a name for the asset: ")

    # Create a directory
    parent_folder = name
    meshes_folder = name + '/meshes'
    Path(parent_folder).mkdir(parents=True, exist_ok=True)
    Path(meshes_folder).mkdir(parents=True, exist_ok=True)

    # Move map.osm and coordinates inside the parent folder
    def move_files(file_name, directory):
        Path(file_name).rename(directory + '/' + file_name)
        try:
            Path(file_name).rename(directory + '/' + file_name)
        except FileNotFoundError:
            pass

    files = [
        'map.osm', 'coordinates.csv', 'environment.urdf',
        'environment_collision_free.urdf'
    ]
    for file in files:
        move_files(file, parent_folder)

    files = ['map.obj', 'map.png', 'map.mtl']
    for file in files:
        move_files(file, meshes_folder)

    # Finaly move the whole folder to data folder
    move_files('test', '../data/assets/')


if __name__ == "__main__":
    preprocess()
