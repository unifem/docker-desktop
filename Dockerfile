# Builds a Docker image for Unifem development environment
# with Ubuntu 16.04, Octave, Python3, Jupyter Notebook and Atom
#
# Authors:
# Xiangmin Jiao <xmjiao@gmail.com>

FROM numgeom/desktop:dev
LABEL maintainer "Xiangmin Jiao <xmjiao@gmail.com>"

USER root
WORKDIR /tmp
COPY url /tmp
ADD image/bin $DOCKER_HOME/bin
RUN chown -R $DOCKER_USER:$DOCKER_GROUP $DOCKER_HOME/bin

USER $DOCKER_USER

###############################################################
# Build Unifem for Octave
###############################################################
RUN rm -f $DOCKER_HOME/.octaverc && \
    mkdir -p $DOCKER_HOME/.config/unifem && \
    echo " \
    addpath $DOCKER_HOME/fastsolve/ilupack4m/matlab/ilupack\n\
    run $DOCKER_HOME/fastsolve/paracoder/load_m2c.m\n\
    run $DOCKER_HOME/fastsolve/petsc4m/load_petsc.m\n\
    " > $DOCKER_HOME/.config/unifem/startup.m && \
    \
    $DOCKER_HOME/bin/pull_unifem && \
    $DOCKER_HOME/bin/build_unifem

WORKDIR $DOCKER_HOME/unifem
USER root
