# kitdm-pycli
This Python project contains a collection of command line clients for different KIT Data Manager services. The clients
are supposed to be used to ease local administration, for testing, and automated operations.

## Prerequisites

* Python 3.9+
* [Optional] base-repo installation
* [Optional] MetaStore installation
* [Optional] Typed PID Maker installation
* [Optional] Keycloak installation

## Quickstart

If you don't need access to the code you can install 'kitdm-pycli' directly from this repository. Therefore, just call:

```bash
pip install git+https://github.com/kit-data-manager/kitdm-pycli.git
```
Afterwards, you should create a properties file, e.g., pycli-properties.json, based on [properties.example.json](properties.example.json).
Once finished, you either let an environment variable named `PYCLI_PROPERTIES` point to this file or you directly call 'kitdm-pycli' as follows:

```bash
PYCLI_PROPERTIES=<path_to_pycli-properties.json> base-repo-client getResources
```

For details about the contained clients, please refer to the *Main Usage Information* sections at the end of this document.


## Installation and setup

After cloning the repository, start with installing the dependencies by calling

```bash
pip install poetry
poetry install
```

Optionally, especially when you are modifying code, you may call available tests via:

```bash
poetry poe test
```

Afterwards, the configuration file `properties.example.json` must be modified to fit your local setup and moved to
`properties.json` in the current folder. The configuration options in the file are grouped by service and should be
self-explaining. If you are unsure, contact your local infrastructure administrator to obtain missing information.

If you want to use multiple properties files for different setups, you may point to the appropriate file via its
absolute path set as the environment variable `PYCLI_PROPERTIES`. If not set, `properties.json` is expected to be
located in the current folder.

If all properties are correctly set, one of the available clients can be used. For details, please refer to the
following chapters.

## base-repo-client

*base-repo-client.py* allows to perform many operations on a configured base-repo instance to create, read, update,
and delete resources and their file contents. Basic usage information is printed below, but can also be obtained via

```commandline
poetry run base-repo-client --help
```

For details about a particular operation, e.g., createResource, help can be obtained via

```commandline
poetry run base-repo-client createResource --help
```

### Main Usage Information - base-repo

```commandline
usage: base-repo-client.py [-h] [-a | --auth | --no-auth] [-r {TABLE,LIST,RAW}] [-o OUTPUT] [-d | --debug | --no-debug]
                           {createResource,createContent,getResource,getResources,getContent,downloadContent,updateResource,patchResource,patchContent,deleteResource,deleteContent} ...

Command line client interface for the base-repo service.

positional arguments:
  {createResource,createContent,getResource,getResources,getContent,downloadContent,updateResource,patchResource,patchContent,deleteResource,deleteContent}
                        Operation selection
    createResource      Create a new data resource.
    createContent       Create a new content element.
    getResource         List metadata for one or more single resources.
    getResources        List metadata for all resources,optionally filtered by creation time.
    getContent          List metadata for one or more resource's content elements.
    downloadContent     Download content from a resource.
    updateResource      Update a resource's metadata providing a complete resource metadata document that will replace the existing version.
    patchResource       Patch a resource's metadata. In comparison the the update, the patch operation accepts an RFC 6902 JSON Patch document instead of all resource metadata.
    patchContent        Patch content metadata.
    deleteResource      Delete one or more single resource(s) and all its contents.
    deleteContent       Delete content.

options:
  -h, --help            show this help message and exit
  -a, --auth, --no-auth
                        Switch for enabling/disabling authentication before the actual service request. If enabled, the KeyCloak instance configured in properties.json is used. By default, the user is asked for username and
                        password. However, both can also be configured in properties.json such that only missing information is requested, e.g., if the password is not stored in properties.json, which is anyway only recommended
                        in a protected environment.
  -r {TABLE,LIST,RAW}, --render_as {TABLE,LIST,RAW}
                        This parameter allows to configure the way results are rendered. By default, a user-friendly representation as table is printed where results are returned. The visible columns of the table can be
                        configured in properties.json.Alternatively, only the resource ids can be printed for further processing or the raw result can be returned.
  -o OUTPUT, --output OUTPUT
                        The absolute or relative path of an output file used to store the output of the performed operation, e.g., a file download or the rendered result. If used in combination with --render_as TABLE or LIST
                        outputs that can rendered as such are re-formatted depending on the output file extension. Supported extensions are .csv (comma separated), .json (structured table), and .html (web table). If not
                        provided, all outputs are printed to stdout.
  -d, --debug, --no-debug
                        Enable verbose output for debugging. Disabled by default. (default: False)
```

### Main Usage Information - MetaStore

