# Builds a Docker image for NumGeom development environment
# with Ubuntu 16.04, Octave, Python3, Jupyter Notebook and Atom
#
# Authors:
# Xiangmin Jiao <xmjiao@gmail.com>

FROM fastsolve/desktop:dev
LABEL maintainer "Xiangmin Jiao <xmjiao@gmail.com>"

USER root
WORKDIR /tmp
COPY url /tmp
ADD image/bin $DOCKER_HOME/bin
RUN chown -R $DOCKER_USER:$DOCKER_GROUP $DOCKER_HOME/bin

USER $DOCKER_USER

###############################################################
# Build NumGeom for Octave
###############################################################
RUN rm -f $DOCKER_HOME/.octaverc && \
    mkdir -p $DOCKER_HOME/.config/numgeom && \
    echo " \
    addpath $DOCKER_HOME/fastsolve/ilupack4m/matlab/ilupack\n\
    run $DOCKER_HOME/fastsolve/paracoder/load_m2c.m\n\
    run $DOCKER_HOME/fastsolve/petsc4m/load_petsc.m\n\
    " > $DOCKER_HOME/.config/numgeom/startup.m && \
    \
    $DOCKER_HOME/bin/pull_numgeom && \
    $DOCKER_HOME/bin/build_numgeom && \
    \
    $DOCKER_HOME/bin/pull_numgeom2

    # $DOCKER_HOME/bin/build_numgeom2 && \
    # \
    # curl -L "$(cat /tmp/url)" | sudo bsdtar zxf - -C /usr/local --strip-components 2 && \
    # MATLAB_VERSION=$(cd /usr/local/MATLAB; ls) sudo -E /etc/my_init.d/make_aliases.sh && \
    # $DOCKER_HOME/bin/build_numgeom -matlab && \
    # $DOCKER_HOME/bin/build_numgeom2 -matlab && \
    # sudo rm -rf /usr/local/MATLAB/R*

WORKDIR $DOCKER_HOME/numgeom
USER root
