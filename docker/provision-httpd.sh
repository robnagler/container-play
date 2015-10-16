#!/bin/sh
#
# Runs inside docker container as root
#
mkdir -p "$HTTPD_ROOT"/cgi-bin
install -m 400 /cfg2/index.html "$HTTPD_ROOT"/index.html
install -m 500 /cfg2/hello-world.cgi "$HTTPD_ROOT"/cgi-bin/hello-world
chown -R "$HTTPD_USER:$HTTPD_USER" "$HTTPD_ROOT"
chmod -R a-w "$HTTPD_ROOT"
# We need to make sure /cfg/hello-world.sh is world executable, since
# the httpd will be running as non-root, but my-app ran as root (docker default)
chmod 755 /cfg /cfg/hello-world.sh
