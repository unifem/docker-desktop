# Builds a Docker image for Unifem development environment
# with Ubuntu 16.04, Octave, Python3, Jupyter Notebook and Atom
#
# Authors:
# Xiangmin Jiao <xmjiao@gmail.com>

FROM numgeom/desktop:dev
LABEL maintainer "Xiangmin Jiao <xmjiao@gmail.com>"

USER root
WORKDIR /tmp
ADD image/home $DOCKER_HOME/

ARG SSHKEY_ID=secret
ARG MFILE_ID=secret

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
         libnss3 && \
    pip3 install -U \
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
         urllib3 \
         \
         PyQt5 \
         spyder && \
    rm -rf /var/lib/apt/lists/* /tmp/* && \
    chown -R $DOCKER_USER:$DOCKER_GROUP $DOCKER_HOME

###############################################################
# Build Unifem for Octave
###############################################################
USER $DOCKER_USER

RUN gd-get-pub -o - $(sh -c "echo '$SSHKEY_ID'") | tar xf - -C $DOCKER_HOME && \
    ssh-keyscan -H github.com >> $DOCKER_HOME/.ssh/known_hosts && \
    rm -f $DOCKER_HOME/.octaverc && \
    mkdir -p $DOCKER_HOME/.unifem && \
    echo " \
    run $DOCKER_HOME/fastsolve/ilupack4m/startup.m\n\
    run $DOCKER_HOME/fastsolve/paracoder/startup.m\n\
    run $DOCKER_HOME/fastsolve/petsc4m/startup.m\n\
    " > $DOCKER_HOME/.unifem/startup.m && \
    \
    $DOCKER_HOME/bin/pull_unifem && \
    $DOCKER_HOME/bin/build_unifem && \
    rm -f $DOCKER_HOME/.ssh/id_rsa*


    # gd-get-pub $(sh -c "echo '$MFILE_ID'") | \
    #     sudo bsdtar zxf - -C /usr/local --strip-components 2 && \
    # MATLAB_VERSION=$(cd /usr/local/MATLAB; ls) sudo -E /etc/my_init.d/make_aliases.sh && \
    # sudo rm -rf /usr/local/MATLAB/R*


WORKDIR $DOCKER_HOME/unifem
USER root
