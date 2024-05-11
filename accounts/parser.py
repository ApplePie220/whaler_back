import json
import yaml
import os
class DockerfileParser:
    def parse_json_to_dockerfile(json_data):
        nodes = json_data["nodes"]
        edges = json_data["edges"]
        
        dockerfile_input = ""
        dockerfile_output = ""
        
        input_nodes = [node for node in nodes if node["type"] == "input"]
        output_nodes = [node for node in nodes if node["type"] == "output"]
        
        if len(input_nodes) != 1:
            raise ValueError("There must be exactly one input node.")
        
        prev_target_id = None
        
        for edge in edges:
            source_node = next((node for node in nodes if node["id"] == edge["source"]), None)
            target_node = next((node for node in nodes if node["id"] == edge["target"]), None)
            
            
            if source_node and target_node:
                if prev_target_id != source_node['id']:
                    dockerfile_input += f"{source_node['label']} {source_node['parameters']}\n"
                    dockerfile_input += f"{target_node['label']} {target_node['parameters']}\n"
                else:
                    dockerfile_input += f"{target_node['label']} {target_node['parameters']}\n"
                prev_target_id = target_node['id']
        
        if len(output_nodes) != 1:
            raise ValueError("There must be exactly one output node.")
        
        return dockerfile_input 
    
class DockerfileToJsonParser:
    def parse_dockerfile_to_json(dockerfile_input):
        lines = dockerfile_input.split('\n')
        nodes = []
        edges = []

        prev_node_index = None
        input_node_id = None

        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                label = parts[0]
                parameters = ' '.join(parts[1:])
                position_x = 800
                position_y = 0

                if prev_node_index is not None:
                    position_x = nodes[prev_node_index]["position"]["x"]
                    position_y = nodes[prev_node_index]["position"]["y"] + 100

                node_id = f"dndnode_{len(nodes)}"

                if label == "FROM":
                    node_type = "input"
                    input_node_id = node_id
                elif label == "CMD":
                    node_type = "output"
                else:
                    node_type = "default"

                node = {
                    "id": node_id,
                    "type": node_type,
                    "position": {
                        "x": position_x,
                        "y": position_y
                    },
                    "data": {
                        "toolbarPosition": "left"
                    },
                    "label": label,
                    "parameters": parameters
                }

                nodes.append(node)

                if prev_node_index is not None:
                    edge = {
                        "id": f"edge_{len(edges)}",
                        "source": nodes[prev_node_index]["id"],
                        "target": node_id
                    }
                    edges.append(edge)

                prev_node_index = len(nodes) - 1

        # Adding edge from input node to the first node
        if input_node_id:
            edge = {
                "id": f"edge_{len(edges)}",
                "source": input_node_id,
                "target": nodes[0]["id"]
            }
            edges.append(edge)

        return {"nodes": nodes, "edges": edges}

class DockercomposeParser:
    def parse_json_to_docker_compose(json_data):
        nodes = json_data["nodes"]
        edges = json_data["edges"]

        services = {}

        for node in nodes:
            label = node["label"]
            parameters = node["parameters"]

            if node["type"] == "default":
                services[parameters] = {}

        for edge in edges:
            source_node = next((node for node in nodes if node["id"] == edge["source"]), None)
            target_node = next((node for node in nodes if node["id"] == edge["target"]), None)

            if source_node and target_node:
                source_label = source_node["parameters"]
                target_label = target_node["label"]
                target_parameters = target_node["parameters"]

                if target_label == "Image":
                    services[source_label]["image"] = target_parameters
                elif target_label == "Depends_on":
                    services[source_label]["depends_on"] = target_parameters
                elif target_label == "Environment":
                    services[source_label]["environment"] = target_parameters
                elif target_label == "Build":
                    services[source_label]["build"] = target_parameters
                elif target_label == "Restart":
                    services[source_label]["restart"] = target_parameters
                elif target_label == "Networks":
                    services[source_label]["networks"] = target_parameters
                elif target_label == "Ports":
                    services[source_label]["ports"] = target_parameters
                elif target_label == "Volumes":
                    services[source_label]["volumes"] = target_parameters

        docker_compose = {"version": "3", "services": services}

        return docker_compose

