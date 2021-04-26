import os
import subprocess

filenames = os.listdir()

for filename in filenames:
    if not filename.endswith(".npz"):
        continue

    command = f"""/usr/local/bin/python3 populate_profile_data.py -f "sample.db" --profile_filename "{filename}" """
    cmd = subprocess.run(command, shell=True)
    print(cmd)

