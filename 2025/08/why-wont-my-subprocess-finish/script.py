#!/usr/bin/env python3

import subprocess
import sys

sp = subprocess.Popen(sys.argv[1:], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

stdout, stderr = [], []
while sp.poll() is None:
    if stdout_chunk := sp.stdout.readline():
        stdout.append(stdout_chunk.decode("utf-8"))
    if stderr_chunk := sp.stderr.readline():
        stderr.append(stderr_chunk.decode("utf-8"))

open("stdout.txt", "w").write("".join(stdout))
open("stderr.txt", "w").write("".join(stderr))
