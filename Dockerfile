# Builds a Docker image for Unifem development environment
# with Ubuntu 16.04, Octave, Python3, Jupyter Notebook and Atom
#
# Authors:
# Xiangmin Jiao <xmjiao@gmail.com>

FROM numgeom/desktop:latest
LABEL maintainer "Xiangmin Jiao <xmjiao@gmail.com>"

USER root
WORKDIR /tmp
ADD image/bin $DOCKER_HOME/bin

RUN pip3 install -U \
         numpy \
         matplotlib \
         sympy \
         scipy \
         pandas \
         nose \
         sphinx \
         flufl.lock \
         ply \
         pytest \
         six \
         \
         urllib3 && \
    chown -R $DOCKER_USER:$DOCKER_GROUP $DOCKER_HOME/bin

###############################################################
# Build Unifem for Octave
###############################################################
USER $DOCKER_USER

RUN rm -f $DOCKER_HOME/.octaverc && \
    mkdir -p $DOCKER_HOME/.config/unifem && \
    echo " \
    addpath /usr/local/ilupack4m/matlab/ilupack\n\
    run /usr/local/paracoder/load_m2c.m\n\
    run /usr/local/petsc4m/load_petsc.m\n\
    " > $DOCKER_HOME/.config/unifem/startup.m && \
    \
    $DOCKER_HOME/bin/pull_unifem && \
    $DOCKER_HOME/bin/build_unifem

WORKDIR $DOCKER_HOME/unifem
USER root
