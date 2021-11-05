from sqlalchemy.sql.expression import true
import ckan.lib.helpers as h
import ckan.plugins.toolkit as toolkit

_get_or_bust= toolkit.get_or_bust
_ = toolkit._
# import ckan.logic.validators as v

not_empty = toolkit.get_validator('not_empty')
#ignore_missing = p.toolkit.get_validator('ignore_missing')
#ignore_empty = p.toolkit.get_validator('ignore_empty')
is_boolean = toolkit.get_validator('boolean_validator')
# https://docs.ckan.org/en/2.8/extensions/validators.html#ckan.logic.validators.json_object
# NOT FOUND import ckan.logic.validators.json_object
#json_object = p.toolkit.get_validator('json_object')
# isodate

import ckan.lib.navl.dictization_functions as df

missing = df.missing
StopOnError = df.StopOnError
Invalid = df.Invalid

import ckanext.jsonschema.constants as _c
import ckanext.jsonschema.tools as _t
# import ckanext.jsonschema.validators as v
import logging
log = logging.getLogger(__name__)

#TODO... something more ckan oriented? 
#https://github.com/ckan/ckan/blob/c5c529d10ebe63d8573515483fdd46e0839477f0/ckan/lib/dictization/model_dictize.py
def instance_to_dict(i):
    '''
    The Validator receive a resource instance, we need a dict...
    '''
    return i


#############################################

import jsonschema
from jsonschema import validate,RefResolver,Draft4Validator,Draft7Validator
import json
import ckan.model as model

_SCHEMA_RESOLVER = jsonschema.RefResolver(base_uri='file://{}/'.format(_c.PATH_SCHEMA), referrer=None)

def _stop_on_error(errors,key,message):
    errors[key].append(_(message))
    raise StopOnError(_(message))
    
import six
def scheming_valid_json_object(value, context):
    """Store a JSON object as a serialized JSON string
    It accepts two types of inputs:
        1. A valid serialized JSON string (it must be an object or a list)
        2. An object that can be serialized to JSON
    """
    if not value:
        return
    elif isinstance(value, six.string_types):
        try:
            loaded = json.loads(value)

            if not isinstance(loaded, dict):
                raise Invalid(
                    _('Unsupported value for JSON field: {}').format(value)
                )

            return value
        except (ValueError, TypeError) as e:
            raise Invalid(_('Invalid JSON string: {}').format(e))

    elif isinstance(value, dict):
        try:
            return json.dumps(value)
        except (ValueError, TypeError) as e:
            raise Invalid(_('Invalid JSON object: {}').format(e))
    else:
        raise Invalid(
            _('Unsupported type for JSON field: {}').format(type(value))
        )

def default_version(key, data, errors, context):
    '''
    Validator providing default values 
    '''
    if not data[key]:
        data[key]=_c.SCHEMA_VERSION
    return

def schema_check(key, data, errors, context):
    '''
    Validator providing schema check capabilities
    '''
    body = data.get(key)
    if not body:
        _stop_on_error(errors,key,_('Can\'t validate empty Missing value {}'.format(key)))

    # ##############SIDE EFFECT#################
    # # if configuration comes as string:
    # # convert incoming string to a dict
    try:
        if not isinstance(body, dict):
            body = json.loads(body)
    except Exception as e:
        _stop_on_error(errors,key,'Not a valid json dict :{}'.format(str(e)))
    # ##############SIDE EFFECT#################
    
    schema = _t.get_schema_of(data.get((_c.SCHEMA_TYPE_KEY,)))

    # TODO extension point (we may want to plug other schema checkers)
    if not schema:
        _stop_on_error(errors,key,'Unable to load a valid jsonschema_type')

    try:
        # if not Draft4Validator.check_schema(constants.LAZY_GROUP_SCHEMA):
        #     raise Exception('schema not valid') #TODO do it once on startup (constants)
        #validator = Draft4Validator(constants.LAZY_GROUP_SCHEMA, resolver=resolver, format_checker=None)
        validator = Draft7Validator(schema, resolver=_SCHEMA_RESOLVER)
        # VALIDATE JSON SCHEMA
        _ret = validator.validate(body)

    except jsonschema.exceptions.ValidationError as e:
        #DEBUG
        #import traceback
        #traceback.print_exc()
        #TODO better message
        _stop_on_error(errors,key,'Error validating:{}'.format(str(e)))
    except Exception as e:
        #DEBUG
        #import traceback
        #traceback.print_exc()
        #TODO better message
        _stop_on_error(errors,key,'Error validating:{}'.format(str(e)))

def default_lon_e(key, data, errors, context):
    '''
    Validator providing default values 
    '''
    if not data[key]:
        data[key]=180
        return
    try:
        if float(data[key])>180:
            data[key]=180
    except ValueError:
        data[key]=180

def default_lon_w(key, data, errors, context):
    '''
    Validator providing default values 
    '''
    if not data[key]:
        data[key]=-180
        return
    try:
        if float(data[key])<-180:
            data[key]=-180
    except ValueError:
        data[key]=-180

def default_lat_n(key, data, errors, context):
    '''
    Validator providing default values 
    '''
    if not data[key]:
        data[key]=90
        return
    try:
        if float(data[key])>90:
            data[key]=90
    except ValueError:
        data[key]=90

def default_lat_s(key, data, errors, context):
    '''
    Validator providing default values 
    '''
    if not data[key]:
        data[key]=-90
        return
    try:
        if float(data[key])<-90:
            data[key]=-90
    except ValueError:
        data[key]=-90