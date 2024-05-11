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

