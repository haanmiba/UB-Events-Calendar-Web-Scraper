class Configuration:

    def __init__(self, path, start_page, end_page, all_pages, output, output_path, output_mode):
        self.chromedriver_path = path
        self.start_page = start_page
        self.end_page = end_page
        self.all_pages = all_pages
        self.output = output
        self.output_path = output_path
        self.output_mode = output_mode

    def __str__(self):
        return '''-------------
        CONFIGURATION
        -------------
        Chromedriver Path: {}
        Start Page: {}
        End Page: {}
        All Pages: {}
        Output: {}
        Output Path: {}
        Output Mode: {}'''.format(self.chromedriver_path, self.start_page, self.end_page, self.all_pages,
                                  self.output, self.output_path, self.output_mode)

    def __repr__(self):
        return self.__str__()
