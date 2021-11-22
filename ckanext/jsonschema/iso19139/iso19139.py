from sqlalchemy.sql.expression import true
from sqlalchemy.sql.sqltypes import ARRAY

import ckan.lib.helpers as h
import ckan.plugins.toolkit as toolkit

_get_or_bust= toolkit.get_or_bust
_ = toolkit._
import ckan.plugins as p

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

import ckanext.jsonschema.validators as _v
import ckanext.jsonschema.constants as _c
import ckanext.jsonschema.tools as _t
import ckanext.jsonschema.interfaces as _i

import logging
log = logging.getLogger(__name__)


import ckan.lib.navl.dictization_functions as df


#############################################

import jsonschema
from jsonschema import validate,RefResolver,Draft4Validator,Draft7Validator
import json
import ckan.model as model

TYPE_ONLINE_RESOURCE='online-resource'
TYPE_ISO19139='iso19139'

SUPPORTED_DATASET_FORMATS = [TYPE_ISO19139]
SUPPORTED_RESOURCE_FORMATS = []

class JsonschemaIso19139(p.SingletonPlugin):
    p.implements(_i.IBinder, inherit=True)

        # namespaces = {u'http://www.opengis.net/gml/3.2': u'gml', u'http://www.isotc211.org/2005/srv': u'srv', u'http://www.isotc211.org/2005/gts': u'gts', u'http://www.isotc211.org/2005/gmx': u'gmx', u'http://www.isotc211.org/2005/gmd': u'gmd', u'http://www.isotc211.org/2005/gsr': u'gsr', u'http://www.w3.org/2001/XMLSchema-instance': u'xsi', u'http://www.isotc211.org/2005/gco': u'gco', u'http://www.isotc211.org/2005/gmi': u'gmi', u'http://www.w3.org/1999/xlink': u'xlink'}
        # # TODO DEBUG
        # import ckanext.jsonschema.utils as _u
        # import os
        # j = _u.xml_to_json_from_file(os.path.join(_c.PATH_TEMPLATE,'test_iso.xml'))
        # import json
        # _j=json.loads(j)
        # _namespaces=_j['http://www.isotc211.org/2005/gmd:MD_Metadata']['@xmlns']
        # namespaces = dict((v,k) for k,v in _namespaces.iteritems())
        # _u.json_to_xml()
        # _u.xml_to_json_from_file(os.path.join(_c.PATH_TEMPLATE,'test_iso.xml'), True, namespaces)

    def supported_resource_types(self, dataset_type, opt=_c.SCHEMA_OPT, version=_c.SCHEMA_VERSION):
        if version != _c.SCHEMA_VERSION:
            # when version is not the default one we don't touch
            return []

        if dataset_type in SUPPORTED_DATASET_FORMATS:
            #TODO should be a dic binding set of resources to dataset types 
            return SUPPORTED_RESOURCE_FORMATS

        return []

    def supported_dataset_types(self, opt, version):
        if version != _c.SCHEMA_VERSION:
            # when version is not the default one we don't touch
            return []

        return SUPPORTED_DATASET_FORMATS

    def extract_from_json(self, body, type, opt, version, key, data, errors, context):
        
        if type == TYPE_ISO19139:
            _extract_iso(body, opt, version, key, data, errors, context)
        # if type == TYPE_ONLINE_RESOURCE:
            # _extract_transfer_options(body, opt, type, version, key, data, errors, context)





# def append_nested(_dict, tuple, value = {}):
#     try:
#         d = _dict
#         for k in tuple[:-1]:
#             v = d.get(k)
#             if not v:
#                 d = d.setdefault(k,{})
#             elif isinstance(v, list):
#                 d = {}
#                 v.append(d)
#             elif isinstance(v, dict):
#                 d = d[k]

#         d.update({tuple[-1:][0]:value})
#     except:
#         return None
#     return _dict

def set_nested(dict, tuple, value):
    try:
        d = dict
        for k in tuple[:-1]:
            d = d.setdefault(k,{})
        d.update({tuple[-1:][0]:value})
    except:
        return None
    return dict

def pop_nested(dict, tuple):
    d = dict
    for k in tuple[:-1]:
        try:
            d = d[k]
        except:
            return
    return d.pop(tuple[-1:][0])

