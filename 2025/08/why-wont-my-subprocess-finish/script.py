#!/usr/bin/env python3

import subprocess
import sys

proc = subprocess.Popen(sys.argv[1:], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

stdout, stderr = [], []
while proc.poll() is None:
    if stdout_chunk := proc.stdout.readline():
        stdout.append(stdout_chunk.decode("utf-8"))
    if stderr_chunk := proc.stderr.readline():
        stderr.append(stderr_chunk.decode("utf-8"))

open("stdout.txt", "w").write("".join(stdout))
open("stderr.txt", "w").write("".join(stderr))
