class Event:

    def __init__(self, title, link, start, end):
        self.title = title
        self.link = link
        self.start = start
        self.end = end

    def __str__(self):
        return '{}\n{}\nStart: {}\nEnd: {}\n'.format(self.title,
                                                     self.link,
                                                     self.start.strftime('%m/%d/%Y %I:%M %p %Z%z'),
                                                     self.end.strftime('%m/%d/%Y %I:%M %p %Z%z'))

    def __repr__(self):
        return self.__str__()
