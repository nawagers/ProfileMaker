"""
Provide various functions and helper classes.

Classes:
    maxloglevel: Filters out log messages above a set level
Functions:
    fastdist: Quickly calculates distance between two GPS coordinates

"""

import logging


def fastdist(lat1, lon1, lat2, lon2, mu):
    """
    Approximate the distance between two points.

    Calculates the 2D Euclidean distance between two points using a planar
    projection from a spherical earth model. When both points lie between 25
    and 50 degrees latitude, the errors are under 1% for up to 4 degrees change
    in latitude and longitude (each) when mu is cos(lat1) and around 2% over a
    span of 50 degrees longitude when mu is cos((lat1-lat2)/2). The algorithm
    is meant to be fast when only comparative approximations are needed such
    as Knuth's "Post-office problem". The argument mu should be calculated
    only once outside of any loops. Be sure to convert to radians if the cos
    function requires it, like math.cos(). This function does not work over the
    180th meridian. |lon1-lon2| must be < 180.

    Example usage 1 (Find closest point in coordinates[] to POI):
        mu = math.cos(math.radians(POI.latitude))
        closestpoint = coordinates[0]
        mindist = fastdist(coordinates[0].latitude, coordinates[0].longitude,
                           POI.latitude, POI.longitude, mu)
        for point in coordinates:
            dist = FastDist(point.latitude, point.longitude,
                            POI.latitude, POI.longitude, mu)
            if dist < mindist:
                mindist = dist
                closestpoint = point

    Example usage 2 (Approximate the distance in meters):
        mu = math.cos(math.radians((point1.latitude + point2.latitude))/2)
        dist = math.sqrt(fastdist(point1.latitude, point1.longitude,
                                  point2.latitude, point2.longitude, mu))
                                  * 110946)

    Args:
        lat1: A float in Decimal Degrees of the latitude of point 1
        lon1: A float in Decimal Degrees of the longitude of point 1
        lat2: A float in Decimal Degrees of the latitude of point 2
        lon2: A float in Decimal Degrees of the longitude of point 2
        mu: A float of the scaling factor applied to longitude to equate
            it to equatorial degrees latitude, typically cos(lat1) in radians

    Returns:
        A float containing distance in equatorial degrees squared

    """
    return (lat1 - lat2) ** 2 + ((mu * (lon1 - lon2)) ** 2)


class MaxLogLevel(logging.Filter):
    """
    Filter the log handler to set a maximum log level.

    Inherit from logging.Filter. Set the maximum log level captured by
    the handler to remove higher levels.

    Methods:
        __init__: Extend super.__init__ to create new instance
        filter: Extend super.filter to remove log levels higher than
            maximum

    """

    def __init__(self, maximum, name=""):
        """
        Create new instance of MaxLogLevel.

        Args:
            maximum: logging level not to exceed
            name: str of logging channel to apply the filter. If name is
                "" then the filter applies to all channels.
        """
        super(MaxLogLevel, self).__init__(name)
        self.max_level = maximum

    def filter(self, record):
        """
        Suppress records when the level is too high or wrong channel.

        Extends Filter.filter to additionally suppress log messages which
        exceed the maximum level. For example if the filter maximum is
        logging.INFO and the record.levelno is logging.WARNING the filter
        will return 0 causing the Logger instance to ignore it. The name
        filtering of Filter.filter is preserved. If the filter is set to
        accept "A" it will pass when record.name is "A" or "A.*", where *
        is any number of "." separated substrings.

        Args:
            record: LogRecord instance to be filtered

        Returns:
            zero if record should be suppressed, non-zero otherwise

        """
        if record.levelno <= self.max_level:
            return super(MaxLogLevel, self).filter(record)
        return 0
