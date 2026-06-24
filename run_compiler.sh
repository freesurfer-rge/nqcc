#!/bin/bash

uv --directory "$(dirname "$(readlink -f "$0")")" run python -m nqcc "$@"