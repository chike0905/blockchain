FROM ubuntu:16.04
MAINTAINER chike <chike@sfc.wide.ad.jp>

# apt update
RUN apt update
RUN apt install -y sudo

# add sudo user
RUN groupadd -g 1000 developer && \
    useradd  -g      developer -G sudo -m -s /bin/bash chike && \
        echo 'chike:hogehoge' | chpasswd

        RUN echo 'Defaults visiblepw'             >> /etc/sudoers
        RUN echo 'chike ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

        USER chike

WORKDIR /home/chike
RUN sudo apt -y upgrade

# install pyenv
RUN sudo apt -y install git gcc make openssl libssl-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl bzip2
RUN git clone https://github.com/yyuu/pyenv.git ~/.pyenv
ENV HOME /home/chike
ENV PYENV_ROOT $HOME/.pyenv
ENV PATH $PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH

# install python
RUN pyenv install 3.6.0
RUN pyenv global 3.6.0

# for debug
RUN pip install ipython

# add apps
ADD . /home/chike/blockchain

CMD ["/bin/sh","./blockchain/exec_in_docker.sh"]
