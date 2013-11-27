from django.db import models, connection
from django.utils.translation import ugettext_lazy as _

from django_hstore import forms, util


class HStoreDictionary(dict):
    """
    A dictionary subclass which implements hstore support.
    """
    def __init__(self, value=None, field=None, instance=None, **params):
        super(HStoreDictionary, self).__init__(value, **params)
        self.field = field
        self.instance = instance

    def remove(self, keys):
        """
        Removes the specified keys from this dictionary.
        """
        queryset = self.instance._base_manager.get_query_set()
        queryset.filter(pk=self.instance.pk).hremove(self.field.name, keys)


class HStoreReferenceDictionary(HStoreDictionary):
    """
    A dictionary which adds support to storing references to models
    """
    def __getitem__(self, *args, **kwargs):
        value = super(self.__class__, self).__getitem__(*args, **kwargs)
        # if value is a string it needs to be converted to model instance
        if isinstance(value, basestring):
            reference = util.acquire_reference(value)
            self.__setitem__(args[0], reference)
            return reference
        # otherwise just return the relation
        return value
    
    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


class HStoreDescriptor(models.fields.subclassing.Creator):
    def __set__(self, obj, value):
        value = self.field.to_python(value)
        if isinstance(value, dict):
            value = HStoreDictionary(
                value=value, field=self.field, instance=obj
            )
        obj.__dict__[self.field.name] = value


class HStoreReferenceDescriptor(models.fields.subclassing.Creator):
    def __set__(self, obj, value):
        value = self.field.to_python(value)
        if isinstance(value, dict):
            value = HStoreReferenceDictionary(
                value=value, field=self.field, instance=obj
            )
        obj.__dict__[self.field.name] = value


class HStoreField(models.Field):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('db_index', True)
        super(HStoreField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super(HStoreField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, HStoreDescriptor(self))

    def get_default(self):
        """
        Returns the default value for this field.
        """
        if self.has_default():
            if callable(self.default):
                return self.default()
            return self.default
        if (
            not self.empty_strings_allowed or 
                (
                self.null
                and not connection.features.interprets_empty_strings_as_nulls
                )
            ):
            return None
        return {}

    def value_to_string(self, obj):
        return self._get_val_from_obj(obj)

    def db_type(self, connection=None):
        return 'hstore'

    def south_field_triple(self):
        from south.modelsinspector import introspector
        name = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        args, kwargs = introspector(self)
        return name, args, kwargs


class DictionaryField(HStoreField):
    description = _("A python dictionary in a postgresql hstore field.")

    def formfield(self, **params):
        params['form_class'] = forms.DictionaryField
        return super(DictionaryField, self).formfield(**params)

    def _value_to_python(self, value):
        return value

    def get_prep_value(self, value):
        if value:
            value = util.json_serialize_dict(value)
        return super(DictionaryField, self).get_prep_value(value)

    def to_python(self, value):
        value = super(DictionaryField, self).to_python(value)
        if value:
            return util.json_unserialize_dict(value)
        else:
            return {}


class ReferencesField(HStoreField):
    description = _("A python dictionary of references to model instances in an hstore field.")
    
    def contribute_to_class(self, cls, name):
        super(ReferencesField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, HStoreReferenceDescriptor(self))

    def formfield(self, **params):
        params['form_class'] = forms.ReferencesField
        return super(ReferencesField, self).formfield(**params)

    def get_prep_lookup(self, lookup, value):
        if isinstance(value, dict):
            return util.serialize_references(value)
        return value

    def get_prep_value(self, value):
        return util.serialize_references(value)

    def to_python(self, value):
        return value if isinstance(value, dict) else HStoreReferenceDictionary({})

    def _value_to_python(self, value):
        return util.acquire_reference(value)


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(rules=[], patterns=['django_hstore\.hstore'])
except ImportError:
    pass
