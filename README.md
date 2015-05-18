# onesky-python

This is a simple python wrapper around the OneSky API for managing
translations.  For the full documentation on the OneSky REST API, see
https://github.com/onesky/api-documentation-platform.

It's still pretty early/rough, so please let me know if you have any
problems or suggestions!  I'm not sure I'm crazy about the methods
returning (http status, dictionary) pairs, so I'm particularly open to
suggestions there.  Perhaps throwing an exception for a bad http status?

## Installation
Install using `pip`:
```
$ pip install onesky-python
```

Or, download the source code for `onesky-python`, and then run:
```
$ python setup.py install
```

Depending on your setup, you may need to run the above commands with `sudo`.

## Getting Started—A Simple Example

Simply create a client using your API key.  Most of the methods return the JSON response from OneSky as a dictionary:

```python
from onesky import Client

client = Client(api_key='<your API key>',
                api_secret='<your API secret>')

status, json_response = client.project_group_list()
# {
#   "meta": { "status": 200, "record_count": 2 },
#   "data": [
#     { "id": 365, "name": "Travel Magazine" },
#     { "id": 366, "name": "Fashion Magazine" }
#   ]
# }

status, json_response = client.project_list(365)
# {
#   "meta": { "status": 200, "record_count": 2, },
#   "data": [
#      { "id": 6968, "name": "Company website" },
#      { "id": 6969, "name": "Company blog" }
#    ]
# }

status, json_response = client.project_show(6968)
# {
#   "meta": { "status": 200 },
#   "data": {
#     "id": 6968,
#     "name": "Website",
#     "description": "Words from company website.",
#     "project_type": {
#       "code": "website",
#       "name": "Website"
#     },
#     "string_count": 1385,
#     "word_count": 2956
#   }
# }
```
To upload a file using the `file_upload` method, simply pass the
filename as the `file_name` argument, and the contents of that file
will be sent.

Downloading a file via the `translation_export` method automatically
saves the file on disk.  To specify the directory for downloaded
files, set `download_dir` when creating your `Client` object (defaults
to `'.'`).  The filename will also be set as a `downloaded_filename`
key in the response.

## Command-line interface

A simple command-line interface is also provided for testing your
integration and running other simple tests of the API.  All of the
Client methods are provided with the same name as the corresponding function.
```python
import onesky.interactive

interpreter = onesky.interactive.Interpreter('<your API key>', '<your API secret>')
interpreter.cmdloop()
```

```
onesky> help

Documented commands (type help <topic>):
========================================
file_delete       order_show               project_list
file_list         project_create           project_show
file_upload       project_delete           project_type_list
help              project_group_create     project_update
import_task_list  project_group_delete     quotation_show
import_task_show  project_group_languages  translation_export
locale_list       project_group_list       translation_status
order_create      project_group_show
order_list        project_languages

onesky> project_group_list
GET https://platform.api.onesky.io/1/project-groups
params: dev_hash=<whatever>&timestamp=<whatever>&api_key=<whatever>
Status code: 200
Response:
{u'data': [<list of your project groups>]
 u'meta': {u'first_page': None,
           u'last_page': None,
           u'next_page': None,
           u'page_count': 1,
           u'prev_page': None,
           u'record_count': 4,
           u'status': 200}}
onesky>
```

## Unit Tests

To run the unit tests, you'll need the `nose` and `mock` libraries installed:
```
$ pip install mock nose
$ cd /path/to/onesky-python
$ nosetests
```
