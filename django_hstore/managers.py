from django.db import models

from django_hstore.query import HStoreQuerySet
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
        kwargs = util.serialize_queryset_arguments(self.hstore_fieldnames, **kwargs)
        return super(HStoreManager, self).filter(*args, **kwargs)

    def exclude(self, *args, **kwargs):
        kwargs = util.serialize_queryset_arguments(self.hstore_fieldnames, **kwargs)
        return super(HStoreManager, self).exclude(*args, **kwargs)

try:
    from django.contrib.gis.db import models as geo_models
    
    from django_hstore.query import HStoreGeoQuerySet


    class HStoreGeoManager(geo_models.GeoManager, HStoreManager):
        """
        Object manager combining Geodjango and hstore.
        """
        def get_query_set(self):
            return HStoreGeoQuerySet(self.model, using=self._db)
except ImportError as e:
    print("\033[93m"
            "\n--------------------------------------------"
            "\nFailed to import Django's GIS module.  Perhaps you do not have the GeoDjango requirements installed?  "
            "Continuing without GeoSpatial support."
            "\n\nError Details:\n%s" % e +
            "\n--------------------------------------------\n"
            "\033[0m")
    pass