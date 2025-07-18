FROM python:3.12

ENV DEBIAN_FRONTEND=noninteractive

RUN useradd -ms /bin/bash runner
USER runner
WORKDIR /home/runner

COPY --chown=runner requirements.txt .
RUN pip install -r requirements.txt && pip freeze > requirements.txt

# get data & scripts
RUN curl https://zenodo.org/api/records/10494170/files-archive --output main41.zip && \
    unzip main41.zip && \
    rm main41.zip && \
    find . -type f -name '*.zip' -exec unzip {} \; && \
    bash -c 'rm *.zip'

# Use data provided by the authors, so we don't have to install tree sitter here
# RUN cd /home/runner/scripts && bash setup.sh

COPY --chown=runner entrypoint.sh .
ENTRYPOINT bash entrypoint.sh
