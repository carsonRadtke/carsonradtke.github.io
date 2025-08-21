// $ cc -o subprocess subprocess.c

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
