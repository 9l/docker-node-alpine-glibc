#!/usr/bin/env python3

import os
import sys

node_versions = [
    "23",
]

glibc_version = "2.34-r0"

docker_arches = [
    "linux/amd64",
    "linux/arm64",
]

def read_file(file):
    with open(file, "r") as f:
        return f.read()

def write_file(file, contents):
    dir = os.path.dirname(file)
    if dir and not os.path.exists(dir):
        os.makedirs(dir)
    with open(file, "w") as f:
        f.write(contents)

def update_alpine_gblic():
    template = read_file("Dockerfile-alpine-glibc.template")

    for version in node_versions:
        rendered = template \
            .replace("%%TAG%%", version) \
            .replace("%%GLIBC-VERSION%%", glibc_version)
        write_file(f"{version}/alpine-glibc/Dockerfile", rendered)

def update_ci():
    file = ".github/workflows/ci.yml"
    config = read_file(file)

    versions = ""
    for version in node_versions:
        platform = []
        for arch in docker_arches:
            platform.append(f"{arch}")
        platform = ",".join(platform)

        versions += f"          - name: {version}-alpine-glibc{glibc_version}\n"
        versions += f"            context: {version}/alpine-glibc\n"
        versions += f"            platforms: {platform}\n"
        versions += f"            tags: |\n"
        for tag in node_versions:
            versions += f"              {tag}-alpine-glibc\n"

    marker = "#VERSIONS\n"
    split = config.split(marker)
    rendered = split[0] + marker + versions + marker + split[2]
    write_file(file, rendered)

def usage():
    print(f"Usage: {sys.argv[0]} update|update-ci|update-all")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        usage()

    task = sys.argv[1]
    if task == "update":
        update_alpine_gblic()
    elif task == "update-ci":
        update_ci()
    elif task == "update-all":
        update_alpine_gblic()
        update_ci()
    else:
        usage()