def get_nested(dict, tuple):
    d = dict
    for k in tuple[:-1]:
        try:
            d = d[k]
        except:
            return
    # return d.get(tuple[-1:])
    return d.get(tuple[-1:][0])

# https://github.com/jab/bidict/blob/0.18.x/bidict/__init__.py#L90
#from bidict import FrozenOrderedBidict, bidict, inverted 
# OVERWRITE
# OnDup, RAISE, DROP_OLD
# bidict, inverted, 
# class RelaxBidict(FrozenOrderedBidict):
    # __slots__ = ()
    # on_dup = OnDup(key=RAISE, val=DROP_OLD, kv=RAISE)
    # on_dup = OVERWRITE


def map_to(from_dict, map, to_dict):
    errors=[]
    for (k,v) in map.items():
        if not set_nested(to_dict, v, get_nested(from_dict, k)):
            errors.append({k,v})
    return errors

# def map_inverse(to_dict, map, from_dict):
#     errors=[]
#     for (k,v) in inverted(map):
#         if not set_nested(to_dict, v, get_nested(from_dict, k)):
#             errors.append({k,v})
#     return errors

# context = {
#         _c.SCHEMA_OPT_KEY : opt,
#         _c.SCHEMA_VERSION_KEY : version
#     }
# def _extract_iso(body, type, data, context):        
def _extract_iso(body, opt, version, key, data, errors, context):

    
    # DATA translation
    # root_fields = FrozenOrderedBidict({
    root_fields = {
        
        ('gmd:MD_Metadata','gmd:fileIdentifier','gco:CharacterString'):('fileIdentifier',),
        ('gmd:MD_Metadata','gmd:metadataStandardName','gco:CharacterString'):('metadataStandardName',), # TODO this could be an array
        ('gmd:MD_Metadata','gmd:characterSet','gmd:MD_CharacterSetCode','@codeListValue',):('characterSet',),
        ('gmd:MD_Metadata','gmd:identificationInfo','gmd:MD_DataIdentification','gmd:citation','gmd:CI_Citation','gmd:language','gco:CharacterString',):('language',),
        ('gmd:MD_Metadata','gmd:metadataStandardVersion','gco:CharacterString'):('metadataStandardVersion',),
        ('gmd:MD_Metadata','gco:CharacterString'):('parentIdentifier',),
        # TODO dataIdentification
        ('gmd:MD_Metadata','gmd:referenceSystemInfo','gmd:MD_ReferenceSystem','gmd:RS_Identifier','gmd:code','gco:CharacterString'):('referenceSystemIdentifier',),
        # TODO spatialRepresentationInfo
        ('gmd:MD_Metadata','gmd:dataQualityInfo','gmd:DQ_DataQuality','gmd:lineage','gmd:LI_Lineage','gmd:statement','gco:CharacterString'):('dataQualityInfo','lineage','statement',),
        # TODO dataQualityInfo complete LI_Lineage gmd:source

        ('gmd:MD_Metadata','gmd:identificationInfo','gmd:MD_DataIdentification','gmd:citation','gmd:CI_Citation','gmd:title','gco:CharacterString'):('title',),
        ('gmd:MD_Metadata','gmd:identificationInfo','gmd:MD_DataIdentification','gmd:citation','gmd:CI_Citation','gmd:abstract','gco:CharacterString'):('notes',),
        
        # ('gmd:MD_Metadata','gmd:identificationInfo','gmd:MD_DataIdentification','gmd:citation','gmd:CI_Citation','gmd:status','gmd:MD_ProgressCode','"@codeListValue',):('status',)

        # ('gmd:MD_Metadata','gmd:identificationInfo','gmd:MD_DataIdentification','gmd:citation','gmd:CI_Citation','gmd:alternateTitle','gco:CharacterString'):'alternateTitle'
    }
    _data = dict(data)
    _body = dict(body)

    # map body to ckan fields (_data)
    errors = map_to(_body, root_fields, _data)


    # complex_fields = FrozenOrderedBidict({
        # ('gmd:MD_Metadata','gmd:distributionInfo','gmd:MD_Distribution','gmd:transferOptions',):('transferOptions',),
        # ('gmd:MD_Metadata','gmd:MD_Metadata','gmd:identificationInfo','gmd:MD_DataIdentification','gmd:citation', 'gmd:CI_Citation'):('identificationInfo'),
    # })

    # Extract resources from body (to _data)
    _extract_transfer_options(_body, opt, version, key, _data, errors, context)
    
    
    # BODY: iso19139 to iso translation

    # body_fields = FrozenOrderedBidict({
    #     ('gmd:characterSet','gmd:MD_CharacterSetCode','@codeListValue',):('characterSet',)
    # })
    # errors = map_to(_body, body_fields, _body)

    body.update(_body)
    # TODO if errors:
    #     _v.stop_with_error('Unable to find citation info', key, errors)


    # TODO the rest of the model

    _data['url'] = h.url_for(controller = 'package', action = 'read', id = _data['name'], _external = True)

    # Update _data with changes
    data.update(_data)


