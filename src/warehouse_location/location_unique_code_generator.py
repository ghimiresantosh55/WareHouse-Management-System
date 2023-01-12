from .models import Location


def generate_location_code(prefix, parent_level: int, parent_id):

    count = Location.objects.filter(level=parent_level+1, parent=parent_id).count()
    if parent_level == -1:
        code = prefix + str(count+1).zfill(1)
    else:
        code = prefix + str(count+1).zfill(2)
    return code
