FROM openjdk:8-jdk-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies including python3-pip
RUN apt-get update && apt-get install -y \
    git wget curl \
    default-jre \
    maven \
    python3 \
    python3-pip \
    && apt-get clean

# RUN update-alternatives --install /usr/bin/java java /usr/lib/jvm/java-8-openjdk-amd64/bin/java 1 \
#  && update-alternatives --set java /usr/lib/jvm/java-8-openjdk-amd64/bin/java

WORKDIR /experiment
RUN mkdir -p /experiment/output

# Clone RegexEval and install python deps system-wide
RUN git clone https://github.com/s2e-lab/RegexEval.git
WORKDIR /experiment/RegexEval
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt && \
    pip3 install torch==1.12.0

# Clone and setup ReScue
WORKDIR /experiment
RUN git clone https://github.com/2bdenny/ReScue.git
WORKDIR /experiment/ReScue
RUN pip3 install mysql-connector-python && \
    mvn clean install

# Clone and setup ReDoSHunter
WORKDIR /experiment
RUN git clone https://github.com/yetingli/ReDoSHunter.git
WORKDIR /experiment/ReDoSHunter
RUN mvn clean install

# Copy and add execution permission for the run script
COPY run_pipeline.sh /experiment/run_pipeline.sh
RUN chmod +x /experiment/run_pipeline.sh

WORKDIR /experiment

# default shell
CMD ["bash", "run_pipeline.sh"]
