from typing import List, Union
import threading
import subprocess


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
