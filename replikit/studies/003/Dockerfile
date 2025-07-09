FROM francescosovrano/dox4p2bcompliance:latest

# Install Python 3.11
RUN apt-get update && apt-get install -y \
    wget build-essential libssl-dev zlib1g-dev libncurses5-dev \
    libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev \
    libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev tk-dev

RUN wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz && \
    tar xvf Python-3.11.9.tgz && \
    cd Python-3.11.9 && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make altinstall && \
    cd .. && rm -rf Python-3.11.9*

# Set python and pip aliases
RUN ln -s /usr/local/bin/python3.11 /usr/bin/python && \
    ln -s /usr/local/bin/pip3.11 /usr/bin/pip

WORKDIR /usr/src/app

RUN rm -rf expert_vs_gpt_vs_doxpy/code/gpt_based_approach/marketplaces/*.pkl
RUN rm -rf expert_vs_gpt_vs_doxpy/code/gpt_based_approach/search_engines/*.pkl
RUN rm -rf expert_vs_gpt_vs_doxpy/data/assessment_results/chatgpt-based/GPT-4/*.csv
RUN rm -rf expert_vs_gpt_vs_doxpy/code/data_analysis/expert_vs_tools/tables/*.csv

COPY run_automated_assessments.sh /usr/src/app

RUN chmod +x run_automated_assessments.sh

COPY convert_results.py /usr/src/app

RUN bash -c '.env/bin/pip install seaborn'
RUN bash -c 'pip3.11 install numbers_parser pandas'