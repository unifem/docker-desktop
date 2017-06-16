#!/usr/bin/env python

"""
Launch a Docker image with Ubuntu and LXDE window manager, and
automatically open up the URL in the default web browser.
"""

# Author: Xiangmin Jiao <xmjiao@gmail.com>

from __future__ import print_function  # Only Python 2.x

import sys
import subprocess
import time

APP = "unifem"


def parse_args(description):
    "Parse command-line arguments"

    import argparse

    # Process command-line arguments
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-i', '--image',
                        help='The Docker image to use. ' +
                        'The default is ' + APP + '/desktop.',
                        default=APP + "/desktop")

    parser.add_argument('-t', '--tag',
                        help='Tag of the image. The default is dev. ' +
                        'If the image already has a tag, its tag prevails.',
                        default="dev")

    parser.add_argument('-m', '--matlab', nargs='?',
                        metavar='VERSION',
                        help='Specify MATLAB version. Supported versions ' +
                        'include R2016b or R2017a. The default is R2017a.',
                        const="R2017a", default="")

    parser.add_argument('-v', '--volume',
                        help='A data volume to be mounted at ~/' + APP + '. ' +
                        'The default is ' + APP + '_src.',
                        default=APP + "_src")

    parser.add_argument('-p', '--pull',
                        help='Pull the latest Docker image. ' +
                        'The default is not to pull.',
                        action='store_true',
                        default=False)

    parser.add_argument('-r', '--reset',
                        help='Reset configurations to default.',
                        action='store_true',
                        default=False)

    parser.add_argument('-c', '--clear',
                        help='Clear the source tree and use the precompiled version in image.',
                        action='store_true',
                        default=False)

    parser.add_argument('-d', '--detach',
                        help='Run in background and print container id',
                        action='store_true',
                        default=False)

    parser.add_argument('-s', '--size',
                        help='Size of the screen. The default is to use ' +
                        'the current screen size.',
                        default="")

    parser.add_argument('-n', '--no-browser',
                        help='Do not start web browser',
                        action='store_true',
                        default=False)

    parser.add_argument('-a', '--args',
                        help='All the arguments after -a will be passed to the ' +
                        '"docker run" command. Useful for specifying ' +
                        'resources and environment variables.',
                        nargs=argparse.REMAINDER)

    args = parser.parse_args()

    # Append tag to image if the image has no tag
    if args.image.find(':') < 0:
        args.image += ':' + args.tag

    return args


def random_ports(port, n):
    """Generate a list of n random ports near the given port.

    The first 5 ports will be sequential, and the remaining n-5 will be
    randomly selected in the range [port-2*n, port+2*n].
    """
    import random

    for i in range(min(5, n)):
        yield port + i
    for i in range(n - 5):
        yield max(1, port + random.randint(-2 * n, 2 * n))


def id_generator(size=6):
    """Generate a container ID"""
    import random
    import string

    chars = string.ascii_lowercase
    return APP + "-" + (''.join(random.choice(chars) for _ in range(size)))


def find_free_port(port, retries):
    "Find a free port"
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    for prt in random_ports(port, retries + 1):
        try:
            sock.bind(("127.0.0.1", prt))
            sock.close()
            return prt
        except socket.error:
            continue

    print("Error: Could not find a free port.")
    sys.exit(-1)


def wait_net_service(port, timeout=30):
    """ Wait for network service to appear.
    """
    import socket

    for _ in range(timeout * 10):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("127.0.0.1", port))
        except socket.error:
            sock.close()
            time.sleep(0.1)
            continue
        else:
            sock.close()
            time.sleep(2)
            return True


def get_screen_resolution():
    """Obtain the local screen resolution."""

    try:
        if sys.version_info.major > 2:
            import tkinter as tk
        else:
            import Tkinter as tk

        root = tk.Tk()
        root.withdraw()
        width, height = root.winfo_screenwidth(), root.winfo_screenheight()

        return str(width) + 'x' + str(height)
    except:
        return ""


