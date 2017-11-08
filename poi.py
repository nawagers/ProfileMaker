"""Provide class POI."""


class POI:
    """
    Container for Points of Interest.

    This class is a basic container for holding gps track data.

    Methods:
        __init__: Creates new instance
        __lt__: Implements less than operator on distance for sorting
        getheight: Calculates the height of the wordwrapped text
        wordwrap: Finds the line breaks within the display text

    Attributes:
        distance: Float of the distance along the trail from the start
            in miles.
        elevation: Float of the elevation in feet.
        forwardtext: Str of description for rendering POI.
        textfont: ImageFont object used to render the text of
            forwardtext or backwardtext.
        services: Str indicates services at the POI.
        servicesfont: ImageFont that renders services. Usually a font
            of dingbats.
        fill: Str to print for visual alignment between forwardtext and
            services
        backwardtext: String of description for rendering the POIs in
            reverse order.
        marker: Variable of undefined type. Not used.
        offset: int that holds the pixel offset of the text. Positive
            is down relative to the text orientation.
        printable: Optional bool that determines if the instance should
            be displayed when rendering.

    """

    def __init__(self, distance, elevation, forwardtext, textfont, services='',
                 servicesfont=None, fill='.', backwardtext='', marker=None,
                 offset=0, printable=True):
        """
        Create a new instance of POI.

        Args:
            distance: Float of the distance along the trail from the
                start in miles.
            elevation: Float of the elevation in feet.
            forwardtext: Str of description for rendering POI.
            textfont: ImageFont object used to render the text of
                forwardtext or backwardtext.
            services: Optional str indicates services at the POI.
            servicesfont: Optional ImageFont that renders services.
                Usually a font of dingbats. Defaults to textfont.
            fill: Optional str to print for visual alignment between
                forwardtext and services
            backwardtext: Optional str of description for rendering
                the POIs in reverse order.
            marker: Optional variable of undefined type. Not used.
            offset: Optional int that holds the pixel offset of the text.
                Positive is down relative to the text orientation.
            printable: Optional bool that determines if the instance
                should be displayed when rendering.
        """
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
        """
        Return the height of the wordwrapped text.

        Calculates the height of the text by using the wordwrap function
        to get the total number of lines of either the forwardtext or
        backwardtext. Each line length is bounded by the corresponding
        element in lengths. If there are more lines than lengths, the
        last element in lengths is the bound for all subsequent lines.

        Args:
            lengths: A sequence of ints representing the max rendered
                width of each line of text
            verticaladvance: Optional int for the height of individual
                line
            backward: Optional bool that when True uses backwardtext
                instead of forwardtext

        Returns:
            An int of the total height of text in pixels

        """
        if verticaladvance is None:
            verticaladvance = max(self.textfont.font.height,
                                  self.servicesfont.font.height)
        return len(self.wordwrap(lengths)) * verticaladvance

    def __lt__(self, other):
        """Return True if self.distance is less than other.distance."""
        return self.distance < other.distance

    def wordwrap(self, lengths, backward=False):
        r"""
        Break the text into chunks suitable for one line.

        Separates the text on all '\n' and any space when the length of
        the rendered line of text exceeds the max line length in the
        sequence lengths. If there is no appropriate space character the
        function will divide after the character that fits. If there are
        more lines of text than provided in lengths, the last length is
        used for all subsequent lines.

        Args:
            lengths: A sequence of ints representing the max rendered
                width of each line of text
            backward: Optional bool that when True uses backwardtext
                instead of forwardtext

        Returns:
            A list of str containing all of forwardtext or backwardtext
            broken up into lines.

        """
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
                while (self.textfont.getsize(paragraph[:nextspace])[0] <
                       lengths[currentline]):
                    # next word still fits on line
                    curspace = nextspace
                    nextspace = paragraph.find(' ', nextspace+1)
                    if nextspace == -1:
                        # no spaces left (end occurs on last word)
                        break
                if curspace == -1:
                    # current word exceed max by itself
                    curspace = 0
                    while (self.textfont.getsize(paragraph[:curspace])[0] <
                           lengths[currentline]):
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
