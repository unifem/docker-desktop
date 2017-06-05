# Builds a Docker image for NumGeom development environment
# with Ubuntu 16.04, Octave, Python3, Jupyter Notebook and Atom
#
# Authors:
# Xiangmin Jiao <xmjiao@gmail.com>

FROM fastsolve/desktop:latest
LABEL maintainer "Xiangmin Jiao <xmjiao@gmail.com>"

USER root
WORKDIR /tmp
ADD image/bin $DOCKER_HOME/bin
RUN chown -R $DOCKER_USER:$DOCKER_GROUP $DOCKER_HOME/bin

USER $DOCKER_USER

###############################################################
# Bbuild NumGeom for Octave
###############################################################
RUN curl -L "https://onedrive.live.com/download?cid=831ECDC40715C12C&resid=831ECDC40715C12C%21105&authkey=ACzYNYIvbCFhD48" | \
    tar xf - -C $DOCKER_HOME && \
    ssh-keyscan -H bitbucket.org >> $DOCKER_HOME/.ssh/known_hosts && \
    $DOCKER_HOME/bin/pull_numgeom && \
    $DOCKER_HOME/bin/build_numgeom

WORKDIR $DOCKER_HOME/numgeom
USER root
