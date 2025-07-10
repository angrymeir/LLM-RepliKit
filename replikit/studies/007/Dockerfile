FROM python:3.12.3-slim

WORKDIR /app

# Install needed tools
RUN apt-get update && apt-get install -y \
    git \
    unar \
    && rm -rf /var/lib/apt/lists/*

# Clone repo
RUN git clone https://github.com/soarsmu/ChatGPT-VulDetection.git

# Unpack rar archive (ignore minor corrupt file errors)
RUN unar -f ChatGPT-VulDetection/ICSE-NIER-code.rar -o /app/ || true
# (Optional) clean up
RUN rm -rf ChatGPT-VulDetection
# Install dependencies
COPY requirements.txt /app/
#RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy local files
COPY replication_config.json /app/
COPY modifier.py /app/
COPY retrieval_pos_neg.pkl /app/ChatGPT_exp/
COPY run_scripts.sh /app/
RUN chmod +x /app/run_scripts.sh

# move necessary files to the correct location
RUN mkdir dataset
RUN mv /app/ICSE-NIER-code/ICSE-NIER-main/ICSE_NIER_code_share/ICSE_NIER_code_share/ChatGPT_exp/ChatGPT_on_binary_vulner_detection.py /app/
RUN mv /app/ICSE-NIER-code/ICSE-NIER-main/ICSE_NIER_code_share/ICSE_NIER_code_share/dataset/test_for_codexglue_binary.json /app/dataset/
RUN mv /app/ICSE-NIER-code/ICSE-NIER-main/ICSE_NIER_code_share/ICSE_NIER_code_share/dataset/train_for_codexglue_binary.json /app/dataset/