# I need to pull the config_dir checks into their own thing.
# I mean ultimately, this is not the right way to do this, right?
# I should really just have the creation of those be in the same
# ssh command. totally possible, potentially annoying.
# This won't be hard. I just need to do a 'mkdir -p .scor/$(hostname)';
# Right before the other call in the ssh thing
#
# Also, I need to get the get_nodes_list stuff into its own module.
#
import argparse
from os import getenv
from pathlib import Path
from typing import List, Optional
from scor.mapping import run_command_across_nodes
from scor.cmd_parsing import (
    process_command,
    create_base_dir_path_check_commands,
    create_sub_dir_path_check_commands,
)


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

    config_dir = "~/.scor/"

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


def get_cli_args():
    parser = argparse.ArgumentParser(
        prog="Capvt Package Manager",
        description="Simple apt wrapper for clusters",
    )
    parser.add_argument("command")
    args = parser.parse_args()

    return args.command


if __name__ == "__main__":
    main()
