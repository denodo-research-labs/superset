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

```sh
user@machine:~$ df -h
Filesystem      Size  Used Avail Use% Mounted on
...
/dev/sdd        251G  241G     0 100% /mnt/wsl/rancher-desktop/run/data
```

In order to clean this cache, we can use this command:

```sh
docker builder prune -a
```

## Releasing

### 1. Uploading images to Denodo's gcr.io image container

The "denodo-proddev-container" project in Google Cloud contains all the Docker images created internally. This can be
accessed at https://console.cloud.google.com/artifacts/docker/denodo-proddev-container/us/gcr.io

Newly-built Superset images are automatically uploaded there according to the Jenkinsfile file in the root of the
build branches. Build branches (typically only one) can be configured in Jenkins: https://porsche-brown.denodo.com/

The selected branch or branches are automatically built after every commit, and results are uploaded to the images
container with name "denodolabs/superset-denodo".

Builds can also be triggered manually from the Jenkins UI. When running from Jenkins, the "DRY RUN" flag should be
unchecked in order for the resulting image to be actually uploaded to the gcr.io image container.


### 2. Pulling the generated images from gcr.io

The first time we do this, we need to make sure we are properly authenciated in the container. From a PowerShell, and
having previously installed the Google Cloud SDK:

```sh
gcloud auth configure-docker gcr.io
```

Now we can pull the image from gcr.io with:

```sh
docker pull gcr.io/denodo-proddev-container/denodolabs/superset-denodo:${version}
```


### 3. Testing the images

Images generated by Jenkins and pushed to gcr.io (Release Candidates) can be tested by running them similarly to
development images:

```sh
docker run -d --name superset-denodo-${simplif_version}-rc -e SUPERSET_SECRET_KEY=${secret_key} -p 8088:8088 gcr.io/denodo-proddev-container/denodolabs/superset-denodo:${version}
```
For example:
```sh
docker run -d --name superset-denodo-402-rc -e SUPERSET_SECRET_KEY=a8750bf552 -p 8088:8088 gcr.io/denodo-proddev-container/denodolabs/superset-denodo:4.0.2_denodo-20240801
```


### 4. Uploading images to Harbor

In order to upload images to Harbor, we need to make sure that we are correctly authenticated:

```sh
docker login harbor.open.denodo.com
```

Then in order to push these images to Harbor, we need to take the images we already got from gcr.io and give them a,
new name, i.e. apply a new tag for them (same image, two "names") so that they now additionally have the names (tags)
they would have if they were downloaded from harbor.open.denodo.com.

We can do this with the `docker tag` command, like:

```sh
docker tag gcr.io/denodo-proddev-container/denodolabs/superset-denodo:${version} harbor.open.denodo.com/denodo-connects-${denodo_version}/images/superset-denodo:${version_plus_latest}
```

Note that we need to do this for all `denodo_version` values applicable (e.g. `8.0` and `9`), and we need to apply
to the images not only the version tag that corrresponds to `${version}` (e.g. `4.0.2_denodo-20240801`) but also the
`latest` tag.

So for example:

```sh
docker tag gcr.io/denodo-proddev-container/denodolabs/superset-denodo:4.0.2_denodo-20240801 harbor.open.denodo.com/denodo-connects-8.0/images/superset-denodo:4.0.2_denodo-20240801

docker tag gcr.io/denodo-proddev-container/denodolabs/superset-denodo:4.0.2_denodo-20240801 harbor.open.denodo.com/denodo-connects-8.0/images/superset-denodo:latest

docker tag gcr.io/denodo-proddev-container/denodolabs/superset-denodo:4.0.2_denodo-20240801 harbor.open.denodo.com/denodo-connects-9/images/superset-denodo:4.0.2_denodo-20240801

docker tag gcr.io/denodo-proddev-container/denodolabs/superset-denodo:4.0.2_denodo-20240801 harbor.open.denodo.com/denodo-connects-9/images/superset-denodo:latest
```

Once the tags are created, we can push them to Harbor using `docker push`:

