# Builds a Docker image for FastSolve development environment
# with Ubuntu 16.04, Octave, Python3, Jupyter Notebook and Atom
#
# Authors:
# Xiangmin Jiao <xmjiao@gmail.com>

FROM fastsolve/desktop:latest
LABEL maintainer "Xiangmin Jiao <xmjiao@gmail.com>"

USER root
WORKDIR /tmp

# Install Atom and packages
RUN add-apt-repository ppa:webupd8team/atom && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        ddd \
        electric-fence \
        valgrind \
        \
        meld \
        atom \
        clang-format && \
    curl -L https://goo.gl/ExjLDP | bsdtar zxf - -C /usr/local --strip-components 2 && \
    ln -s -f /usr/local/MATLAB/R2017a/bin/glnxa64/mlint /usr/local/bin && \
    apt-get clean && \
    pip3 install -U \
         autopep8 \
         flake8 \
         PyQt5 \
         spyder && \
    apm install \
        language-cpp14 \
        language-matlab \
        language-fortran \
        language-docker \
        autocomplete-python \
        autocomplete-fortran \
        git-plus \
        merge-conflicts \
        split-diff \
        gcc-make-run \
        platformio-ide-terminal \
        intentions \
        busy-signal \
        linter-ui-default \
        linter \
        linter-gcc \
        linter-gfortran \
        linter-flake8 \
        linter-matlab \
        dbg \
        output-panel \
        dbg-gdb \
        python-debugger \
        auto-detect-indentation \
        python-autopep8 \
        clang-format && \
    rm -rf /var/lib/apt/lists/* && \
    chown -R $DOCKER_USER:$DOCKER_GROUP $DOCKER_HOME

WORKDIR $DOCKER_HOME
