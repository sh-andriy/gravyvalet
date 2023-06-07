# Gravyvalet

A thicker, more hands-on counterpart to waterbutler.

# Reason for being

The goal is to split out OSF addons into their own well-encapsulated service. This is the prototype/initial version 

## Approach

Mostly just started off by figuring out the necessary endpoints and putting in stubs.  Then started inlining code from the OSF, chasing down things through base classes, decorators, and utility functions.  Foolishly attempted to inline the actual django model code for addons.  That broke me. Moved that into a side file and just stubbed out the called model code.  Currently trying to fill out the stubs with simple impls & fixtures.

Chose box as the first addon to implement, since it is one of the saner, less corner-casey addons.  Not currently worrying to much about making it extensible, figure that's part of the actual dev.

# Quickstart

It's a Django app. `gravyvalet` is the "root" app, but most of the work is being done in the `charon` app.

For no particular reason, I've chosen `8011` as the default gravyvalet port.

```
$ pip install -r requirements.txt
$ python manage.py runserver 8011
```
