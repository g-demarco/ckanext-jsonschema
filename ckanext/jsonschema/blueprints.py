
from ckan.logic import schema
from ckan.common import json
from ckan.plugins.toolkit import get_action, request, h, get_or_bust
import json

# import ckan.common as converters
# from paste.deploy.converters import asbool

import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
from ckan.common import _, request

# Define some shortcuts
NotFound = logic.NotFound
ValidationError = logic.ValidationError

import ckanext.jsonschema.constants as _c
import ckanext.jsonschema.tools as _t
# import ckanext.terriajs.utils as utils
import logging
log = logging.getLogger(__name__)

from jinja2 import Template,Markup
from flask import Blueprint, abort, jsonify, send_file, Response, stream_with_context

jsonschema = Blueprint(_c.TYPE, __name__)
#url_prefix=constants.TYPE)

########################################
## Schema proxy

def read_schema(schema_type):
    '''
    Dumps the content of a local schema file.
    The file resolution is based on the configured schema folder and the (argument) json file name
    '''
    return json.dumps(_t.get_schema_of(schema_type))

jsonschema.add_url_rule('{}/<schema_type>'.format(_c.REST_SCHEMA_PATH), view_func=read_schema, endpoint='schema', methods=[u'GET'])

def read_schema_file(filename):
    '''
    Dumps the content of a local schema file.
    The file resolution is based on the configured schema folder and the (argument) json file name
    '''
    import os
    return read_schema(os.path.splitext(filename)[0])


jsonschema.add_url_rule('{}/<filename>'.format(_c.REST_SCHEMA_FILE_PATH), view_func=read_schema_file, endpoint='schema_file', methods=[u'GET'])


def read_template(schema_type):
    '''
    Dumps the content of a local schema file.
    The file resolution is based on the configured schema folder and the (argument) json file name
    '''
    import os
    return json.dumps(_t.get_template_of(schema_type))

jsonschema.add_url_rule('{}/<schema_type>'.format(_c.REST_TEMPLATE_PATH), view_func=read_template, endpoint='template', methods=[u'GET'])


def resolve_module(schema_type):
    '''
    Dumps the url of a js module file name matching the schema type
    '''
    import os
    module = _t.get_module_for(schema_type)
    if module:
        # return Response(stream_with_context(module), mimetype='text/plain')
        return send_file(module, mimetype='application/javascript')
    return abort(404, _('Unable to locate JS module for type: {}'.format(schema_type)))

jsonschema.add_url_rule('{}/<schema_type>'.format(_c.REST_MODULE_FILE_PATH), view_func=resolve_module, endpoint='module', methods=[u'GET'])
