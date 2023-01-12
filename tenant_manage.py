#!/usr/bin/env python
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ims.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    from django.db import connection, connections

    args = sys.argv
    schema = args[1]

    with connection.cursor() as cursor:
        connections['log_db'].cursor().execute(f"SET search_path to {schema}")
        cursor.execute(f"SET search_path to {schema}")
        del args[1]
        execute_from_command_line(args)
