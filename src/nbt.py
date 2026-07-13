import json

import networkx as nx
from ipysigma import Sigma
import matplotlib.pyplot as plt
import time

def get_timestamp():
    return time.strftime("%Y%m%d%H%M%S")

# Function to convert JSON data to a NetworkX graph
def convert_json_to_nx(date_range: str):
    # Open the JSON file containing the parsed data
    file_path = f"data/in/nbt_index_{date_range}.json"
    with open(file_path, "r") as f:
        data = json.load(f)
        
    # Extract the catalogue data from the JSON
    catalogue_items = data["results"]["bindings"]
    item_dict_list = []

    edges = []
    nodes = {}
    
    for x in catalogue_items:

        if x is not None:
            itemdata = x
            # Create a dictionary for each catalogue item
            item = {
                "uri": itemdata.get("uri").get("value"),
                "title": itemdata.get("name").get("value"),
                "language": itemdata.get("language").get("value"),
                "date": itemdata.get("jaar").get("value"),
                "pref_subject": itemdata.get("preflabel").get("value") if itemdata.get("preflabel") is not None else None,
                "narrower_subject": itemdata.get("narrowerlabel").get("value") if itemdata.get("narrowerlabel") is not None else None,
                "broader_subject": itemdata.get("broaderlabel").get("value") if itemdata.get("broaderlabel") is not None else None,
            }
            item_dict_list.append(item)

            # Define edges for the catalogue graph
            #for subject in item["subject"]:
            edges.append((item["pref_subject"], item["title"]))
            if item["narrower_subject"] is not None:
                edges.append((item["pref_subject"], item["narrower_subject"]))
                edges.append((item["narrower_subject"], item["title"]))
            if item["broader_subject"] is not None:
                edges.append((item["pref_subject"], item["broader_subject"]))
                edges.append((item["broader_subject"], item["title"]))

            # Define nodes for the catalogue graph
            keys_title_to_extract = ["title", "pref_subject", "narrower_subject", "broader_subject", "date", "language", "uri"]
            keys_subject_to_extract = ["pref_subject", "narrower_subject", "broader_subject"]
            for node_attributes in item_dict_list:
                node_title = node_attributes["title"]
                node_pref_subject = node_attributes["pref_subject"]
                node_narrower_subject = node_attributes["narrower_subject"]
                node_broader_subject = node_attributes["broader_subject"]

                sub_dict_title = {key: node_attributes[key] for key in keys_title_to_extract if key in node_attributes}
                sub_dict_title["type"] = "book"
                sub_dict_subject = {key: node_attributes[key] for key in keys_subject_to_extract if key in node_attributes}
                sub_dict_subject["type"] = "subject"
                
                nodes[node_title] = sub_dict_title
                nodes[node_pref_subject] = sub_dict_subject
                nodes[node_narrower_subject] = sub_dict_subject
                nodes[node_broader_subject] = sub_dict_subject

    #print(edges)
    #print(nodes)
    
    G = nx.DiGraph()
    for edge in edges:
        G.add_edge(edge[0], edge[1])

    nx.set_node_attributes(G, nodes)
    nx.draw(G, with_labels=True)
    #plt.savefig("filename.png")

    # Create a Sigma visualization
    Sigma(
        G,
        )
    Sigma.write_html(
        G,
        #f"data/out/{get_timestamp()}_nbt_index_{date_range}.html",
        f"data/out/nbt_index_{date_range}.html",
        fullscreen=True,
        node_metrics=["louvain"],
        node_color="pref_subject",
        node_size_range=(3, 30),
        node_shape = "type",
        node_shape_mapping = {
            "book": "book_2",
            "subject": "label"
            },
        max_categorical_colors=50,
        default_edge_type="curve",
        #node_border_color_from="node",
        default_node_label_size=14,
        node_size=G.degree,
        label_density=2
    )

if __name__ == "__main__":
    date_ranges = [
        "1800-1825",
        "1826-1850",
        "1851-1875",
        "1876-1900",
        "1901-1925",
        "1926-1950",
        "1951-1975",
        "1976-2000"
    ]
    for dr in date_ranges:
        convert_json_to_nx(dr)
    #convert_json_to_nx("1800-1825")    