```sh
docker push harbor.open.denodo.com/denodo-connects-${denodo_version}/images/superset-denodo:${version_plus_latest}
```

So for example:

```sh
docker push harbor.open.denodo.com/denodo-connects-8.0/images/superset-denodo:4.0.2_denodo-20240801

docker push harbor.open.denodo.com/denodo-connects-8.0/images/superset-denodo:latest

docker push harbor.open.denodo.com/denodo-connects-9/images/superset-denodo:4.0.2_denodo-20240801

docker push harbor.open.denodo.com/denodo-connects-9/images/superset-denodo:latest
```


### 5. Signing images in Harbor

At this point, the recently pushed images will appear at https://harbor.open.denodo.com as "unsigned". So they have
to be signed using "Cosign".

An internal document on this process can be read at: https://docs.google.com/document/d/1H82Derzn0vaxLZJEhPKYGIboLwsxt1aSiVQZW-gNfdc/edit#heading=h.h1yom9h7m2mx

Once the Cosign infrastructure has been correctly installed, images can be signed executing the following from
PowerShell, from the folder where the `cosign_denodo.key` file has been created:

```sh
cosign sign --key cosign_denodo.key harbor.open.denodo.com/denodo-connects-${denodo_version}/images/superset-denodo@sha256:${sha_sum}
```

The value for `${sha_sum}` above can be obtained from the Harbor interface itself, where images will appear referenced
like `sha245:xxxx`. But note that that SHA sum is in _reduced_ format, and cosign will need the entire value. This
entire value can be obtained by clicking on the details of the image on the Harbor interface and copying it from
the URL.

Also, during the signing operation, cosign will ask for the password for the private key used for signing. This has to
be obtained according to the document above, and will typically be stored and managed using LastPass.

Given the `${version}` and `latest` tags will have the same SHA sum, this will only be needed once for each value
of `{denodo_version}`. So for example:

```sh
cosign sign --key cosign_denodo.key harbor.open.denodo.com/denodo-connects-8.0/images/superset-denodo@sha256:4a0a22762df12bcc3dae31d7ecf50de8c82c89f9171d75f1ef072283aa134591

cosign sign --key cosign_denodo.key harbor.open.denodo.com/denodo-connects-9/images/superset-denodo@sha256:4a0a22762df12bcc3dae31d7ecf50de8c82c89f9171d75f1ef072283aa134591
```

Once signed, images should appear as such at the Harbor user interface, and this will conclude the process.


## Exporting images for their inclusion in the Denodo Dashboard artifacts

Due to network restrictions, some customers require images to be included in the Denodo Dashboard artifacts downloadable
from the Support Site (they cannot download from Denodo Harbor). We will distribute these images in `.tar.gz` format.

In order to facilitate this, we need to save the images from our local repository using `docker save`:

```sh
docker save harbor.open.denodo.com/denodo-connects-${denodo_version}/images/superset-denodo:${version} -o superset-denodo-${denodo_version}-image-${version}.tar
```

And then gzip it to get the `.tar.gz` final file:

```sh
gzip superset-denodo-${denodo_version}-image-${version}.tar
```

Note that, if the GZip tool is not installed in Windows, it can be used from a WSL2 distribution, as Linux typically
include this tool.

For example:

```sh
docker save harbor.open.denodo.com/denodo-connects-8.0/images/superset-denodo:4.0.2_denodo-20240801 -o superset-denodo-8.0-image-4.0.2_denodo-20240801.tar
gzip superset-denodo-8.0-image-4.0.2_denodo-20240801.tar

docker save harbor.open.denodo.com/denodo-connects-9/images/superset-denodo:4.0.2_denodo-20240801 -o superset-denodo-9-image-4.0.2_denodo-20240801.tar
gzip superset-denodo-9-image-4.0.2_denodo-20240801.tar
```

Images will now be ready to be included in the DenodoConnect artifacts, and when loaded will create the same tags
in the host docker system as if they were downloaded from Harbor.