def download_matlab(version, user, image, volumes):
    """Download MATLAB if not yet installed"""

    installed = subprocess.check_output(["docker", "run", "--rm"] +
                                        volumes +
                                        [image,
                                         'if [ -e "/usr/local/MATLAB/' +
                                         version + '/installed" ]; ' +
                                         'then echo "installed"; fi'])

    if installed.find(b"installed") < 0:
        # Downloading software using Google authentication
        try:
            print('Authenticating for MATLAB intallation...')
            p = subprocess.Popen(["docker", "run", "--rm", '-ti'] + volumes +
                                 [image, "gd-auth -n"],
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)

            # Monitor the stdout to extract the URL
            for line in iter(p.stdout.readline, ""):
                ind = line.find("https://accounts.google.com")
                if ind >= 0:
                    # Open browser if found URL
                    print('Log in with your authorized Google account in the ' +
                          'webbrowser to get verification code.')
                    if not args.no_browser:
                        webbrowser.open(line[ind:-1])
                    else:
                        print('Open browswe at URL:')
                        print(line[ind:-1])

                    sys.stdout.write('\r\nEnter verification code: ')
                    sys.stdout.flush()
                    break

            if p.wait() != 0:
                raise BaseException

            # Downloading MATLAB software
            print("\nDownloading MATLAB...")
            cmd = "gd-get -p 0ByTwsK5_Tl_PcFpQRHZHcTM1VW8 " + version + \
                "_glnx64_nohelp.tgz | sudo tar zxf - -C /usr/local --delay-directory-restore " + \
                "--warning=no-unknown-keyword --strip-components 2 && " + \
                "sudo chown -R " + user + ":" + user + \
                " /usr/local/MATLAB/" + version + "/licenses && " + \
                "sudo touch /usr/local/MATLAB/" + version + "/installed && " + \
                "(gd-get -p 0ByTwsK5_Tl_PcFpQRHZHcTM1VW8 licenses.tgz | " + \
                "sudo bsdtar zxf - -C /usr/local/MATLAB/" + version + " || true)"

            err = subprocess.call(["docker", "run", "--rm", "-ti"] +
                                  volumes + ["-w", "/tmp/", image, cmd])
        except BaseException:
            err = -1

        if err:
            print("Failed to download MATLAB. Please rerun " + sys.argv[0] +
                  " with the -r option and use a valid Google account.")
            sys.exit(err)


