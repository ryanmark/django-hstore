from django.db import models
from django.contrib.gis.db import models as geo_models
from django_hstore.query import HStoreQuerySet, HStoreGeoQuerySet

from django_hstore import util


class HStoreManager(models.Manager):
    """
    Object manager which enables hstore features.
    """
    use_for_related_fields = True

    def __init__(self, hstore_fieldnames=(), *args, **kwargs):
        self.hstore_fieldnames = hstore_fieldnames
        super(HStoreManager, self).__init__(*args, **kwargs)

    def get_query_set(self):
        return HStoreQuerySet(self.model, using=self._db)

    def hkeys(self, attr, **params):
        return self.filter(**params).hkeys(attr)

    def hpeek(self, attr, key, **params):
        return self.filter(**params).hpeek(attr, key)

    def hslice(self, attr, keys, **params):
        return self.filter(**params).hslice(attr, keys)

    def filter(self, *args, **kwargs):
        kwargs = self._serialize_hstore_arguments(**kwargs)
        return super(HStoreManager, self).filter(*args, **kwargs)

    def exclude(self, *args, **kwargs):
        kwargs = self._serialize_hstore_arguments(**kwargs)
        return super(HStoreManager, self).exclude(*args, **kwargs)

    def _serialize_hstore_arguments(self, *args, **kwargs):
        for k,v in kwargs.items():
            # Only serialize for filters where both:
            # a) the filter has double underscores (data__contains={'a': 1}), rather
            #    than equivalence filters (data={'a': 1, 'b': 2}) where serialization
            #    takes place in DictionaryField.get_prep_value().
            # b) the field being used for the filter is provided as a string in the 
            #    hstore_fieldnames tuple used when declaring the manager in the object
            #    model.
            if (len(k.split('__')) > 1) and (k.split('__')[0] in self.hstore_fieldnames):
                kwargs[k] = util.json_serialize_dict(v)
        return kwargs


class HStoreGeoManager(geo_models.GeoManager, HStoreManager):
    """
    Object manager combining Geodjango and hstore.
    """
    def get_query_set(self):
        return HStoreGeoQuerySet(self.model, using=self._db)
