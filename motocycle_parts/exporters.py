from scrapy.exporters import JsonLinesItemExporter


class MyJsonLinesItemExporter(JsonLinesItemExporter):
    def __init__(self, file, **kwargs):
        super(MyJsonLinesItemExporter, self).__init__(file, ensure_ascii=False, **kwargs)