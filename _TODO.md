# TODO: gravyvalet code docs

## README.md
- brief summary
- links to all other docs

## ARCHITECTURE.md
- code layout
- concepts and relationships
- sequence diagrams

addon operation invocation thru gravyvalet (as currently implemented)
```mermaid
sequenceDiagram
    participant browser
    Box cornflowerblue *.osf.io
        participant gravyvalet
        participant osf-api
    end
    Note over browser: browsing files on osf, say
    browser->>gravyvalet: request directory listing (create an addon operation invocation)
    gravyvalet->>osf-api: who is this?
    osf-api->>gravyvalet: this is who
    gravyvalet->>osf-api: may they do what they're asking to?
    alt no
        osf-api->>gravyvalet: no
        gravyvalet->>browser: no
    else yes
        osf-api->>gravyvalet: yes
        gravyvalet->>external-service: request directory listing
        external-service->>gravyvalet: serve directory listing
        Note over gravyvalet: translate listing into interoperable format
        gravyvalet->>browser: serve directory listing
    end
```

download a file thru waterbutler, with get_auth and gravyvalet (as currently implemented)
```mermaid
sequenceDiagram
    participant browser
    Box cornflowerblue *.osf.io
        participant waterbutler
        participant gravyvalet
        participant osf-api
    end
    browser->>waterbutler: request file
    waterbutler->>osf-v1: get_auth
    alt no
        osf-v1->>waterbutler: no
        waterbutler->>browser: no
    else yes
        osf-v1->>gravyvalet: request gravy
        gravyvalet->>osf-v1: serve gravy
        osf-v1->>waterbutler: credentials and config
        waterbutler->>external service: request file
        external service->>waterbutler: serve file
        waterbutler->>browser: serve file
    end
```

hypothetical world where waterbutler talks to gravyvalet... is this better than get_auth?
```mermaid
sequenceDiagram
    participant browser
    Box cornflowerblue *.osf.io
        participant waterbutler
        participant gravyvalet
        participant osf-api
    end
    browser->>waterbutler: request file
    waterbutler->>gravyvalet: request gravy
    gravyvalet->>osf-api: who is this?
    osf-api->>gravyvalet: this is who
    gravyvalet->>osf-api: may they do what they're asking to?
    alt no
        osf-api->>gravyvalet: no
        gravyvalet->>waterbutler: no
        waterbutler->>browser: no
    else yes
        osf-api->>gravyvalet: yes
        gravyvalet->>waterbutler: serve gravy
        waterbutler->>external service: request file
        external service->>waterbutler: serve file
        waterbutler->>browser: serve file
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
- required changes to waterbutler? (with mention of ideal "none")

## how-to/key_rotation.md
- credentials encryption overview
- secret and prior secrets
- scrypt configuration

## how-to/deployment_environment.md
- all environment variables
- link app/env.py
