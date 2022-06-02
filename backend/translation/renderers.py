"""
Provides XML rendering support.
"""
from io import StringIO

from django.utils.encoding import force_str
from django.utils.xmlutils import SimplerXMLGenerator
from rest_framework.renderers import BaseRenderer


class MyXMLRenderer(BaseRenderer):
    """
    Renderer which serializes to XML.
    """

    media_type = "application/xml"
    format = "xml"
    charset = "utf-8"
    item_tag_name = "error"
    root_tag_name = "matches"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """
        if data is None:
            return ""

        stream = StringIO()

        xml = SimplerXMLGenerator(stream, self.charset)
        xml.startDocument()
        self._to_xml(xml, data)

        xml.endDocument()
        return stream.getvalue()

    def _to_xml(self, xml, data):
        if isinstance(data, (list, tuple)):
            xml.startElement(self.root_tag_name, {})
            for item in data:
                self._to_xml(xml, item)
            xml.endElement(self.root_tag_name)

        elif isinstance(data, dict):
            xml.startElement(self.item_tag_name, data)
            xml.endElement(self.item_tag_name)

        elif data is None:
            # Don't output any value
            pass

        else:
            xml.characters(force_str(data))