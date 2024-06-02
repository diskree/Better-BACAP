import os
import re
import sys
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("subproject", type=str, help="Subproject directory name")
parser.add_argument("version", type=str, help="Version of subproject")
args = parser.parse_args()
subproject_dir = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), args.subproject), args.version)
if not os.path.exists(subproject_dir):
    print(f"Directory '{subproject_dir}' is not exists.")
    sys.exit(1)

original_dir = os.path.join(subproject_dir, "Original")
better_dir = os.path.join(subproject_dir, "Better")
patches_dir = os.path.join(subproject_dir, "Patches")

if not os.path.exists(original_dir):
    print(f"Original directory in '{args.subproject}' is not exists.")
    sys.exit(1)

os.makedirs(better_dir, exist_ok=True)
os.makedirs(patches_dir, exist_ok=True)

data_dir = os.path.join(original_dir, "data")

advancement_message_functions = {}
advancement_trophy_functions = {}

for data_sub_dir, _, data_files in os.walk(data_dir):
    for data_file in data_files:
        if data_file.endswith('.json'):
            with open(os.path.join(data_sub_dir, data_file), 'r', encoding='utf-8') as data_json_file:
                data_json = json.loads(data_json_file.read().replace("\t", "    ").replace("\\'", "'"))
                if 'display' in data_json and 'rewards' in data_json and 'function' in data_json['rewards']:
                    rewards_function_namespace, rewards_function_path = data_json['rewards']['function'].split(':')
                    rewards_function = os.path.join(data_dir, f"{rewards_function_namespace}/functions/{rewards_function_path}.mcfunction")
                    if os.path.exists(rewards_function):
                        with open(rewards_function, 'r', encoding='utf-8') as rewards_function_file:
                            for rewards_command in rewards_function_file:
                                function_ids = re.findall(r"run function ([^\s]+)", rewards_command)
                                for function_id in function_ids:
                                    function_namespace, function_path = function_id.split(':')
                                    function = os.path.join(data_dir, f"{function_namespace}/functions/{function_path}.mcfunction")
                                    if os.path.exists(function):
                                        advancement_dir = data_sub_dir
                                        advancement_namespace = os.path.dirname(os.path.dirname(advancement_dir))
                                        advancement_name = data_file
                                        advancement_id = f"{os.path.basename(advancement_namespace)}:{os.path.basename(advancement_dir)}/{os.path.splitext(os.path.basename(advancement_name))[0]}"
                                        function_dir = function_path.split('/')[0]
                                        if function_dir == 'msg':
                                            advancement_message_functions[advancement_id] = function
                                        elif function_dir == 'trophy':
                                            advancement_trophy_functions[advancement_id] = function

for advancement_id, message_function_path in advancement_message_functions.items():
    better_path = os.path.join(better_dir, os.path.relpath(message_function_path, original_dir))
    os.makedirs(os.path.dirname(better_path), exist_ok=True)
    with open(message_function_path, 'r', encoding='utf-8') as infile, \
         open(better_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            if line.startswith("tellraw @a"):
                line = line.replace(
                    '"hoverEvent"',
                    f'"clickEvent":{{"action":"run_command","value":"/advancementssearch highlight {advancement_id} obtained_status"}},"hoverEvent"'
                )
            outfile.write(line)


for advancement_id, trophy_function_path in advancement_trophy_functions.items():
    better_path = os.path.join(better_dir, os.path.relpath(trophy_function_path, original_dir))
    os.makedirs(os.path.dirname(better_path), exist_ok=True)
    with open(trophy_function_path, 'r', encoding='utf-8') as infile, \
         open(better_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            if line.startswith("give @s"):
                line = line.replace(
                    'Trophy:1',
                    f'InvulnerablePlusPlus:{{ItemEntity:1,Void:1}},FakeItems:{{IsFake:1}},AdvancementId:"{advancement_id}",Trophy:1'
                )
            outfile.write(line)
