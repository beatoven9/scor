# This honestly could be usefule as a simple command runner.
# Maybe the outputs could be saved to files, one per node.
# Output must be captured. There should probably be a way of getting prompted.
# 
A simple package-manager wrapper for installing/uninstalling packages on all nodes.

Basic premise:

	run as root
	type in the command that you want to run
	the wrapper will just run the command on every node
		node-list should be gathered by an environment variable
			-if the environment variable does not exist, 
			you should be prompted to create one and add it to your .bashrc file




I should do some tests first.

1. in Python use a bash call thing to ssh into another node and make another command. (touch a file).
2. add functionality to ^^ that script to receive std from that node.
3. write this output to a file.
4. have this script call it for each node in a list.
5. create an env variable for the node list. and read from it.
6. if there is no env variable ask them to list their nodes hostnames.
7. output the correct env variable and suggest the user paste it into their .bashrc file.




Other ideas:

I should write scripts to do the rest of these tasks using the command runner.
I should figure out how to install it as a module.

