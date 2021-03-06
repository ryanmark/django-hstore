import datetime

try: import simplejson as json
except ImportError: import json
from django.core.exceptions import ObjectDoesNotExist


def acquire_reference(reference):
    try:
        implementation, identifier = reference.split(':')
        module, sep, attr = implementation.rpartition('.')
        implementation = getattr(__import__(module, fromlist=(attr,)), attr)
        return implementation.objects.get(pk=identifier)
    except ObjectDoesNotExist:
        return None
    except Exception:
        raise ValueError


def identify_instance(instance):
    implementation = type(instance)
    return '%s.%s:%s' % (implementation.__module__, implementation.__name__, instance.pk)


def serialize_references(references):
    refs = {}
    # if None or string return empty dict
    if references is None or isinstance(references, basestring):
        return {}
    # if dictionary do serialization
    elif isinstance(references, dict):
        for key, instance in references.iteritems():
            if not isinstance(instance, basestring):
                refs[key] = identify_instance(instance)
            else:
                refs[key] = instance
        else:
            return refs
    # else just return the object, might be doing some other operation and we don't want to interfere
    else:
        return references


def unserialize_references(references):
    refs = {}
    if references is None:
        return refs
    for key, reference in references.iteritems():
        if isinstance(reference, basestring):
            refs[key] = acquire_reference(reference)
        else:
            refs[key] = reference
    else:
        return refs


def json_serialize_dict(d):
    return dict([(k, json_serialize_value(v)) for k,v in d.items()])


def json_unserialize_dict(d):
    try:
        d = dict([(k, json_unserialize_value(v)) for k,v in d.items()])
    except TypeError:
        pass
    return d


def json_serialize_value(value):
    value = stringify_datetime(value)
    return json.dumps(value)


def json_unserialize_value(value):
    try:
        value = json.loads(value)
    except ValueError:
        pass
    value = destringify_datetime(value)
    return value


def serialize_queryset_arguments(hstore_fieldnames, *args, **kwargs):
    for k,v in kwargs.items():
        # Only serialize for filters where both:
        # a) the filter has double underscores (data__contains={'a': 1}), rather
        #    than equivalence filters (data={'a': 1, 'b': 2}) where serialization
        #    takes place in DictionaryField.get_prep_value().
        # b) the field name that the data is being filtered by is provided as a
        #    string in the  hstore_fieldnames tuple used when declaring the manager
        #    in the object model.
        # c) the filter value is a dict or a numeral
        if (len(k.split('__')) > 1) and (k.split('__')[0] in hstore_fieldnames):
            if isinstance(v, dict):
                kwargs[k] = json_serialize_dict(v)
            if isinstance(v, int) or isinstance(v, float):
                kwargs[k] = json_serialize_value(v)
    return kwargs


def stringify_datetime(value):
    if isinstance(value, datetime.datetime):
        value = datetime.datetime.strftime(value, '%Y-%m-%d %H:%M:%S.%f')
    elif isinstance(value, datetime.date):
        value = datetime.date.strftime(value, '%Y-%m-%d')
    elif isinstance(value, datetime.time):
        value = datetime.time.strftime(value, '%H:%M:%S.%f')
    return value


def destringify_datetime(value):
    if type(value) is str:
        # Try Datetime
        if len(value) is 26:
            try:
                value = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                pass
        # Try Date
        elif len(value) is 10:
            try:
                value = datetime.datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                pass
        # Try Time
        elif len(value) is 15:
            try:
                value = datetime.datetime.strptime(value, '%H:%M:%S.%f').time()
            except ValueError:
                pass
    return value
