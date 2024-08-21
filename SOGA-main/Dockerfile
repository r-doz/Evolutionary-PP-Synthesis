FROM --platform=linux/amd64 ubuntu:22.04

# Set timezone environment variable
RUN ln -snf /usr/share/zoneinfo/America/New_York /etc/localtime && echo America/New_York > /etc/timezone

#SHELL ["/bin/bash", "-c"]
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Install any additional packages that your application requires
RUN apt-get update && apt-get install -y software-properties-common
RUN apt install nano build-essential pip nano curl wget libatlas-base-dev libblas3 liblapack3 liblapack-dev libblas-dev gfortran git gcc default-libmysqlclient-dev pkg-config qtbase5-dev qt5-qmake libsqlite3-dev python-setuptools llvm-dev texlive-latex-base texlive-fonts-recommended texlive-fonts-extra texlive-lang-greek texlive-science -y

# Copy your application code into the image
COPY . /root/SOGA

# Set the working directory
WORKDIR /root/SOGA
RUN pip install -U pip
RUN pip install --upgrade pip setuptools
RUN pip install --verbose -r  requirements.txt 

#build PSI
WORKDIR /root/SOGA/tools
#RUN git clone https://github.com/eth-sri/psi.git
WORKDIR /root/SOGA/tools/psi
RUN ./dependencies-release.sh && ./build-release.sh

WORKDIR /root/SOGA