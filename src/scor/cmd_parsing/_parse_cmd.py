from typing import List
from os import path
from pathlib import Path
import datetime


def process_command(
    command_string: str,
    config_dir: Path,
    node_list: List[str],
) -> List[str]:
    command_tokens = tokenize_command(command_string)

    uid = create_uid()
    commands_list = []
    for node in node_list:
        subdir_path = get_config_subdir_path(config_dir, node)
        log_filename = node + "__" + str(uid) + ".log"
        err_filename = node + "__" + str(uid) + ".err"
        log_path = path.join(subdir_path, log_filename)
        err_path = path.join(subdir_path, err_filename)
        new_command = command_tokens + ["1>", str(log_path), "2>", str(err_path)]
        commands_list.append(new_command)

    return commands_list


def tokenize_command(command_string: str):
    tokenized_command = command_string.split()
    return tokenized_command


def create_base_dir_path_check_commands(
    config_dir: Path,
):
    command = 'if [ ! -d "{0}" ]; then mkdir {0}; fi'.format(config_dir)
    command_tokens = tokenize_command(command)
    return command_tokens


def create_sub_dir_path_check_commands(config_dir: Path, node_list: List[str]):
    command_token_list = []
    for node in node_list:
        sub_dir = get_config_subdir_path(config_dir, node)
        command = 'if [ ! -d "{0}" ]; then mkdir {0}; fi'.format(sub_dir)
        command_tokens = tokenize_command(command)
        command_token_list.append(command_tokens)

    return command_token_list


def create_uid():
    time_now = datetime.datetime.now()
    time_string = time_now.strftime("%d_%m_%y__%H_%M_%S_%f")
    return time_string


def get_config_subdir_path(config_path: Path, node: str):
    return path.join(config_path, node)


