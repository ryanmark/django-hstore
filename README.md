# django-hstore

Django-hstore is a niche library which integrates the [hstore](http://www.postgresql.org/docs/9.0/interactive/hstore.html) extension of PostgreSQL into Django,
assuming one is using Django 1.2+, PostgreSQL 9.0+, and Psycopg 2.3+.

## Fork features

This fork aims to support data-types beyond strings.  To do so, all values entered in to / retrived from django-hstore are serialized to / from JSON.

## Limitations

- Due to how Django implements its ORM, you will need to use the custom ``postgresql_psycopg2`` backend
  defined in this package, which naturally will prevent you from dropping in other django extensions
  which require a custom backend (unless you fork and combine).
- PostgreSQL's implementation of hstore has no concept of type; it stores a mapping of string keys to
  string values. ~~This library makes no attempt to coerce keys or values to strings.~~ As such, this library encodes all values to JSON.

## Running the tests

Assuming one has the dependencies installed as well as nose, and a PostgreSQL 9.0+ server up and running::

    DB_USER=<username> HSTORE_SQL=<path-to-contrib/hstore.sql> ./runtests

## Usage

First, update your settings module to specify the custom database backend::

    DATABASES = {
        'default': {
            'ENGINE': 'django_hstore.postgresql_psycopg2',
            ...
        }
    }

The library provides three principal classes:

* ``django_hstore.hstore.DictionaryField``
    * An ORM field which stores a mapping of string key/value pairs in an hstore column.
* ``django_hstore.hstore.ReferencesField``
    * An ORM field which builds on DictionaryField to store a mapping of string keys to django object references, much like ForeignKey.
* ``django_hstore.hstore.Manager``
    * An ORM manager which provides much of the query functionality of the library.

Model definition is straightforward::

    from django.db import models
    from django_hstore import hstore

    class Something(models.Model):
        name = models.CharField(max_length=32)
        data = hstore.DictionaryField(db_index=True)
        objects = hstore.Manager()

        def __unicode__(self):
            return self.name

You then treat the ``data`` field as simply a dictionary of string pairs::

    instance = Something.objects.create(name='something', data={'a': '1', 'b': '2'})
    assert instance.data['a'] == '1'

    empty = Something.objects.create(name='empty')
    assert empty.data == {}

    empty.data['a'] = '1'
    empty.save()
    assert Something.objects.get(name='something').data['a'] == '1'

You can issue indexed queries against hstore fields::

    # equivalence
    Something.objects.filter(data={'a': '1', 'b': '2'})

    # subset by key/value mapping
    Something.objects.filter(data__contains={'a': '1'})

    # subset by list of keys
    Something.objects.filter(data__contains=['a', 'b'])

    # subset by single key
    Something.objects.filter(data__contains='a')

You can also take advantage of some db-side functionality by using the manager::

    # identify the keys present in an hstore field
    >>> Something.objects.hkeys(id=instance.id, attr='data')
    ['a', 'b']

    # peek at a a named value within an hstore field
    >>> Something.objects.hpeek(id=instance.id, attr='data', key='a')
    '1'

    # do the same, after filter
    >>> Something.objects.filter(id=instance.id).hpeek(attr='data', key='a')
    '1'

    # remove a key/value pair from an hstore field
    >>> Something.objects.filter(name='something').hremove('data', 'b')

The hstore methods on manager pass all keyword arguments aside from ``attr`` and ``key``
to ``.filter()``.
