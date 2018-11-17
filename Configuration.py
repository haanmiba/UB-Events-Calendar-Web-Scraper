class Configuration:
    """
    A class used to represent the configurations for program execution

    Attributes
    ----------
    chromedriver_path : str
        the file path to the ChromeDriver executable
    headless : bool
        whether or not the ChromeDriver should run headless (w/o GUI)
    deep_scrape : bool
        whether or not the web scraper will `deep scrape` (extract additional info from individual event pages)
    start_page : int
        the page of the UB Events Calendar where the web scraper will begin scraping events
    end_page : int
        the page of the UB Events Calendar where the web scraper will stop scraping events (at bottom of page)
    all_pages : bool
        whether or not the web scraper will scrape from all pages
    export : bool
        whether or not the scraped events will be exported to an external file
    overwrite : bool
        whether or not an external file with the same name as `export_path` is allowed to be overwritten
    export_path : str
        the destination file path for the exported file
    export_extension : str
        the file type of the exported file
    print_events : bool
        whether or not scraped events will be printed to the command line
    """

    def __init__(self, path, headless, deep_scrape, start_page, end_page, all_pages,
                 export, overwrite, export_path, export_extension, print_events):
        """
        Parameters
        ----------
        path : str
            The file path to the chromedriver
        headless : bool
            Whether or not the chromedriver should run headless (w/o GUI)
        deep_scrape : bool
            Whether or not the web scraper will `deep scrape` (extract additional info from individual event pages)
        start_page : int
            The page of the UB Events Calendar where the web scraper will begin scraping events
        end_page : int
            The page of the UB Events Calendar where the web scraper will stop scraping events (at bottom of page)
        all_pages : bool
            Whether or not the web scraper will scrape from all pages
        export : bool
            Whether or not the scraped events will be exported to an external file
        overwrite : bool
            Whether or not an external file with the same name as `export_path` is allowed to be overwritten
        export_path : str
            The destination file path for the exported file
        export_extension : str
            The file type of the exported file
        print_events : bool
            Whether or not scraped events will be printed to the command line
        """

        self.chromedriver_path = path
        self.headless = headless
        self.deep_scrape = deep_scrape
        self.start_page = start_page
        self.end_page = end_page
        self.all_pages = all_pages
        self.export = export
        self.overwrite = overwrite
        self.export_path = export_path
        self.export_extension = export_extension
        self.print_events = print_events
