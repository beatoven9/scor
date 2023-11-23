import argparse
import datetime
import subprocess
import threading
from os import getenv, path
from pathlib import Path
from typing import List, Optional, Union


def main():
    command_string = get_cli_args()
    run_command(command_string=command_string)


def run_command(command_string: str, node_list: Optional[List[str]] = None):
    """
    This is the main interface of the program.

    --User can have environment variable "NODE_LIST" set to the
    hostnames of the nodes you wish to target.

    --Alternatively, you can provide a list of hostnames.
    """

    config_dir = "~/.cpm/"

    if node_list is None:
        node_list = get_node_list()

    run_command_on_all_nodes(
        command_string=command_string,
        config_dir=config_dir,
        node_list=node_list,
    )


def get_node_list():
    # node_list for now is an env var of the format "node1,node2,node3"
    # Later, it will be gathered from slurm.
    node_list_var = getenv("NODE_LIST")
    node_list = process_node_list(node_list_var)

    return node_list


def process_node_list(node_list_var):
    node_list = node_list_var.split(",")
    return node_list


def run_command_on_all_nodes(
    command_string: str, config_dir: Path, node_list: List[str]
):
    check_config_dirs(config_dir, node_list)
    command_tokens = process_command(command_string, config_dir, node_list)

    run_command_across_nodes(command_tokens, node_list)


def create_uid():
    time_now = datetime.datetime.now()
    time_string = time_now.strftime("%d_%m_%y__%H_%M_%S_%f")
    return time_string


def check_config_dirs(config_dir: Path, node_list: List[str]):
    path_check_command_list = create_base_dir_path_check_commands(
        config_dir,
    )
    run_command_across_nodes(path_check_command_list, node_list)

    subdir_path_check_command_list = create_sub_dir_path_check_commands(
        config_dir=config_dir,
        node_list=node_list,
    )

    run_command_across_nodes(subdir_path_check_command_list, node_list)


def create_base_dir_path_check_commands(
    config_dir: Path,
):
    command = 'if [ ! -d "{0}" ]; then mkdir {0}; fi'.format(config_dir)
    command_tokens = tokenize_command(command)
    return command_tokens


def get_config_subdir_path(config_path: Path, node: str):
    return path.join(config_path, node)


def create_sub_dir_path_check_commands(config_dir: Path, node_list: List[str]):
    command_token_list = []
    for node in node_list:
        sub_dir = get_config_subdir_path(config_dir, node)
        command = 'if [ ! -d "{0}" ]; then mkdir {0}; fi'.format(sub_dir)
        command_tokens = tokenize_command(command)
        command_token_list.append(command_tokens)

    return command_token_list


def get_cli_args():
    parser = argparse.ArgumentParser(
        prog="Capvt Package Manager",
        description="Simple apt wrapper for clusters",
    )
    parser.add_argument("command")
    args = parser.parse_args()

    return args.command


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


def run_commands(command_tokens):
    result = subprocess.run(command_tokens, stdout=subprocess.PIPE)
    return result


def run_command_across_nodes(
    command_tokens: Union[
        List[str],
        List[List[str]],
    ],
    node_list: List[str],
):
    def spawn_thread(command_tokens):
        command = [
            "ssh",
            node,
            " ".join(command_tokens),
        ]

        print("Running command: ", " ".join(command))
        new_thread = threading.Thread(target=subprocess_wrapper, args=[command])
        return new_thread

    threads = []
    if isinstance(command_tokens[0], str):
        # spawn one thread per node
        for node in node_list:
            new_thread = spawn_thread(command_tokens)
            threads.append(new_thread)
            new_thread.start()

    elif isinstance(command_tokens[0], List):
        for command, node in zip(command_tokens, node_list):
            new_thread = spawn_thread(command)
            threads.append(new_thread)
            new_thread.start()

    print("----Waiting for all jobs to complete.")
    # wait for threads to complete
    for thread in threads:
        thread.join()

    print("\nCOMPLETE!\n")


def subprocess_wrapper(command: List[str]):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return result


if __name__ == "__main__":
    main()