```commandline
usage: metastore-client.py [-h] [-a | --auth | --no-auth] [-r {TABLE,LIST,RAW}] [-o OUTPUT] [-d | --debug | --no-debug]
                           {createSchema,createDocument,getSchema,getSchemas,getDocument,getDocuments,downloadSchema,downloadDocument,updateSchema,updateDocument,deleteSchema,deleteDocument} ...

Command line client interface for the MetaStore service.

positional arguments:
  {createSchema,createDocument,getSchema,getSchemas,getDocument,getDocuments,downloadSchema,downloadDocument,updateSchema,updateDocument,deleteSchema,deleteDocument}
                        Operation selection
    createSchema        Create a new metadata schema.
    createDocument      Create a new metadata document.
    getSchema           List metadata for single or multiple registered schemas.
    getSchemas          List metadata for multiple registered schemas.
    getDocument         List metadata for single or multiple registered documents by id
    getDocuments        List metadata for multiple registered documents.
    downloadSchema      Download a metadata schema.
    downloadDocument    Download a metadata document.
    updateSchema        Update a metadata schema.
    updateDocument      Update a metadata document.
    deleteSchema        Delete one or more schemas.
    deleteDocument      Delete one or more documents.

options:
  -h, --help            show this help message and exit
  -a, --auth, --no-auth
                        Switch for enabling/disabling authentication before the actual service request. If enabled, the KeyCloak instance configured in properties.json is used. By default, the user is asked for username and
                        password. However, both can also be configured in properties.json such that only missing information is requested, e.g., if the password is not stored in properties.json, which is anyway only recommended
                        in a protected environment.
  -r {TABLE,LIST,RAW}, --render_as {TABLE,LIST,RAW}
                        This parameter allows to configure the way results are rendered. By default, a user-friendly representation as table is printed where results are returned. The visible columns of the table can be
                        configured in properties.json.Alternatively, only the resource ids can be printed for further processing or the raw result can be returned.
  -o OUTPUT, --output OUTPUT
                        The absolute or relative path of an output file used to store the output of the performed operation, e.g., a file download or the rendered result. If used in combination with --render_as TABLE or LIST
                        outputs that can rendered as such are re-formatted depending on the output file extension. Supported extensions are .csv (comma separated), .json (structured table), and .html (web table). If not
                        provided, all outputs are printed to stdout.
  -d, --debug, --no-debug
                        Enable verbose output for debugging. Disabled by default. (default: False)
```

### Main Usage Information - Typed PID Maker

```commandline
usage: typed-pid-maker-client.py [-h] [-a | --auth | --no-auth] [-r {TABLE,LIST,RAW}] [-o OUTPUT] [-d | --debug | --no-debug] {createRecord,getPid,getKnownPid,getKnownPids,updateRecord} ...

Command line client interface for the Typed PID Maker service.

positional arguments:
  {createRecord,getPid,getKnownPid,getKnownPids,updateRecord}
                        Operation selection
    createRecord        Create a new typed PID record.
    getPid              List PIDs and their create/modification details for one or more PIDs.
    getKnownPid         Get one or more known PIDs and their create/modification details.
    getKnownPids        List all known PIDs and their create/modification details, optionally filtered by creation time.
    updateRecord        Update a PID Record's metadata providing a complete PID record document that will replace the existing version.

options:
  -h, --help            show this help message and exit
  -a, --auth, --no-auth
                        Switch for enabling/disabling authentication before the actual service request. If enabled, the KeyCloak instance configured in properties.json is used. By default, the user is asked for username and
                        password. However, both can also be configured in properties.json such that only missing information is requested, e.g., if the password is not stored in properties.json, which is anyway only recommended
                        in a protected environment.
  -r {TABLE,LIST,RAW}, --render_as {TABLE,LIST,RAW}
                        This parameter allows to configure the way results are rendered. By default, a user-friendly representation as table is printed where results are returned. The visible columns of the table can be
                        configured in properties.json.Alternatively, only the resource ids can be printed for further processing or the raw result can be returned.
  -o OUTPUT, --output OUTPUT
                        The absolute or relative path of an output file used to store the output of the performed operation, e.g., a file download or the rendered result. If used in combination with --render_as TABLE or LIST
                        outputs that can rendered as such are re-formatted depending on the output file extension. Supported extensions are .csv (comma separated), .json (structured table), and .html (web table). If not
                        provided, all outputs are printed to stdout.
  -d, --debug, --no-debug
                        Enable verbose output for debugging. Disabled by default. (default: False)
```

## License

The KIT Data Manager is licensed under the Apache License, Version 2.0.
