We recently hit an issue where a build script was getting stuck on some machines some of
the time. It was one of those issues that didn't happen too frequently and restarting
the terminal instead of debugging the problem seemed like the best use of time.

Well, let's go ahead and debug the problem now. Consider a simple Python program that 
executes a given command and stores console output in `stdout.txt` and `stderr.txt`:

```python
import subprocess
import sys

# Execute the provided command line
proc = subprocess.Popen(sys.argv[1:], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Collect output from stdout and stderr
stdout, stderr = [], []
while proc.poll() is None:
    if stdout_chunk := proc.stdout.readline():
        stdout.append(stdout_chunk.decode("utf-8"))
    if stderr_chunk := proc.stderr.readline():
        stderr.append(stderr_chunk.decode("utf-8"))

# Write collected output to text file
open("stdout.txt", "w").write("".join(stdout))
open("stderr.txt", "w").write("".join(stderr))
```

Great! Run this on a few example programs and it seems to work flawlessly. But let's
write a program that is intentionally pathalogical:

```c
#include <stdio.h>
#include <stdlib.h>

// Write "." to stderr a whole bunch of times. Controlled the command line argument.
int main(int argc, const char *argv[]) {
  if (argc != 2)
    return 1;
  int N = atoi(argv[1]);
  for (int i = 0; i < 1024 * N; i++) {
    fprintf(stderr, ".");
  }
  return 0;
}
```

Let's give these programs a try:

``` bash
$ ./script.py ./subprocess 1 && wc -c stderr.txt 
    1024 stderr.txt
$ ./script.py ./subprocess 2 && wc -c stderr.txt
    2048 stderr.txt
$ ./script.py ./subprocess 4 && wc -c stderr.txt
    4096 stderr.txt
```

Cool. How far can we push it?

``` bash
$ ./script.py ./subprocess 32 && wc -c stderr.txt
   32768 stderr.txt
$ ./script.py ./subprocess 64 && wc -c stderr.txt
   65536 stderr.txt
$ ./script.py ./subprocess 128 && wc -c stderr.txt
```

Uh-oh. `N=128` is not terminating. Let's Ctrl-C.

```python
^CTraceback (most recent call last):
  File "/Users/carson/repos/blog/2025/08/why-wont-my-subprocess-finish/./script.py", line 10, in <module>
    if stdout_chunk := proc.stdout.readline():
                       ~~~~~~~~~~~~~~~~~~~~^^
KeyboardInterrupt
```

Looks like the executor script is getting stuck waiting on stdout. Let's figure out
where the subprocess is getting stuck.

```cpp
* thread #1, queue = 'com.apple.main-thread', stop reason = signal SIGSTOP
  * frame #0: 0x000000018f8fbbd0 libsystem_kernel.dylib`__write_nocancel + 8
    frame #1: 0x000000018f7f8884 libsystem_c.dylib`__swrite + 24
    frame #2: 0x000000018f7d935c libsystem_c.dylib`_swrite + 108
    frame #3: 0x000000018f7d73e4 libsystem_c.dylib`__sflush + 232
    frame #4: 0x000000018f7d9234 libsystem_c.dylib`__xvprintf + 296
    frame #5: 0x000000018f7d90ec libsystem_c.dylib`vfprintf_l + 156
    frame #6: 0x000000018f7d9044 libsystem_c.dylib`fprintf + 68
    frame #7: 0x00000001040784e0 subprocess`main(argc=2, argv=0x000000016bd87238) at subprocess.c:11:5
    frame #8: 0x000000018f57d924 dyld`start + 6400
```

Ah, looks the spawned process we are getting stuck in `fprintf` when trying to write "."
to stdout. Clearly there is some sort of deadlock happening here, but why?

### What do we know?

We hare hitting a deadlock when the subprocess is trying to write to stderr and the 
output collecting script is trying to read from stdout. Let's learn a bit more about
buffering!