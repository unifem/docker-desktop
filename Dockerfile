# Builds a Docker image with Ubuntu 16.04, Octave, Python3 and Jupyter Notebook
# for NumGeom
#
# Authors:
# Xiangmin Jiao <xmjiao@gmail.com>

FROM fastsolve/desktop:latest
LABEL maintainer "Xiangmin Jiao <xmjiao@gmail.com>"

USER root
WORKDIR /tmp

########################################################
# Customization for user
########################################################
ARG NG_USER=numgeom
ARG OLD_USER=$DOCKER_USER

ENV DOCKER_USER=$NG_USER \
    DOCKER_GROUP=$NG_USER \
    DOCKER_HOME=/home/$NG_USER \
    HOME=/home/$NG_USER

RUN usermod -l $DOCKER_USER -d $DOCKER_HOME -m $OLD_USER && \
    groupmod -n $DOCKER_USER $OLD_USER

WORKDIR $DOCKER_HOME

ENTRYPOINT ["/sbin/my_init","--quiet","--","/sbin/setuser","numgeom","/bin/bash","-l","-c"]
CMD ["$DOCKER_SHELL","-l","-i"]
