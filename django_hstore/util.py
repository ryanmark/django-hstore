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
    import ipdb; ipdb.set_trace();
    refs = {}
    for key, instance in references.iteritems():
        if not isinstance(instance, basestring):
            refs[key] = identify_instance(instance)
        else:
            refs[key] = instance
    else:
        return refs


def unserialize_references(references):
    import ipdb; ipdb.set_trace();
    refs = {}
    for key, reference in references.iteritems():
        if isinstance(reference, basestring):
            refs[key] = acquire_reference(reference)
        else:
            refs[key] = reference
    else:
        return refs


def json_serialize_dict(dikt):
    return dict([(k, json_serialize_value(v)) for k,v in dikt.items()])


def json_unserialize_dict(dikt):
    try:
        dikt = dict([(k, json_unserialize_value(v)) for k,v in dikt.items()])
    except TypeError:
        pass
    return dikt


def json_serialize_value(value):
    return json.dumps(value)


def json_unserialize_value(value):
    return json.loads(value)
