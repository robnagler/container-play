### Basic Docker Usage

A short tutorial on Docker.

#### Running a Image as a Container

The Docker Hub provides libraries, which you can just pull down and
run. [busybox](https://hub.docker.com/_/busybox/) is a very small image
(<1MB), which has the same functionality as your broadband router:

```bash
$ docker run busybox echo Hello, World!
Unable to find image 'busybox:latest' locally
latest: Pulling from library/busybox
library/busybox:latest: The image you are pulling has been verified. Important: image verification is a tech preview feature and should not be relied on to provide security.
Digest: sha256:3ebe07818fc2a8001cbb672b878ab0b81f047066093bb9c3f05600514710b921
Status: Downloaded newer image for busybox:latest
Hello, World!
```

Next time you run, it doesn't have to load so is quite fast:

```bash
$ time docker run busybox echo Hello, World!
Hello, World!

real	0m0.664s
user	0m0.031s
sys	    0m0.034s
```

And, that's running on a VirtualBox VM on my Mac. On a native linux,
it will be faster.

Run interactively, you give flags `-t` for terminal and `-i` and interactive:

```bash
$ docker run -i -t busybox sh
/ # echo hello
hello
/ # ls
bin   dev   etc   home  proc  root  sys   tmp   usr   var
```

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

#### Containers are Emphemeral

Docker has *images* and *containers*. An image is a tarball that Docker
unpacks and instantiates as a container. A container can be running (`Up`)
or stopped (`Exited`).

When you create a container from an image, it's a clean system every time:

```bash
$ docker run -i -t busybox sh -c 'ls; touch aaa; ls'
bin   dev   etc   home  proc  root  sys   tmp   usr   var
aaa   bin   dev   etc   home  proc  root  sys   tmp   usr   var
$ docker run -i -t busybox sh -c 'ls; touch aaa; ls'
bin   dev   etc   home  proc  root  sys   tmp   usr   var
aaa   bin   dev   etc   home  proc  root  sys   tmp   usr   var
$
```

The file `aaa` is not "saved" when a container exits. This is
a feature, because you get a reproducible environment on every
"boot"

#### Building an Image

You build new images off base images by creating a Dockerfile, typically
in its own directory. This is a minimal Dockerfile:

```
FROM busybox
MAINTAINER Rob Nagler
```

You build the image by specifying the path of the directory:

```bash
$ time docker build .
Sending build context to Docker daemon 17.41 kB
Step 0 : FROM busybox
 ---> 0064fda8c45d
Step 1 : MAINTAINER Rob Nagler
 ---> Using cache
 ---> cda15ffd2f27
Successfully built cda15ffd2f27

real	0m0.107s
user	0m0.030s
sys     0m0.033s
```

This is very fast, because Docker doesn't copy the base image (`FROM busybox`).
Instead it uses
[advanced multi layered unification filesystem (aufs](https://en.wikipedia.org/wiki/Aufs)
to layer the new image on the old image. This means that distributing
application specific docker containers very quickly, because the base
image(s) (the operating system then your base libraries) change slowly
while your application can change quickly.

Here's our image listed with the `images` command:

```bash
$ docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
<none>              <none>              cda15ffd2f27        8 minutes ago       1.113 MB
busybox             latest              0064fda8c45d        42 hours ago        1.113 MB
```

You see the busybox image we downloaded, but the new image we just built
does not have a *tag* which means you will have to invoke it by its
image id:

```bash
$ docker run cda15ffd2f27 echo hello
```

This is inconvenient so people give tags to images, which you can do post-build:

```bash
$ docker tag cda15ffd2f27 my-app
$ docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
my-app              latest              cda15ffd2f27        13 minutes ago      1.113 MB
<none>              <none>              cda15ffd2f27        8 minutes ago       1.113 MB
busybox             latest              0064fda8c45d        42 hours ago        1.113 MB
```

However, you typically do his on the build line with

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
$ docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
my-app              latest              cda15ffd2f27        15 minutes ago      1.113 MB
busybox             latest              0064fda8c45d        42 hours ago        1.113 MB
```

Wait, what happend? Nothing? The image was rebuilt, but it had exactly the
same contents as the previous build so docker didn't do anything. This is a
bit strange, but makes a lot of sense in that docker builds are idempotent,
which makes the process of creating and running a docker image reproducible.
Docker uses the hash of the image for its ID, which is how it verifies that
nothing has changed.

#### Building an Application Image

A Dockerfile typically has more information than just the base box and
maintainer. You provision the image with a `RUN` command and then
specify a `CMD` that starts when the container boots. Here's a more
complex Dockerfile:

```
FROM busybox
MAINTAINER Rob Nagler
ADD . /cfg
RUN chmod +x /cfg/hello-world
CMD /cfg/hello-world
```

The `ADD` instruction tells Docker to copy the contents of the build
directory on the host to the build container (guest). Note that
`docker build` instantiates the base container (`FROM`) as a
container, which then is modified and persisted (see below) all in one
step.

The `RUN` command is executed in the build container (under `sh
-c`). There can be multiple `RUN` commands in a Dockerfile, but I
don't recommend this. Rather create a single "provisioner" script that
is executed by a single RUN command.

Finally, the `CMD` command is execute by default when the image is
instantiated as a container.

To execute the build with this new Dockerfile (`Dockerfile-my-app`) in
the same directory as the basic `Dockefile`, we need to pass it on the
command line. We also tag the image at build time with the `-t` flag:

```bash
$ docker build -f Dockerfile-my-app -t my-app .
```

When we run the container without an explicit command, this is what happens:

```bash
$ docker run my-app
Hello, World!
```

This is the basic steps of an app, but it's not all that useful as
an app.

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
