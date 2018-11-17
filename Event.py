class Event:
    """
    A class used to represent an event from the University at Buffalo Events Calendar

    Attributes
    ----------
    title : str
        the title of the event
    link : str
        a hyperlink to the event's page
    start : str
        a formatted string (MM/DD/YYYY HH:MM AM/PM UTC-OFFSET) representing the start time of the event
    end : str
        a formatted string (MM/DD/YYYY HH:MM AM/PM UTC-OFFSET) representing the end time of the event
    description : str
        description of the event
    location : str
        location of the event
    contact : dict
        contact information for the event (name of host, phone number, email)
    additional_info : dict
        additional information for the event
    """

    def __init__(self, title, link, start, end):
        """
        Parameters
        ----------
        title : str
            The title of the event
        link : str
            A hyperlink to the event's page
        start : str
            A formatted string (MM/DD/YYYY HH:MM AM/PM UTC-OFFSET) representing the start time of the event
        end : str
            A formatted string (MM/DD/YYYY HH:MM AM/PM UTC-OFFSET) representing the end time of the event
        """

        self.title = title
        self.link = link
        self.start = start
        self.end = end
        self.description = None
        self.location = None
        self.contact = None
        self.additional_info = None

    def __str__(self):
        return 'Title: {}\nLink:  {}\nStart: {}\nEnd:   {}\n\n'.format(self.title, self.link, self.start, self.end)

    def __repr__(self):
        return self.__str__()
