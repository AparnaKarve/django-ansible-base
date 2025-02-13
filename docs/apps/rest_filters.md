# Filtering and Sorting

django-ansible-base has a built in mechanism for filtering and sorting query sets based on django-rest-framework Filters.

## Settings

Add `ansible_base.rest_filters` to your installed apps:

```
INSTALLED_APPS = [
    ...
    'ansible_base.rest_filters',
]
```

### Additional Settings
Additional settings are required to enable filtering on your rest endpoints.
This will happen automatically if using [dynamic_settings](../Installation.md)

To manually enable filtering without dynamic settings the following items need to be included in your settings:
```
REST_FRAMEWORK = {
    ...
    'DEFAULT_FILTER_BACKENDS': (
        'ansible_base.rest_filters.rest_framework.type_filter_backend.TypeFilterBackend',
        'ansible_base.rest_filters.rest_framework.field_lookup_backend.FieldLookupBackend',
        'rest_framework.filters.SearchFilter',
        'ansible_base.rest_filters.rest_framework.order_backend.OrderByBackend',
    ),
    ...
}
```

## Letting Extra Query Params Through

Sometimes you may have a view that needs to use a query param for a reason unrelated to filtering.
If the rest_filters filtering is enabled, then this will not work, resulting in a 400 response code
due to the model not having an expected field.

To deal with this, after including the dynamic settings, you can add your field to the "reserved" list:

```python
from ansible_base.lib import dynamic_config
dab_settings = os.path.join(os.path.dirname(dynamic_config.__file__), 'dynamic_settings.py')
include(dab_settings)

ANSIBLE_BASE_REST_FILTERS_RESERVED_NAMES += ('extra_querystring',)
```

This will prevent 400 errors for requests like `/api/v1/organizations/?extra_querystring=foo`.
No filtering would be done in this case, the query string would simply be ignored.

If you want to do this on a view level, not for the whole app, then add `rest_filters_reserved_names` to the view.

```python
class CowViewSet(ModelViewSet, AnsibleBaseView):
    serializer_class = MySerializer
    queryset = MyModel.objects.all()
    rest_filters_reserved_names = ('extra_querystring',)
```

## Preventing Field Searching

### prevent_search function

Sensitive fields like passwords should be excluded from being searched. To do there is there a function called `prevent_search` which can wrap your model fields like:

```
from ansible_base.lib.utils.models import prevent_search

class Authenticator(UniqueNamedCommonModel):
   ...
   configuration = prevent_search(JSONField(default=dict, help_text="The required configuration for this source"))
   ...
```

If you add fields to prevent searching on its your responsibility to add unit/functional tests to ensure that data is not exposed. Here is an example of a test:
```
@pytest.mark.parametrize(
    'model, query',
    [
        (Authenticator, 'configuration__icontains'),
    ],
)
def test_filter_sensitive_fields_and_relations(model, query):
    field_lookup = FieldLookupBackend()
    with pytest.raises(PermissionDenied) as excinfo:
        field, new_lookup = field_lookup.get_field_from_lookup(model, query)
    assert 'not allowed' in str(excinfo.value)
```

### PASSWORD_FIELDS

Another option available is `PASSWORD_FIELDS` which can explicitly protect password fields on your models like:

```
class MyModel(CommonModel):

    PASSWORD_FIELDS = ['inputs']
```

In this example, the `inputs` field of MyModel would be excluded from being searched.
