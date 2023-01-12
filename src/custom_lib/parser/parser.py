from djangorestframework_camel_case.settings import api_settings
from djangorestframework_camel_case.util import underscoreize
from drf_nested_forms import NestedMultiPartParser


class CustomNestedParser(NestedMultiPartParser):
    json_underscoreize = api_settings.JSON_UNDERSCOREIZE

    def parse(self, stream, media_type=None, parser_context=None):
        data = super(CustomNestedParser, self).parse(stream=stream, media_type=media_type,
                                                     parser_context=parser_context)
        print(data)
        # return data
        return underscoreize(data, **self.json_underscoreize)
