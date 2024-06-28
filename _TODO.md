# TODO: gravyvalet code docs

## README.md
- brief summary
- links to all other docs

## ARCHITECTURE.md
- code layout
- concepts and relationships
- sequence diagrams

```mermaid
sequenceDiagram
    browser->>wb: request file
    wb->>gv: request gravy
    gv->>wb: serve gravy
    wb->>external service: request file
    external service->>wb: serve file
    wb->>browser: serve file
```

```mermaid
sequenceDiagram
    Box Blue *.osf.io
        participant gv
        participant osf-api
    end
    Note over browser: browsing files on osf, say
    browser->>gv: request directory listing
    gv->>osf-api: who is this?
    osf-api->>gv: this is who
    gv->>osf-api: can they do what they're asking to?
    alt no
        osf-api->>gv: no
        gv->>browser: no
    else yes
        osf-api->>gv: yes
        gv->>external-service: request directory listing
        external-service->>gv: serve directory listing
        Note over gv: translate listing into interoperable format
        gv->>browser: serve directory listing
    end
```


## how-to/local_setup_with_osf.md
- with gravyvalet docker-compose.yml
- with osf.io docker-compose.yml
- without docker?

## how-to/new_imp_interface.md
- defining interface with operations
- required adds to addon_service

## how-to/migrating_osf_addon_to_imp.md
- implementing imp
- current limitations

## how-to/new_storage_imp.md
- implementing imp
- required changes to wb? (with mention of ideal "none")

## how-to/key_rotation.md
- credentials encryption overview
- secret and prior secrets
- scrypt configuration

## how-to/deployment_environment.md
- all environment variables
- link app/env.py
