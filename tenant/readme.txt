Commands to perform for launching tenants without any erros

1) Set default db for data
2) create 'log_db' for logging data
2) perform command: python manage.py makemigrations
3) perform command: python manage.py migrate tenant
4) Create tenants from python shell: python manage.py shell
    from tenant.models import Tenant
    tenant = Tenant.objects.create(name="tenant_name", schema_name="schema", sub_domain ="sub_domain_for_schema")
5) Perform primary_db and log_db migration : python manage.py create_schemas
7) create super users for schemas : python tenant_manage.py [schema_name] createsuperuser

                                all done enjoy !!!!!