class Configuration:

    def __init__(self, path, headless, deep_scrape, start_page, end_page,
                 all_pages, export, export_path, export_extension, print_events):
        self.chromedriver_path = path
        self.headless = headless
        self.deep_scrape = deep_scrape
        self.start_page = start_page
        self.end_page = end_page
        self.all_pages = all_pages
        self.export = export
        self.export_path = export_path
        self.export_extension = export_extension
        self.print_events = print_events
