Apache Superset: DENODO contributions to the Apache Superset Project (GitHub)
=============================================================================


## Differences between the official distribution of Apache Superset and Denodo's

The main differences are:

  * Denodo's distribution is based on the official "ci" (Continuous Integration) official Docker image, whereas
    Apache Superset offers many other distribution and installation options. This is done for convenience, because
    the Denodo image is meant for quick installation and usage, mainly in local environments. This image is an
    "all-in-one", i.e. it does not allow the possibility to have a separate metadata database.
  * Denodo's distribution changes the base image used for the Docker image from a standard Debian-based "python"
    image to a Red Hat Universal Base Image (UBI), specifically one specialized in python development/execution. This is
    done in order to reduce the amount of vulnerabilities identifiable in the software distributed by Denodo.
    * Note that this means many changes in the standard `Dockerfile` in order to manage the packages to be installed
      and removed from the original base images and software.
  * Denodo's distribution includes both the db_engine_spec and the `denodo-sqlalchemy` dialect pre-installed, but the
    official installations of Apache Superset only include db_engine_specs, not the underlying drivers or SQLAlchemy
    dialects, which need to be installed with `pip install {package}` (or
    `docker exec -it {container} pip install {package})` — restarting the container may be needed).
    * Note however that, even if not included out-of-the-box, the versions of `denodo-sqlalchemy` that are deemed
      compatible with the standard distribution of Superset are configured in the standard distribution (in `setup.py`
      as of Superset 4.0).
  * Denodo's distribution includes a customized logo and application name, as well as a version number clearly
    identifying the software as a Denodo-modified version (e.g. `4.0.2+denodo-20240808`)
  * Denodo's distribution repositories include additional documentation (like this file) and also build artifacts such
    as a `Jenkinsfile` meant to configure how the image should be built by Denodo's own continuous integration systems.


