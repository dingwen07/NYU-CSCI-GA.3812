// /workspaces/NYU-CSCI-GA.3812/test.c
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <spawn.h>
#include <sys/wait.h>

int main(void) {

    // append data to dataset.csv, mimicking tampering behavior
    FILE *fp = fopen("dataset.csv", "a");
    if (fp == NULL) {
        perror("fopen");
        return EXIT_FAILURE;
    }
    const char *new_data = "2024-01-01,12:00:00,100.0,200.0,300.0\n";
    if (fputs(new_data, fp) == EOF) {
        perror("fputs");
        fclose(fp);
        return EXIT_FAILURE;
    }
    fclose(fp);


    // use posix_spawn to launch /bin/echo
    char *argv_ps[] = { "echo", "Hello from posix_spawn!", NULL };
    char *envp_ps[] = { "PATH=/usr/bin:/bin", NULL };
    pid_t pid;
    int ret = posix_spawn(&pid, "/bin/echo", NULL, NULL, argv_ps, envp_ps);
    if (ret != 0) {
        fprintf(stderr, "posix_spawn failed: %s\n", strerror(ret));
    } else {
        int status;
        if (waitpid(pid, &status, 0) == -1) {
            fprintf(stderr, "waitpid failed: %s\n", strerror(errno));
        } else if (WIFEXITED(status)) {
            printf("posix_spawn child exited with %d\n", WEXITSTATUS(status));
        } else {
            printf("posix_spawn child terminated abnormally\n");
        }
    }

    // then use execve to launch /bin/echo
    char *argv[] = { "echo", "Hello from execve! Haha!", NULL };
    char *envp[] = { "PATH=/usr/bin:/bin", NULL };

    /* Replace the current process with /bin/echo */
    execve("/bin/echo", argv, envp);

    /* execve only returns on error */
    fprintf(stderr, "execve failed: %s\n", strerror(errno));
    return EXIT_FAILURE;
}
