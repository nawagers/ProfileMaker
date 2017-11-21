"""Provide class page."""

import logging
from PIL import Image, ImageDraw, ImageFont


class page:
    """
    Summary.

    Detailed description

    Methods:
        __init__: Creates new instance

    Attributes:
        pagenumber: int of the page number to render on the page
        startdistance: float of the beginning distance on the page
        totaldistance: float of the total distance on the page
        POIs: list of POIs to show on the page
        elevations: list of trackpoints to print on the page
        pageheight: int of the height of the page in pixels
        pagewidth: int of width of the page in pixels
        plotleft: int of the left edge of the plot area in pixels
        plotbottom: int of the bottom edge of the plot area in pixels
        plotheight: int of the plot area height in pixels
        plotwidth: int of the plot area width in pixels
        reflected: bool whether to mirror certain parameters for even/odd
        DPI: int of the output image print resolution

    """

    def __init__(self):
        """
        Create a new instance of page.

        Args:
            initarg1: description
        """
        POIs = []
        elevations = []
        pageheight = 0
        pagewidth = 0
        pagenumber = 0
        startdistance = 0
        totaldistance = 0
        plotleft = 0
        plotbottom = 0
        reflected = False
        DPI = 0
        filename = ""
        fileext = ".png"

    def render(self):
        """
        Render and save all the page data.

        Detailed description

        Args:
            methodarg1: description

        Returns:
            description

        """
