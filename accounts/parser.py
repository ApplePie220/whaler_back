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
                elif label == "CMD" or label == "ENTRYPOINT":
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

class DockercomposeToJsonParser:
    @staticmethod
    def parse_dockercompose_to_json(dockercompose_input):
        try:
            docker_compose = yaml.safe_load(dockercompose_input)
            services = docker_compose.get("services", {})

            nodes = []
            edges = []
            y_position_service = 0  # Инициализируем начальную позицию y для сервисов
            y_position_others = 200  # Инициализируем начальную позицию y для остальных узлов
            x_position = 890  # Инициализируем начальную позицию x

            # Создаем узел для инструкции "services"
            services_node_id = f"dndnode_{len(nodes)}"
            services_node = {
                "id": services_node_id,
                "type": "input",
                "position": {
                    "x": 800,
                    "y": y_position_service  # Установим начальную позицию y для сервисов
                },
                "data": {
                    "toolbarPosition": "left"
                },
                "label": "Services",
                "parameters": ""
            }
            nodes.append(services_node)
            y_position_service += 100  # Увеличим позицию y для сервисов на 100

            # Создаем узлы для каждого сервиса и добавляем связь к ним из узла "Services"
            for service_name, service_config in services.items():
                # Создаем узел для сервиса
                service_node_id = f"dndnode_{len(nodes)}"
                service_node = {
                    "id": service_node_id,
                    "type": "default",
                    "position": {
                        "x": x_position,  # Установим позицию x для сервиса
                        "y": y_position_service  # Установим позицию y для сервиса
                    },
                    "data": {
                        "toolbarPosition": "left"
                    },
                    "label": "service",
                    "parameters": service_name
                }
                nodes.append(service_node)
                x_position += 120  # Увеличим позицию x на 120 для следующего узла
                y_position_service += 0  # Позиция y останется неизменной для следующего сервиса

                # Создаем связь между узлом "Services" и узлом сервиса
                edge = {
                    "id": f"edge_{len(edges)}",
                    "source": services_node_id,
                    "target": service_node_id
                }
                edges.append(edge)

                # Добавляем узлы для параметров
                for key, value in service_config.items():
                    node_id = f"dndnode_{len(nodes)}"
                    node = {
                        "id": node_id,
                        "type": "output",
                        "position": {
                            "x": x_position,  # Установим позицию x для следующего узла
                            "y": y_position_others  # Установим позицию y для следующего узла
                        },
                        "data": {
                            "toolbarPosition": "left"
                        },
                        "label": key,
                        "parameters": value
                    }
                    nodes.append(node)
                    x_position += 160  # Увеличим позицию x на 120 для следующего узла

                    # Добавляем связь между сервисом и соответствующим узлом
                    edge = {
                        "id": f"edge_{len(edges)}",
                        "source": service_node_id,
                        "target": node_id
                    }
                    edges.append(edge)

            return {"nodes": nodes, "edges": edges}
        except Exception as e:
            print(e)
            raise ValueError("Failed to parse docker-compose.yml")