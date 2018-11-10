class Configuration:

    def __init__(self, path, headless, start_page, end_page, all_pages, output, output_path):
        self.chromedriver_path = path
        self.headless = headless
        self.start_page = start_page
        self.end_page = end_page
        self.all_pages = all_pages
        self.output = output
        self.output_path = output_path
        self.output_extension = output_path.rsplit(',', 1)[-1].lower()
