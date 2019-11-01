import subprocess, os, sys

if len(sys.argv) != 2:
	sys.exit("Usage: test.py <input folder>")

for inputfile in [i for i in os.listdir(sys.argv[1]) if ".txt" in i]:
	print("Testing " + inputfile)
	maze = sys.argv[1] + "/" + inputfile
	comm = "python3 sim3.py " + maze + " 1"
	subprocess.call(comm, shell=True)