FROM continuumio/miniconda3

WORKDIR /app

# Create the environment:
COPY environment.yml ./
COPY config.py ./
COPY promethion.mat ./
RUN conda env create -f environment.yml
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y


#Necessary for Medaka.
RUN apt-get update && apt-get install bzip2 g++ zlib1g-dev libbz2-dev liblzma-dev libffi-dev libncurses5-dev libcurl4-gnutls-dev libssl-dev curl make cmake wget python3-all-dev -y

#Clone in ConSeqUMI
RUN git clone https://github.com/JGEnglishLab/ConSeqUMI.git

#Overwrite the default config.py (The one with no path for a lamassemble "last train" file)
RUN mv config.py ConSeqUMI/src/ConSeqUMI/consensus/config.py


# Make RUN commands use the new environment:
RUN echo "conda activate conseq_env" >> ~/.bashrc
SHELL ["/bin/bash", "--login", "-c"]

RUN pip install -e ./ConSeqUMI/
RUN pip install medaka
RUN pip install pyabpoa #need this for medaka
RUN conda install -c bioconda lamassemble -y 
RUN conda install -c bioconda last==1254 -y && conda clean -afy

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "conseq_env", "conseq"]
