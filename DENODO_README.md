Apache Superset: DENODO build
=============================


## Development environment in Windows hosts

It is recommended to keep two clones of the "denodolabs/superset" git repository in git.denodo.com.

  * One in Windows, used for direct interaction with git.denodo.com (origin = git.denodo.com) and easy editing of files.
  * Another one in a WSL2 distribution (e.g. Ubuntu) used for building but linked with the Windows clone, not with 
    git.denodo.com (e.g. origin = /mnt/c/Users/{user}/{route_to_repo}). This way modifications committed locally in
    the Windows repo can be tested and modified easily at the build system (WSL2) without the need to push them to
    git.denodo.com.

Also note that code editors such as Visual Studio Code (recommended for this project) allow connecting to WSL2
distributions in order to directly open files and folders in such WSL2 distribution as if they lived at the Windows
host. So direct editing on the WSL2 repository for building is possible, though changes committed there will need to
be pushed first to the Windows repository before these can be pushed again from the Windows repository to 
git.denodo.com.

Also, it is important that the Docker daemon is only installed in the Windows host (not WSL2) by means of installing
Rancher Desktop as specified in the company-wide instructions for this. Rancher Desktop will in fact install two
WSL2 distributions used for running the Docker daemon, and it will be possible to use the Docker client tool (CLI),
i.e. the "docker" command from both Windows Power Shell and a shell in a WSL2 disitribution (e.g. Ubuntu), though
using it from WSL2 is only recommended for _building_ the Superset images, not for running them, as explained below.


## Building the image

The Superset image needs to be built from WSL2. Also, Rancher Desktop needs to be running in the Windows host so that
the Docker daemon is available.

Command to be executed for building the image:

```sh
docker build --no-cache . -t denodolabs/superset-denodo:${version} --target ci
```

The value for `${version}` above should have been set also in `superset-frontend/package.json` so that users can quickly
reference the version they are working on, but note that python versioning for customized projects like this will look
like `4.0.2+denodo-20240801` whereas Docker does not allow `+` signs in version. Therefore, `+` characters need to be
replaced with `_` so that the above would be specified as `4.0.2_denodo-20240801` in the version of the Docker image:

```sh
docker build --no-cache . -t denodolabs/superset-denodo:4.0.2_denodo-20240801 --target ci
```

(Note this is also taken into account in the `Jenkinsfile` for automatic build.)

The `--no-cache` argument in the command above can be removed when we are testing small changes, in order to speed up
building time, but it is highly recommended to add it when we are producing an image for distribution.

The target to be build is the `ci` because this is the one that performs a set of initialization steps in the container
in order to be _more easily_ used (default users, roles and permissions). Specifically, it calls the
`docker/docker_init.sh` script. If a different target were used for building the image, these steps would need to be
performed manually in order to have a working Superset container.

> **NOTE** Building the Apache Superset image can take up to one hour.


## Starting the container for the first time

Once the image is built (or also, if they are obtained from our internal or public image repositories) we can start it
with:

```sh
docker run -d --name superset-denodo-${simplif_version} -e SUPERSET_SECRET_KEY=${secret_key} -p 8088:8088 denodolabs/superset-denodo:${version}
```

Where:
  * `version` is the version of the image we want to run, e.g. `4.0.2_denodo-20240801`.
  * `simplif_version` is a simplified variant of the version, for container reference convenience, e.g. `402`.
  * `secret_key` is a random key for secrets to be internally used by superset. Ideally this should
    be generated somehow like, for instance, using the `openssl rand -base64 42` command in a Linux shell, but any
    random ASCII-64 string would do for most development and testing purposes (e.g. `2da724ff`).

For example:

```sh
docker run -d --name superset-denodo-402 -e SUPERSET_SECRET_KEY=a8750bf552 -p 8088:8088 denodolabs/superset-denodo:4.0.2_denodo-20240801
```

The `--rm` argument can be added to the command above if we do not wish this container to live in our docker
subsystem after stopping it.

