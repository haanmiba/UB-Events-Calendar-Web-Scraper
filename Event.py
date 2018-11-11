class Event:

    def __init__(self, title, link, start, end):
        self.title = title
        self.link = link
        self.start = start
        self.end = end

    def __str__(self):
        return 'Title: {}\nLink: {}\nStart: {}\nEnd: {}\n\n'.format(self.title, self.link, self.start, self.end)

    def __repr__(self):
        return self.__str__()