def _extract_transfer_options(body, opt, version, key, data, errors, context):

    # _body = dict(body)
    _body = body
    # _data = dict(data)
    _transfer_options = get_nested(_body, ('gmd:MD_Metadata','gmd:distributionInfo','gmd:MD_Distribution','gmd:transferOptions',))
    #  = _data.pop(('transferOptions',))
    if _transfer_options:
        if not isinstance(_transfer_options, list):
            _transfer_options = [ _transfer_options ]
        for options in _transfer_options:

            # units = get_nested(options, ('gmd:unitsOfDistribution', 'gco:CharacterString',)) 
            # transferSize = get_nested(options, ('gmd:transferSize', 'gco:Real',))
            
            online = get_nested(options, ('gmd:MD_DigitalTransferOptions', 'gmd:onLine',))
            if not online:
                continue
            if isinstance(online, list):
                for idx, online_resource in enumerate(list(online)):
                    pop_online(online_resource, opt, TYPE_ONLINE_RESOURCE, version, key, data, errors, context)
                    online.remove(online_resource)
            else:
                pop_online(online, opt, type, version, key, data, errors, context)
                pop_nested(options, ('gmd:MD_DigitalTransferOptions', 'gmd:onLine',))

def pop_online(online_resource, opt, type, version, key, data, errors, context):
    if isinstance(online_resource, list):
            for resource in online_resource:
                get_online_resource(resource, opt, type, version, key, data, errors, context)
    else:
        get_online_resource(online_resource, opt, type, version, key, data, errors, context)

def get_online_resource(resource, opt, type, version, key, data, errors, context):
    r = resource.pop('gmd:CI_OnlineResource', None)
    if not r:
        return

    # we assume:
    # - body is an instance of gmd:CI_OnlineResource
    _body = dict(r)


    new_resource_body_fields = {
        # TODO otherwise do all here
        ('gmd:name', 'gco:CharacterString') : ('name',),
        ('gmd:description', 'gco:CharacterString') : ('description',),
        ('gmd:protocol', 'gco:CharacterString',) : ('protocol',),
        # ('gmd:linkage', 'gco:CharacterString') : ('linkage',),
    }
    _new_resource_body = {}
    errors = map_to(_body, new_resource_body_fields, _new_resource_body)


    # TODO recursive validation triggered by resource_create action ?
    new_resource_dict_fields = {
        # TODO otherwise do all here
        ('gmd:name','gco:CharacterString',) : ('name',),
        ('gmd:description','gco:CharacterString',) : ('description',),
        ('gmd:linkage','gmd:URL') : ('url',)
    }
    
    _new_resource_dict = {
        _c.SCHEMA_OPT_KEY: json.dumps(opt),
        _c.SCHEMA_VERSION_KEY: version,
        _c.SCHEMA_BODY_KEY: json.dumps(_new_resource_body),
        _c.SCHEMA_TYPE_KEY: type,
        # TODO FORMAT
    }
    
    errors = map_to(_body, new_resource_dict_fields, _new_resource_dict)


    
    # new_resource.update({
    #     'format': _get_type_from(protocol, new_resource.get('url')) or ''
    # })

    resources = data.get('resources', [])
    resources.append(_new_resource_dict)
    data.update({'resources': resources})

    # TODO remove from body what is not managed by json
    
