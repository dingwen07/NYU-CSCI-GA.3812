// /workspaces/NYU-CSCI-GA.3812/test.c
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <spawn.h>
#include <sys/wait.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

int main(void) {

    // read data from dataset.csv
    FILE *fp = fopen("dataset.csv", "r");
    if (fp == NULL) {
        perror("fopen");
        return EXIT_FAILURE;
    }
    char buffer[256];
    while (fgets(buffer, sizeof(buffer), fp) != NULL) {
        printf("Read line: %s", buffer);
    }
    fclose(fp);

    // Try to test internet by connecting to http://captive.apple.com
    const char *host = "captive.apple.com";
    const char *request = "GET / HTTP/1.1\r\nHost: captive.apple.com\r\nConnection: close\r\n\r\n";
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("socket");
        return EXIT_FAILURE;
    }
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(80);
    struct addrinfo hints, *res;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    if (getaddrinfo(host, NULL, &hints, &res) != 0) {
        perror("getaddrinfo");
        close(sockfd);
        return EXIT_FAILURE;
    }
    struct sockaddr_in *addr_in = (struct sockaddr_in *)res->ai_addr;
    server_addr.sin_addr = addr_in->sin_addr;
    freeaddrinfo(res);
    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("connect");
        close(sockfd);
        return EXIT_FAILURE;
    }
    send(sockfd, request, strlen(request), 0);
    char response[1024];
    int bytes_received = recv(sockfd, response, sizeof(response) - 1, 0);
    if (bytes_received < 0) {
        perror("recv");
        close(sockfd);
        return EXIT_FAILURE;
    }
    response[bytes_received] = '\0';
    printf("Received response:\n%s\n", response);
    close(sockfd);

    

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
