### Basic Docker Usage

A short tutorial on Docker. If you don't know what Docker is,
[read this first](FIXME).

This tutorial uses Docker from the command line so you
should be familiar with the Linux command line. In general, you won't
be using Docker as a full-blown development environment. You can, of
course, but it's better to use Linux directly, and use Docker for
testing and deployment. Rather, it's more like running `make`
from the shell than from your IDE. The
[Docker Hub](https://hub.docker.com) is quite primitive unlike
say, [GitHub](https://github.com) so that's another reason
to be familiar with the Docker command line.

At RadiaSoft, we don't usually invoke Docker directly. It's a
great tool for isolating execution environments, but it's
a bit like booting a machine every time you want to run a
few commands. It's not super inconvient, just enough so
that we wrap it up in
[some simple scripts](https://github.com/radiasoft/containers)
so you don't have to rememer to do
all the things we'll be talking about below.

There are of course more advanced automation tools for Docker. They
may be more suitable for you, but at RadiaSoft, we deal with lots of
custom build systems for physics codes and supercomputers so there's
no COTS automation for this, unfortunately. Also, it's useful to know
what's going on under the covers, which this tutorial gets into in
quite some detail.

Before getting started, you'll need to
[install Docker](FIXME).
We also recommend you run Docker as an
[ordinary user](FIXME)
since it's easy to confuse executing commands on the host as root and
inside a docker container, which boots into root. Installation is not
part of this tutorial, since that's system dependent.  The cool part
is that once you've installed it, you now have the ability to run
whatever flavor of Linux -- GNU, technically -- that suits your fancy
and application requirements.

For simplicity and speed of download, we'll use the
[Busybox](https://hub.docker.com/_/busybox/)
is a very small image
image from the [Docker Hub](https://hub.docker.com),
which is a very tiny (less than one megabyte) distro that is
used by many embedded devices such as WiFi routers and set-top
boxes. It's got `bash` and a simple `httpd`, which will let us
demonstrate all the features you probably need.

With all those caveats out of the way, let's play with Docker!

#### Basic Execution

`docker run` downloads the image, unpacks it, boots the container,
and runs a shell command:

```bash
$ docker run busybox echo Hello, World!
Unable to find image 'busybox:latest' locally
latest: Pulling from library/busybox
library/busybox:latest: The image you are pulling has been verified. Important: image verification is a tech preview feature and should not be relied on to provide security.
Digest: sha256:3ebe07818fc2a8001cbb672b878ab0b81f047066093bb9c3f05600514710b921
Status: Downloaded newer image for busybox:latest
Hello, World!
```

Next time you run, it's faster, because all Docker daemon has to
do is boot the container and run the command:

```bash
$ time docker run busybox echo Hello, World!
Hello, World!

real	0m0.664s
user	0m0.031s
sys	    0m0.034s
```

You can run an interactive shell by passing the flags `-t` to allocate a pseudo-tty
and `-i` to run interactively (keep stdin open):


```bash
$ docker run -i -t busybox sh
/ # echo hello
hello
/ # ls
bin   dev   etc   home  proc  root  sys   tmp   usr   var
/ # ls /etc
group        hostname     hosts        mtab         passwd       resolv.conf  shadow
```

Running commands in a Docker container is much like ssh'ing into
a virtual machine. It's also similar to running an interactive shell
on the host machine. However, there are subtle differences, for example,
control-P is the escape character in interactive mode, and you can't
change it. If you are running the container in an Emacs shell window,
it can be annoying to type control-P twice to go up one line.

#### Root User

The `#` bash prompt indicates you are running as root
inside the container. That has some important consequences,
which we'll discuss later. For now, it's practical, since you
almost always have to install files only accessible as root,
for example:

```bash
/ # touch /etc/my-app-config
/ # ls /etc
group          hosts          my-app-config  resolv.conf
hostname       mtab           passwd         shadow
```

This just added a file to `/etc` as root, which is something
many apps require. In a freshly booted container, you are
going to have to configure it to do something other than
run `sh`. So put on your sysadmin hat, and we'll configure
a tiny application.

Quick aside. Busybox is truly a minimal distro. When was the
last time you administered a system which has a `/etc`
with only eight files? Neat.

#### Images and Containers

Docker has two distinct objects: *images* and *containers*.
An image is just a tarball that Docker unpacks and
instantiates as a container (process).  Images are static
entities. Containers, OTOH, are either running (`Up`)
or stopped (`Exited`). You use `docker ps` to see what
the state of *all* containers on the host are:

```bash
$ docker ps -a
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS                      PORTS               NAMES
60e4e25ef570        busybox             "sh"                     38 minutes ago      Up 38 minutes                                   serene_payne
fc213ce6cd24        busybox             "echo Hello, World!"     39 minutes ago      Exited (0) 39 minutes ago                       cranky_noyce
32b3f2e47b87        busybox             "echo Hello, World!"     40 minutes ago      Exited (0) 40 minutes ago                       goofy_torvalds
```
Here you see that we ran Docker three times: two echo commands
and one interactive sh that's still running. You can see that
Docker doesn't clean up stopped containers. You can restart them,
but unlike images, you can't change the command that will be run.
Let's restart `goofy_torvalds`:

```bash
$ docker start -a -i cranky_noyce
Hello, World!
```

Not very interesting, because `echo` isn't a useful
application. Alternatively, you might be running some physics
simulation, which failed due to a configuration issue, and the `start`
command might be useful to restart it. That's not the typical
use, but it is definitely useful for debugging.

One thing to note is that the `docker` command is a front-end
that sends messages to the docker daemon. Therefore, `ps -a`
shows all runnning and stopped containers on the machine, and
you can't know which (host) user started which container. Just
something to keep in mind when running Docker on a shared computer.

You can also list all the images on the host computer with
the `images` command:

```bash
$ docker images
[2.7.10;@v docker]$ docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
busybox             latest              0064fda8c45d        40 minutes ago      1.113
M
```

#### Containers are Ephemeral

One strange thing about Docker containers is that they
are ephemeral. As shown above, each time you run an
image it creates a new container. That container is
an exact copy of the image. (Actually, it is the image,
but we'll get to that in a bit.)

Starting from exactly what's in the image is very
useful for testing. However, it can be confusing at times
so that's why it's emphasized here. Here's a demonstration
of the effect:

```bash
$ docker run -i -t busybox sh -c 'ls; touch aaa; ls'
bin   dev   etc   home  proc  root  sys   tmp   usr   var
aaa   bin   dev   etc   home  proc  root  sys   tmp   usr   var
$ docker run -i -t busybox sh -c 'ls; touch aaa; ls'
bin   dev   etc   home  proc  root  sys   tmp   usr   var
aaa   bin   dev   etc   home  proc  root  sys   tmp   usr   var
$
```

The first `ls` shows `/aaa` does not exist. After the `touch`
it does in the first container. In the second container, it
has to be recreated again.

#### Building Images

Images can be created with the `build` command.
You describe what you want in the image in the `Dockerfile`.
At a minimum, you need to specify the base image which
you are going to extend. We'll also specify the maintainer
of the image:

```bash
FROM busybox
MAINTAINER RadiaSoft <docker@radiasoft.net>
```

After creating this `Dockerfile`, you run `build`:

```bash
$ time docker build .
Sending build context to Docker daemon 17.41 kB
Step 0 : FROM busybox
 ---> 0064fda8c45d
Step 1 : MAINTAINER RadiaSoft <docker@radiasoft.net>
 ---> Using cache
 ---> cda15ffd2f27
Successfully built cda15ffd2f27

real	0m0.107s
user	0m0.030s
sys     0m0.033s
```

This is very fast, because Docker doesn't copy the base image.
Instead it uses
[advanced multi layered unification filesystem (aufs](https://en.wikipedia.org/wiki/Aufs)
to layer the new image on the old image. This is one of the very cool
things about Docker, because you can distribute the (large) base
system containing all the common libraries and tools infrequently with
the application image being very small and fast to distribute.

We can see our new image was created with the `images` command:

```bash
$ docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
<none>              <none>              cda15ffd2f27        8 minutes ago       1.113 MB
busybox             latest              0064fda8c45d        42 hours ago        1.113 MB
```

You see the busybox base image along with our new image (`cda15ffd2f27`).
As you can see busybox has a *repository* name of `busybox` and a *tag* of `latest`
(the default). Our new box is not identified as such, but we can run it
by its image identifier `cda15ffd2f27`:

```bash
$ docker run cda15ffd2f27 echo hello
hello
```

You'll want to give your images constants names, which you can do with
the `tag` command:

```bash
$ docker tag cda15ffd2f27 my-app
$ docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
my-app              latest              cda15ffd2f27        13 minutes ago      1.113 MB
busybox             latest              0064fda8c45d        42 hours ago        1.113 MB
```

Typically, you tag your image when you build it as follows:

```bash
$ docker build -t my-app .
docker build -t my-app .
Sending build context to Docker daemon 19.97 kB
Step 0 : FROM busybox
 ---> 0064fda8c45d
Step 1 : MAINTAINER Rob Nagler
 ---> Using cache
 ---> cda15ffd2f27
Successfully built cda15ffd2f27
```

Now, take a look at the list of images:

```bash
$ docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
my-app              latest              cda15ffd2f27        15 minutes ago      1.113 MB
busybox             latest              0064fda8c45d        42 hours ago        1.113 MB
```

Wait, what happened? Nothing. The image was rebuilt, but it had exactly the
same contents as the previous build so docker didn't do anything. This is a
bit strange, but makes a lot of sense in that docker builds are idempotent,
which makes the process of creating and running a docker image reproducible.
Docker uses the hash of the image for its ID, which is how it verifies that
nothing has changed.

#### Simple Application

A Dockerfile typically has more information than just the base box and
maintainer. You add instructions to provision the image.  You provide
configuration files with the `ADD` command, and you install them with
the `RUN` command. Here's a more complex Dockerfile:

```bash
FROM busybox
MAINTAINER Rob Nagler
ADD . /cfg
RUN chmod +x /cfg/hello-world
CMD /cfg/hello-world
```

The `ADD` instruction tells Docker to copy the contents of the build
directory (`.`) on the host to the build container (guest). Note that
`docker build` instantiates the base image (`FROM`) as a
container, which then is modified and persisted all in one step.

The `RUN` command is executed in the build container (under `sh
-c`). There can be multiple `RUN` commands in a Dockerfile, but
it's often simpler (and easier to test) a single provisioning script,
which we'll show how to do below.

The `CMD` instruction is what Docker executes after the image is
instantiated as a container. You can override the `CMD`.

We put these instructions in `Dockefile-my-app` in this repo so
we can execute the build as follows:

```bash
$ docker build -f Dockerfile-my-app -t my-app .
```

There's also a file name `Dockerfile` in the current directory so
we need to specify our uniquely named `Dockerfile-my-app`. We
tag our image `my-app` at build time so we can run our tiny
app as follows:

```bash
$ docker run my-app
Hello, World!
```

We give the image name, and `run` instantiates the image and runs the command
`/cfg/hello-world` contained in the image by default. We can override
the default command, which can be very useful for debugging images.

#### Building a Server

Docker is often used to build servers. There are many features to
support running servers, a few of which, we'll demonstrate here.

Busybox has a built in web server, which can run CGI scripts so we
can show how you would build a simple web application.

In the current directory, there are a number of other files to help
us build the web server. We're into automation so the build and
run process are scripts. Let's go through them one at a time.

##### build-httpd.sh

The build script removes the previous version of the image with
the tag `radiasoft/httpd`. It then builds the image with the
same tag:

```bash
set -e
tag=radiasoft/httpd
name=${basename "$tag")
docker rmi "$tag" >&/dev/null || true
docker build -f Dockerfile-"$name" -t "$tag" .
```

You'll see `set -e` in all RadiaSoft scripts. We believe
programs should
[fail-fast](https://en.wikipedia.org/wiki/Fail-fast)
before they run amock, possibly doing some real damage.

The `$tag` assignment is followed by an assignment of the
`$name` which is assigned the tag's base name `httpd`. This
is used to identify `Dockerfile-httpd`.

##### Dockerfile-httpd

For tutorial purposes, we'll build the image `radiasoft/httpd`
off of the `my-app` image we created earlier.

This new Dockerfile uses a new instruction `ENV` to specify environment
variables, which are set both in the build and run containers.

```bash
FROM my-app
MAINTAINER Radiasoft <docker@radiasoft.net>
ENV HTTPD_USER=www-data
ENV HTTPD_ROOT=/www
ADD . /cfg2
RUN sh /cfg2/provision-httpd.sh
CMD httpd -f -h $HTTPD_ROOT -u $HTTPD_USER:$HTTPD_USER -p $HTTPD_PORT
```

We use two environment variablles `$HTTPD_USER` and `$HTTPD_ROOT`
to share the configuration between the provisioner and the `CMD`.

The default command is `httpd`, which is run in foreground (not daemon)
mode by passing `-f`. This is
with user `www-data`
in the directory `/www`, which we'll populate with a few
files.





#### Config


The main difference between Linux container and a virtual
machine is that you are sharing the same kernel.

The container seems like a virtual machine, but it isn't.
The con are sharing the same

 except for the fact that you are sharing the same running
 Linux kernel as the host machine:

Running commands in a Docker container is much like using a virtual
machine except for the fact that you are sharing the same running
Linux kernel as the host machine:

```bash
/ # uname -a
Linux fc213ce6cd24 4.1.8-100.fc21.x86_64 #1 SMP Tue Sep 22 12:13:06 UTC 2015 x86_64 GNU/Linux
```

This command run in the container is talking to the same exact
kernel as the host computer, which in this case is part of the
Fedora 21 distro. You can see that by the `fc21` in the kernel
distro so when you run `uname` on the host:

```bash
$ uname -a
Linux v 4.1.8-100.fc21.x86_64 #1 SMP Tue Sep 22 12:13:06 UTC 2015 x86_64 x86_64 x86_64 GNU/Linux
```

There are a few subtleties here. The hostname is different. The Docker
container's hostname is `fc213ce6cd24`, and the host computer's hostname is `v`.
Fedora's `uname` provides more information than Busybox's.

You can run a container in background with `-d`:

```bash
$ docker run -d busybox sleep 100
766ef35f7c3e24738e6bc6ce0b0ca635f6fb6bae787e817cf44f72f4300f7f40
$ docker ps
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES
766ef35f7c3e        busybox             "sleep 100"         7 seconds ago       Up 6 seconds                            compassionate_ritchie
$ docker stop 766ef35f7c3e24738e6bc6ce0b0ca635f6fb6bae787e817cf44f72f4300f7f40
766ef35f7c3e24738e6bc6ce0b0ca635f6fb6bae787e817cf44f72f4300f7f40
```

This is how you would deploy containers on a server. You can also run a container
with `&` like a normal Linux process.

#### Building an Image

#### Running a Web Server

Continuing along with the busybox example, we can introduce

docker run -p 8000:80 busybox httpd -f
mkdir -p /www/cgi-bin
chown www-data:www-data -R /www

do a ps ax to show the process is seen on the host

xu  uname

*** docker logs




<html>Hello $REMOTE_ADDR
www-data:www-data
/www/cgi-bin/hello-world

We'll also use a provisioning script.

LS_COLORS=none

'<html>Hello, World!</html>'> index.html

```bash

```bash
$ docker run -d -p 8000:8000 fedora:21 python -m SimpleHTTPServer 8000
```

```bash
$ curl http://127.0.0.1:8000
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><html>
<title>Directory listing for /</title>
<body>
<h2>Directory listing for /</h2>
<hr>
<ul>
<li><a href=".dockerenv">.dockerenv</a>
<li><a href=".dockerinit">.dockerinit</a>
<li><a href="bin/">bin@</a>
<li><a href="boot/">boot/</a>
[...snip...]
```

#### Persistence

Docker allows you to save the state of a modified container into an image.
This is not the usual way of managing Docker containers, because
people usually build docker images using docker build.

sirepo -v

-p

Each command above created a new container from the same image. You
can list the containers as follows:

```bash
$ docker ps -a
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS                      PORTS               NAMES
c241a98d1624        busybox             "sh -c 'ls; touch aaa"   9 seconds ago       Exited (0) 8 seconds ago                        insane_goldstine
f39885258525        busybox             "sh -c 'ls; touch aaa"   10 seconds ago      Exited (0) 9 seconds ago                        nostalgic_bartik
53d12df6c5a9        busybox             "sh"                     19 seconds ago      Exited (0) 17 seconds ago                       suspicious_raman
d19ee53583dc        busybox             "echo Hello, World!"     24 seconds ago      Exited (0) 23 seconds ago                       nostalgic_jones
e1083c36d044        busybox             "echo Hello, World!"     32 seconds ago      Exited (0) 30 seconds ago                       compassionate_rosalind
```




#### Restarting containers

However, a container is saved while it is around.

#### Build

You need a `Dockerfile`. An [example](https://github.com/robnagler/container-play/blob/master/fedora-min) is in this directory.

Look at your list of images:

```bash
docker images
```

#### Cleaning up

docker ps -a -q
docker rm $force $x

fi
x=$(docker images --filter dangling=true -q)
    docker rm $force $x
    docker rmi $force $x


touching root files in the container
