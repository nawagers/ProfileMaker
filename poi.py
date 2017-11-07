from PIL import ImageFont


class POI:
    #Needs DistanceFromStart, Elevation, ForwardText, BackwardText
    # Services, MarkerType, RenderOffset, Printable, TextFont, ServicesFont
    # Fill
    def __init__(self, distance, elevation, forwardtext, textfont, services='',
                  servicesfont=None, fill='.',backwardtext='', marker=None,
                 offset=0, printable=True):
        self.distance = distance
        self.elevation = elevation
        self.forwardtext = forwardtext
        self.services = services
        self.fill = fill
        self.backwardtext = backwardtext
        self.marker = marker
        self.offset = offset
        self.printable = printable
        self.textfont = textfont
        if servicesfont is None:
            self.servicesfont = textfont
        else:
            self.servicesfont = servicesfont


    def getheight(self, lengths, verticaladvance=None, backward=False):
        if verticaladvance is None:
            verticaladvance = max(self.textfont.font.height, self.servicesfont.font.height)
        return len(self.wordwrap(lengths)) * verticaladvance

        
    def __lt__(self, other):
        return self.distance < other.distance


    def wordwrap(self, lengths, backward=False):
        text = self.backwardtext if backward else self.forwardtext
        lines = []
        currentline = 0
        text = text.strip(' ')
        for paragraph in text.split('\n'):
            # Run each paragraph separate to preserve line breaks
            while self.textfont.getsize(paragraph)[0] > lengths[currentline]:
                # Remaining text exceeds max, find split point
                curspace = -1
                nextspace = paragraph.find(' ')
                while self.textfont.getsize(paragraph[:nextspace])[0] < lengths[currentline]:
                    # next word still fits on line
                    curspace = nextspace
                    nextspace = paragraph.find(' ', nextspace+1)
                    if nextspace == -1:
                        #no spaces left (end occurs on last word)
                        break
                if curspace == -1:
                    # current word exceed max by itself
                    curspace = 0
                    while self.textfont.getsize(paragraph[:curspace])[0] < lengths[currentline]:
                        # find the last character that fits
                        curspace += 1
                    lines.append(paragraph[:curspace].strip(' '))
                    if currentline < len(lengths)-1: 
                        currentline += 1
                    paragraph = paragraph[curspace:].strip(' ')
                else:
                    # current word is last one that fits
                    lines.append(paragraph[:curspace].strip(' '))
                    if currentline < len(lengths)-1: 
                        currentline += 1
                    paragraph = paragraph[curspace+1:].strip(' ')
            if len(paragraph) > 0:
                # remaining text is less than max length
                lines.append(paragraph)
                if currentline < len(lengths)-1: 
                        currentline += 1
        return(lines)
