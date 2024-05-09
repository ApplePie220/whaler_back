import json
import os

class DockerfileParser:
    def generate_dockerfile(json_data):
        dockerfile = ""

        # Пройдемся по всем узлам
        for node in json_data["nodes"]:
            label = node["label"]
            parameters = node["parameters"]

            # Если узел имеет тип input, он будет добавлен в начало Dockerfile
            if node["type"] == "input":
                dockerfile += f"{label} {parameters}\n"

            # Если узел имеет тип output, он будет добавлен в конец Dockerfile
            elif node["type"] == "output":
                dockerfile += f"{label} {parameters}\n\n"

            # Если узел имеет тип default, он будет добавлен после узла-источника (source)
            else:
                dockerfile += f"{label} {parameters}\n"

        return dockerfile
