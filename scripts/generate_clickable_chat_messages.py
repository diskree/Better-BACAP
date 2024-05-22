import os
import json

data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
messages_path = os.path.join(data_path, "bc_rewards/functions/msg")

for dir, _, json_files in os.walk(data_path):
    for json_file in json_files:
        if json_file.endswith('.json'):
            with open(os.path.join(dir, json_file), 'r', encoding='utf-8') as advancement_file:
                advancement_json = json.loads(advancement_file.read().replace("\t", "    ").replace("\\'", "'"))
                if 'rewards' in advancement_json and 'display' in advancement_json:
                    function_id = advancement_json['rewards']['function'].split(':')
                    function_namespace = function_id[0]
                    function_path = function_id[1]
                    if function_namespace == 'bc_rewards':
                        folder_and_name = function_path.split('/')
                        folder_name = folder_and_name[0]
                        file_name = folder_and_name[1]
                        if folder_name != "technical" and file_name != "root":
                            file_path = os.path.join(messages_path, folder_name, f"{file_name}.mcfunction")
                            advancement_id = f"{os.path.basename(os.path.dirname(os.path.dirname(dir)))}:{os.path.basename(dir)}/{os.path.splitext(os.path.basename(json_file))[0]}"

                            with open(file_path, 'r', encoding='utf-8') as file:
                                lines = file.read().splitlines()

                            modified_lines = []
                            for line in lines:
                                if line.strip().startswith("tellraw @a"):
                                    tellraw_command = line.strip()[len("tellraw @a"):].strip()
                                    modified_command = tellraw_command.replace(
                                        '"hoverEvent"',
                                        f'"clickEvent":{{"action":"run_command","value":"/advancementssearch highlight {advancement_id} obtained_status"}},"hoverEvent"'
                                    )
                                    modified_lines.append(f"tellraw @a {modified_command}")
                                else:
                                    modified_lines.append(line)

                            with open(file_path, 'w', encoding='utf-8') as file:
                                file.write("\n".join(modified_lines))