Also note that, if the host system is Windows (even if it has a WSL2 installation) it is _highly recommended_ to start
container images from the Windows PowerShell, not from WSL2. And also that PowerShell is specifically recommended
on top of other command line options in Windows (including the standard Command Prompt or any CYGWIN-equivalents) due
to its better compatibility with the argument and literal substitution rules in the "docker" client command.


Just after starting the container, it is recommended to check the container's logs with:

```sh
docker logs -f superset-denodo-${simplif_version}
```

This will _tail_ the logs in the console, until we press `Ctrl + c`.

Once started, we can access Superset with a browser at `http://localhost:8088`, using the `admin/admin` user created
during automatic initialization of the container (`docker_init.sh`).


## Re-starting a stopped container

Once a Superset container is started for the first time, they can be stopped and restarted using the `docker stop` and
`docker start` commands but, for convenience, it is recommended to do this from the _"Containers"_ panel in
Rancher Desktop's user interface.


## Connecting to a VDP server in the host Windows machine from Superset

Once the Superset container is started, if we wanted to create a database connection from Superset to a VDP server
in our Windows host we should use:

   * Host: `host.docker.internal`
   * Port: `9996` or whichever port we have configured for VDP's ODBC/PostgreSQL interface.

This should work assuming that we have followed the instructions above for starting the container from Windows, that
our Rancher Desktop installation has followed the company guidelines (including firewall rule configuration), and that
we have re-started Rancher Desktop and therefore the Docker daemon since the last time our machine has changed IP 
address -- for instance, when we commuted from a work-from-home environment to the office.


## Practical example: Setting a volume for _live_ development on the denodo DB Engine Spec

When making changes on the `denodo.py` DB Engine Spec in Superset, we can set a volume pointing to our local
folder on Windows in order to make changes without needing to create a new image or container:

```sh
docker run -d --name superset-denodo-${simplif_version} -e SUPERSET_SECRET_KEY=${secret_key} -v ${PWD}/${path_to_superset_local_repo}/superset/db_engine_specs:/app/superset/db_engine_specs -p 8088:8088 denodolabs/superset-denodo:${version}
```

Again, the `${PWD}` is an actual shell variable to be expanded by PowerShell. For example:

```sh
docker run -d --name superset-denodo-402 -e SUPERSET_SECRET_KEY=a8750bf552 -p 8088:8088 -v ${PWD}/Workspace/superset/superset/db_engine_specs:/app/superset/db_engine_specs denodolabs/superset-denodo:4.0.2_denodo-20240801
```

Note that changes will still need the container to be stopped and restarted (re-starting takes some seconds):

```sh
docker stop superset-denodo-${simplif_version}
docker start superset-denodo-${simplif_version}
```


## Obtaining a vulnerabilities report with Trivy

In order to obtain a vulnerabilities report using Trivy, we can use this command from a Windows PowerShell:

```sh
docker run --rm -v ${PWD}/tmp:/root/.cache/ -v //var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image denodolabs/superset-denodo:${version} -f json > superset-denodo_vulnerabilities-${version}.json
```

Note that only the `${version}` placeholder above should be replaced in the command, as `${PWD}` is a system variable.
So a real command would look like:

```sh
docker run --rm -v ${PWD}/tmp:/root/.cache/ -v //var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image denodolabs/superset-denodo:4.0.2_denodo-20240801 -f json > superset-denodo_vulnerabilities-4.0.2_denodo-20240801.json
```

The resulting `superset-denodo_vulnerabilities-${version}.json` file will contain the vulnerabilities report.


## Cleaning the docker builder cache

After building many images (especially with the `--no-cache` option), the Docker builder cache might have stored
so much data that Rancher Desktop's data partition becomes full. This will cause strange build errors such as
images not being capable of downloading artifacts or validating repository signatures, or other errors not 
apparently related to a lack of disk space.

This can be verified with `df -h` (see "Avail" below):

```
user@machine:~$ df -h
Filesystem      Size  Used Avail Use% Mounted on
...
/dev/sdd        251G  241G     0 100% /mnt/wsl/rancher-desktop/run/data
```

In order to clean this cache, we can use this command:

```
docker builder prune -a
```