def handle_interrupt(container):
    """Handle keyboard interrupt"""
    try:
        print("Press Ctrl-C again to stop the server: ")
        time.sleep(5)
        print('Invalid response. Resuming...')
    except KeyboardInterrupt:
        print('*** Stopping the server.')
        subprocess.Popen(["docker", "exec", container,
                          "killall", "startvnc.sh"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sys.exit(0)


if __name__ == "__main__":
    import os
    import webbrowser
    import platform

    args = parse_args(description=__doc__)

    pwd = os.getcwd()
    homedir = os.path.expanduser('~')

    if platform.system() == "Linux":
        if subprocess.check_output(['groups']).find(b'docker') < 0:
            print('You are not a member of the docker group. Please add')
            print('yourself to the docker group using the following command:')
            print('   sudo addgroup $USER docker')
            print('Then, log out and log back in before you can use Docker.')
            sys.exit(-1)
        uid = str(os.getuid())
        if uid == '0':
            print('You are running as root. This is not safe. ' +
                  'Please run as a regular user.')
            sys.exit(-1)
    else:
        uid = ""

    try:
        img = subprocess.check_output(['docker', 'images', '-q', args.image])
    except:
        print("Docker failed. Please make sure docker was properly " +
              "installed and has been started.")
        sys.exit(-1)

    if args.pull or not img:
        try:
            err = subprocess.call(["docker", "pull", args.image])
        except BaseException:
            err = -1

        if err:
            sys.exit(err)

        # Delete dangling image
        if img and subprocess.check_output(['docker', 'images', '-f',
                                            'dangling=true',
                                            '-q']).find(img) >= 0:
            subprocess.Popen(["docker", "rmi", "-f", img.decode('utf-8')[:-1]])

    # Create directory .ssh if not exist
    if not os.path.exists(homedir + "/.ssh"):
        os.mkdir(homedir + "/.ssh")

    docker_home = subprocess.check_output(["docker", "run", "--rm",
                                           args.image,
                                           "echo $DOCKER_HOME"]). \
        decode('utf-8')[:-1]
    user = docker_home[6:]

    if args.reset:
        subprocess.check_output(["docker", "volume", "rm", "-f",
                                 APP + "_config"])

    volumes = ["-v", pwd + ":" + docker_home + "/shared",
               "-v", APP + "_config:" + docker_home + "/.config",
               "-v", homedir + "/.ssh" + ":" + docker_home + "/.ssh"]

    # Copy .gitconfig if exists on host and is newer than that in image
    if os.path.isfile(homedir + "/.gitconfig"):
        subprocess.check_output(["docker", "run", "--rm", '-t'] + volumes +
                                ["-v", homedir + "/.gitconfig" +
                                 ":" + docker_home + "/.gitconfig_host",
                                 args.image,
                                 "[[ $DOCKER_HOME/.config/git/config -nt " +
                                 "$DOCKER_HOME/.gitconfig_host ]] || " +
                                 "(mkdir -p $DOCKER_HOME/.config/git && " +
                                 "cp $DOCKER_HOME/.gitconfig_host " +
                                 "$DOCKER_HOME/.config/git/config)"])

    if args.matlab:
        volumes += ["-v", "matlab_bin:/usr/local/MATLAB/"]

        download_matlab(args.matlab, user, args.image, volumes)

    if args.volume:
        if args.clear:
            subprocess.check_output(["docker", "volume",
                                     "rm", "-f", args.volume])

        volumes += ["-v", args.volume + ":" + docker_home + "/" + APP,
                    "-w", docker_home + "/" + APP]
    else:
        volumes += ["-w", docker_home + "/shared"]
    if args.tag == "dev":
        volumes += ["-v", "fastsolve_src:" + docker_home + "/fastsolve",
                    "-v", "numgeom_src:" + docker_home + "/numgeom",
                    "-v", "numgeom2_src:" + docker_home + "/numgeom2"]
        if args.clear:
            subprocess.check_output(["docker", "volume", "rm", "-f",
                                     'fastsolve_src', 'numgeom_src', 'numgeom2_src'])

    print("Starting up docker image...")
    if subprocess.check_output(["docker", "--version"]). \
            find(b"Docker version 1.") >= 0:
        rmflag = "-t"
    else:
        rmflag = "--rm"

    # Determine size of the desktop
    if not args.size:
        size = get_screen_resolution()
        if not size:
            # Set default size and disable webbrowser
            size = "1440x900"
            args.no_browser = True
    else:
        size = args.size

    # Generate a container ID
    container = id_generator()

    envs = ["--hostname", container,
            "--env", "RESOLUT=" + size,
            "--env", "HOST_UID=" + uid]
    if args.matlab:
        envs += ["--env", "MATLAB_VERSION=" + args.matlab]

    # Start the docker image in the background and pipe the stderr
    port_vnc = str(find_free_port(6080, 50))
    subprocess.call(["docker", "run", "-d", rmflag, "--name", container,
                     "-p", "127.0.0.1:" + port_vnc + ":6080"] +
                    envs + volumes + args.args +
                    [args.image, "startvnc.sh >> " +
                     docker_home + "/.log/vnc.log"])

    wait_for_url = True

    # Wait for user to press Ctrl-C
    while True:
        try:
            if wait_for_url:
                # Wait until the file is not empty
                while not subprocess.check_output(["docker", "exec", container,
                                                   "cat", docker_home +
                                                   "/.log/vnc.log"]):
                    time.sleep(1)

                p = subprocess.Popen(["docker", "exec", container,
                                      "tail", "-F",
                                      docker_home + "/.log/vnc.log"],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     universal_newlines=True)

                # Monitor the stdout to extract the URL
                for stdout_line in iter(p.stdout.readline, ""):
                    ind = stdout_line.find("http://localhost:")

                    if ind >= 0:
                        # Open browser if found URL
                        url = stdout_line.replace(":6080/",
                                                  ':' + port_vnc + "/")
                        sys.stdout.write(url)

                        if not args.no_browser:
                            wait_net_service(int(port_vnc))
                            webbrowser.open(url[ind:-1])

                        p.stdout.close()
                        p.terminate()
                        wait_for_url = False
                        break
                    else:
                        sys.stdout.write(stdout_line)

            if args.detach:
                print('Started container ' + container + ' in background.')
                print('To stop it, use "docker stop ' + container + '".')
                sys.exit(0)

            print("Press Ctrl-C to stop the server.")

            # Wait till the container exits or Ctlr-C is pressed
            subprocess.check_output(["docker", "exec", container,
                                     "tail", "-f", "/dev/null"])
        except subprocess.CalledProcessError:
            try:
                # If Docker process no long exists, exit
                if not subprocess.check_output(['docker', 'ps',
                                                '-q', '-f',
                                                'name=' + container]):
                    print('Docker container is no longer running')
                    sys.exit(-1)
                time.sleep(1)
            except KeyboardInterrupt:
                handle_interrupt(container)

            continue
        except KeyboardInterrupt:
            handle_interrupt(container)
        except OSError:
            sys.exit(-1)
