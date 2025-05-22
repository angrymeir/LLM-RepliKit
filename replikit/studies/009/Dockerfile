# Use Ubuntu 22.04 as base
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV GO_VERSION=1.20
ENV RUST_VERSION=1.73.0
ENV PATH="/usr/local/go/bin:/root/.cargo/bin:$PATH"

# Install system tools
RUN apt-get update && apt-get install -y \
    software-properties-common \
    wget \
    curl \
    git \
    build-essential \
    lsb-release \
    apt-transport-https \
    ca-certificates \
    gnupg \
    unzip && \
    rm -rf /var/lib/apt/lists/*

# ------------------------
# Python 3.10 (default in Ubuntu 22.04)
# ------------------------
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    python3-pip && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# ------------------------
# GCC / G++ 11
# ------------------------
RUN apt-get install -y gcc-11 g++-11 && \
    update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 100 && \
    update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 100

# ------------------------
# Clang 14
# ------------------------
RUN apt-get install -y clang-14 && \
    update-alternatives --install /usr/bin/clang clang /usr/bin/clang-14 100

# ------------------------
# Java 11
# ------------------------
RUN apt-get install -y openjdk-11-jdk

# ------------------------
# Go 1.20
# ------------------------
RUN wget https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz && \
    rm go${GO_VERSION}.linux-amd64.tar.gz

# ------------------------
# Rust 1.73
# ------------------------
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y --default-toolchain ${RUST_VERSION}

# ------------------------
# .NET 7.0.14 SDK
# ------------------------
RUN wget https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install -y dotnet-sdk-7.0 && \
    rm -rf /var/lib/apt/lists/*

RUN wget https://raw.githubusercontent.com/Intelligent-CAT-Lab/PLTranslationEmpirical/refs/heads/main/requirements.txt
RUN pip3 install -r requirements.txt

# Default shell
CMD ["/bin/bash"]
