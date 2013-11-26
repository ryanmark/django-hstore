from django.db import models
from django_hstore.query import HStoreQuerySet

from django_hstore import util


class HStoreManager(models.Manager):
    """
    Object manager which enables hstore features.
    """
    use_for_related_fields = True

    def get_query_set(self):
        return HStoreQuerySet(self.model, using=self._db)

    def hkeys(self, attr, **params):
        return self.filter(**params).hkeys(attr)

    def hpeek(self, attr, key, **params):
        return self.filter(**params).hpeek(attr, key)

    def hslice(self, attr, keys, **params):
        return self.filter(**params).hslice(attr, keys)

    def filter(self, *args, **kwargs):
        for k,v in kwargs.items():
            # Only serialize for filters with double underscores (data__contains={'a': 1}),
            # rather than equivalence filters (data={'a': 1, 'b': 2}) where serialization
            # takes place in DictionaryField.get_prep_value().
            if (len(k.split('__')) > 1) and (k.split('__')[0] == 'data'): # TODO: This check to insure that the arg name is 'data' was added to keep the filter serializer from interfering with the ability to filter other non-hstore fields. We should find a new way to find out which fields are hstore fields, rather than hard-coding the field name in.
                kwargs[k] = util.json_serialize_dict(v)
        return super(HStoreManager, self).filter(*args, **kwargs)
