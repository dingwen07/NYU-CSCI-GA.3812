// ignore_sigterm.c
// A simple program that waits for EOF on stdin or signals,
// This code has nothing to do with robothon.

#include <stdio.h>
#include <unistd.h>
#include <signal.h>
#include <poll.h>
#include <string.h>
#include <errno.h>

volatile sig_atomic_t sig_received = 0;

static void sig_handler(int sig) {
    sig_received = sig;
}

int main(int argc, char *argv[]) {
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = sig_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;

    int watch_sigs[] = { SIGHUP, SIGINT, SIGTERM, SIGQUIT, SIGUSR1, SIGUSR2, SIGALRM };
    for (size_t i = 0; i < sizeof(watch_sigs)/sizeof(watch_sigs[0]); ++i) {
        sigaction(watch_sigs[i], &sa, NULL);
    }

    printf("%s pid=%d: waiting for EOF on stdin or signals (prints but does not exit)\n", argv[0], getpid());
    fflush(stdout);

    struct pollfd pfd = {
        .fd = STDIN_FILENO,
        .events = POLLIN | POLLPRI
    };

    for (;;) {
        int ret = poll(&pfd, 1, 2000); // 2s timeout to periodically check signals
        if (ret < 0) {
            if (errno == EINTR) {
                // interrupted by signal; fall through to check sig_received
            } else {
                perror("poll");
            }
        } else if (ret > 0) {
            if (pfd.revents & (POLLIN | POLLPRI)) {
                char buf[256];
                ssize_t n = read(STDIN_FILENO, buf, sizeof(buf));
                if (n < 0) {
                    perror("read");
                } else if (n == 0) {
                    sleep(1); // EOF received; just wait
                } else {
                    // Data received; echo a short notice
                    printf("Read %zd bytes from stdin (not exiting)\n", n);
                    fflush(stdout);
                }
            }
            if (pfd.revents & POLLHUP) {
                printf("POLLHUP on stdin detected\n");
                fflush(stdout);
            }
        }

        if (sig_received) {
            int s = sig_received;
            sig_received = 0;
            const char *name = strsignal(s);
            if (!name) name = "Unknown";
            printf("Signal received: %d (%s)\n", s, name);
            fflush(stdout);
            if (s == SIGINT) {
                printf("SIGINT received, exiting.\n");
                fflush(stdout);
                break;
            }
        }
    }

    return 0;
}
