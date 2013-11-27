from django_hstore.fields import DictionaryField, ReferencesField
from django_hstore.managers import HStoreManager

try: 
	from django_hstore.managers import HStoreGeoManager
except ImportError:
	pass
