"""
Provide funtion various functions.

Functions:
    fastdist: Quickly calculates distance between two GPS coordinates
"""

import math

def fastdist(lat1, lon1, lat2, lon2, mu):
    """
    Approximate the distance between two points

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
