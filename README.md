## kbase-egrin2-service - An EGRIN2 pipeline accessible as a DOE KBase service

### Description

Here at [Baliga Lab](http://baliga.sytemsbiology.net), [Institute for Systems Biology](http://systemsbiology.org), we have created [EGRIN 2.0](http://egrin2.systemsbiology.net) a new model for gene regulatory networks.

We use an automated pipeline for generating EGRIN 2.0 models. This service is an implementation of our pipeline on the DOE KBase infrastructure.
Please be aware that this is a module intended to run as a KBase service within the KBase infrastructure and will likely not work outside of
this context.

For detailed documentation, please consult the project [Wiki](https://github.com/baliga-lab/kbase-egrin2-service/wiki).

### Building the service

```bash
$ cd dev_container
$ source user-env.sh
$ cd modules
$ git clone git@github.com:baliga-lab/kbase-egrin2-service.git
$ cd kbase-egrin2-service
$ make deploy
```

### Running the service

```bash
$ cd $TARGET/services/egrin2_service  # (see Makefile for TARGET location)
$ ./start_service
```
