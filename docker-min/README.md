### Create Minimal docker image

This directory is structured to support
[mkimage.sh](https://github.com/docker/docker/blob/master/contrib/mkimage.sh),
which is part of the
[Docker contrib](https://github.com/docker/docker/tree/master/contrib).

To build a minimal `bash` image called "just-bash", do this:

```sh
./mkimage.sh --tag just-bash just-bash.py
```

This will create an image with a handful of files, mostly automatically extracted.
You can then run it with:

```sh
docker run -i -t just-bash
```

It's just `bash` and `ls`. However, `bash` has a lot of builtins so you can
construct programs.
