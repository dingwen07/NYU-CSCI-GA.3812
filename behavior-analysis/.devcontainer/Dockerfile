# Debian base
FROM debian:stable

# Avoid user prompts
ARG DEBIAN_FRONTEND=noninteractive

# Install core development tools
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y --no-install-recommends build-essential \
    gcc g++ \
    make cmake \
    gdb valgrind strace ltrace \
    git gnupg \
    curl wget ca-certificates \
    unzip zip tar \
    pkg-config \
    python3 python3-pip python3-venv \
    net-tools iputils-ping \
    libssl-dev \
    vim nano \
    sudo

RUN apt-get install -y python3-requests python3-setuptools
RUN apt-get clean

# Create a non-root user for VS Code remote
RUN useradd -m vscode && echo "vscode ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
USER vscode

WORKDIR /workspace
