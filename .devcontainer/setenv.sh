#!/bin/bash

USER_GID=$(id -g)
USER_UID=$(id -u)
HOSTDOCKERGID=$(getent group docker | cut -d: -f3)

echo "USER_GID=$USER_GID" > .devcontainer/.env
echo "USER_UID=$USER_UID" >> .devcontainer/.env
echo "HOSTDOCKERGID=$HOSTDOCKERGID" >> .devcontainer/.env