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
# Temporarily install MATLAB and build NumGeom for Octave and MATLAB
###############################################################
RUN $DOCKER_HOME/bin/pull_numgeom && \
    $DOCKER_HOME/bin/build_numgeom

# RUN $DOCKER_HOME/bin/pull_numgeom && \
#     $DOCKER_HOME/bin/build_numgeom && \
#     \
#     curl -L "$(cat /tmp/url)" | sudo bsdtar zxf - -C /usr/local --strip-components 2 && \
#     MATLAB_VERSION=$(cd /usr/local/MATLAB; ls) sudo -E /etc/my_init.d/make_aliases.sh && \
#     $DOCKER_HOME/bin/build_numgeom --matlab && \
#     sudo rm -rf /usr/local/MATLAB/R*

WORKDIR $DOCKER_HOME/numgeom
USER root
