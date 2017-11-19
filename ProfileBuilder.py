# imports
from geopy.distance import vincenty
from PIL import Image, ImageDraw, ImageFont
import math
import gpxpy
import srtm
import configparser
import os.path

from poi import POI
from utils import fastdist

ConfigFileName = os.path.abspath("TestData/NET.ini")
Config = configparser.ConfigParser()
Config.read(ConfigFileName)


# GPX File
TrackFile = Config.get("InputFiles", "TrackFile")
if not os.path.isabs(TrackFile):
    TrackFile = os.path.join(os.path.dirname(ConfigFileName), TrackFile)
TrackFile = os.path.normpath(TrackFile)

if not os.path.isfile(TrackFile):
    print("Track File does not exists: ", TrackFile)
    raise FileNotFoundError

WaypointFile = Config.get("InputFiles", "WaypointFile")
if len(WaypointFile) == 0:
    WaypointFile = TrackFile
elif not os.path.isabs(WaypointFile):
    WaypointFile = os.path.join(os.path.dirname(ConfigFileName), WaypointFile)
WaypointFile = os.path.normpath(WaypointFile)
if not os.path.isfile(WaypointFile):
    print("Waypoint File does not exists: ", WaypointFile)
    raise FileNotFoundError

TrackNumber = int(Config.get("InputFiles", "TrackNumber"))

# PlotSave
OutputDir = Config.get("OutputFiles", "OutputDir")
if not os.path.isabs(OutputDir):
    OutputDir = os.path.join(os.path.dirname(ConfigFileName), OutputDir)
if not os.path.isdir(OutputDir):
    print("Error: " + OutputDir + " is not a directory")
    raise NotADirectoryError
imageFile = os.path.join(OutputDir, Config.get("OutputFiles", "OutputBase"))
imageFile = os.path.normpath(imageFile)
imageExt = ".png"

# Display characteristics
# Areas in pixels
DPI = Config.getint("PageSize", "DPI")
LeftBuffer = int(Config.getfloat("PlotArea", "LeftBuffer")*DPI)
RightBuffer = int(Config.getfloat("PlotArea", "RightBuffer")*DPI)
TopBuffer = int(Config.getfloat("PlotArea", "TopBuffer")*DPI)
BottomBuffer = int(Config.getfloat("PlotArea", "BottomBuffer")*DPI)

VertPixels = (int(Config.getfloat("PageSize", "Height")*DPI)
              - TopBuffer - BottomBuffer)
HorPixels = (int(Config.getfloat("PageSize", "Width")*DPI)
             - LeftBuffer - RightBuffer)

# Page Number Box
PageNumberBoxHeight = int(Config.getfloat("PageNumber", "Height")*DPI)
PageNumberBoxWidth = int(Config.getfloat("PageNumber", "Width")*DPI)
PageNumberBoxBottom = int(Config.getfloat("PageNumber", "Bottom")*DPI)
PageNumberBoxRight = int(Config.getfloat("PageNumber", "Right")*DPI)
PageNumberBoxColor = Config.get("PageNumber","Color")
PageNumberOffset = int(Config.getfloat("PageNumber", "NumberBaseline")*DPI)
PageSkips = set()
for Page in Config.get("PageNumber", "PageSkips").split(','):
    if len(Page) > 0:
        PageSkips.add(int(Page))

# Rendering Variables
autoMinElev = Config.getboolean("ElevationIntervals", "autoMin")
autoMaxElev = Config.getboolean("ElevationIntervals", "autoMax")
minElev = int(Config.get("ElevationIntervals", "Minimum"))
maxElev = int(Config.get("ElevationIntervals", "Maximum"))
ElevationInterval = int(Config.get("ElevationIntervals", "Interval"))
autoElevInt = Config.getboolean("ElevationIntervals", "autoInt")
autoAdjustPagination = Config.getboolean("Profile", "autoFitMiles")
Pagination = Config.getfloat("Profile", "MilesPerPage")
oddSwap = Config.getboolean("PageLayout", "MirrorPages")
usesatDEM = Config.getboolean("Profile", "UseSatDEM")

# Lines
BackgroundColor = Config.get("PlotArea", "Color")
ElevationColor = Config.get("Profile", "Color")
ElevationWeight = int(Config.getfloat("Profile", "Weight")*DPI)
ElevationIntervalColor = Config.get("ElevationIntervals", "Color")
ElevationIntervalWeight = int(Config.getfloat("ElevationIntervals",
                                              "Weight")*DPI)
skipzero = not Config.getboolean("ElevationIntervals", "LabelZero")
LeftBorderColor = Config.get("SideLines", "LeftColor")
LeftBorderWeight = int(Config.getfloat("SideLines", "LeftWeight")*DPI)
RightBorderColor = Config.get("SideLines", "RightColor")
RightBorderWeight = int(Config.getfloat("SideLines", "RightWeight")*DPI)
TopLeftLine= int(Config.getfloat("SideLines", "LeftTop")*DPI)
BottomLeftLine= int(Config.getfloat("SideLines", "LeftBottom")*DPI)
LeftLine = int(Config.getfloat("SideLines", "LeftHoriz")*DPI)
RightLine = int(Config.getfloat("SideLines", "RightHoriz")*DPI)

# Fonts
WayPointFont = ImageFont.truetype(Config.get("Fonts", "WaypointFont"),
                                  int(Config.getfloat("Fonts", "WaypointHeight")*DPI))
WayPointFontBold = ImageFont.truetype(Config.get("Fonts", "WaypointFontBold"),
                                      int(Config.getfloat("Fonts", "WaypointHeight")*DPI))
PageNumberFont = ImageFont.truetype(Config.get("Fonts", "PageNumberFont"),
                                    int(Config.getfloat("Fonts", "PageNumberHeight")*DPI))
ServiceGlyphs = ImageFont.truetype(Config.get("Fonts", "WaypointGlyphs"),
                                   int(Config.getfloat("Fonts", "WaypointHeight")*DPI))
ElevationAxisFont = ImageFont.truetype(Config.get("Fonts", "ElevationAxisFont"),
                                       int(Config.getfloat("Fonts", "ElevationAxisHeight")*DPI))

ElevationAxisBuffer = int(Config.getfloat("ElevationIntervals", "Buffer")*DPI)
ElevationAxisCenteringScalar = Config.getfloat("ElevationIntervals", "LabelOffsetScalar")

# Waypoint Display
dteLabel = Config.get("Profile", "OppDirectionLabel")
dtsLabel = Config.get("Profile", "DirectionLabel")
elevLabel = Config.get("Profile", "ElevationLabel")
YAxisLabelEdge = int(Config.getfloat("Profile", "LabelBottom")*DPI)
dteEdge = int(Config.getfloat("Profile", "DistanceAheadEdge")*DPI)
dtsEdge = int(Config.getfloat("Profile", "DistanceBehindEdge")*DPI)
DescriptionEdge = int(Config.getfloat("Profile", "DescriptionEdge")*DPI)
DescriptionMaxLength = int(Config.getfloat("Profile",
                                           "DescriptionMaxLength")*DPI)
ElevationEdge = int(Config.getfloat("Profile", "ElevationEdge")*DPI)
ServicesEdge = int(Config.getfloat("Profile", "ServicesEdge")*DPI)
MarkerLength = int(Config.getfloat("Profile", "MarkerLength")*DPI)
MarkerWeight = int(Config.getfloat("Profile", "MarkerWeight")*DPI)
TriangleMarkerSize = int(Config.getfloat("Profile", "TriangleSize")*DPI)
PixelsPerDotLine = int(Config.getfloat("Profile", "FillSpacing")*DPI)
DotLineSymbol = Config.get("Profile", "FillSymbol")

# Constants
FEETPERMETER = 3.28084
FEETPERDEGREE = 363998
MaxWaypointDistance = (Config.getfloat("Profile", "WaypointDistance")
                       / FEETPERDEGREE) ** 2

print("Parsing Waypoint file")
waypoints_file = open(WaypointFile, 'r')
waypointdoc = gpxpy.parse(waypoints_file)
waypoints_file.close()
print("Done parsing waypoints")

print("Parsing Track file")
gps_file = open(TrackFile, 'r')
gpsdoc = gpxpy.parse(gps_file)
gps_file.close()
print("Done parsing track")
if TrackNumber > len(gpsdoc.tracks) - 1:
    print("Error, Track number not found in track file: ", TrackNumber)
    raise IndexError

PreviousPoint = (0.0, 0.0)
PreviousElevation = 0.0
FirstPass = True
TotalDistance = 0.0
TotalElevationGain = 0.0
elevations = []
foundtenth = 0.0
MinElevation = 0
MaxElevation = 0

# list of list [latitude, longitude, comment, serviceglyphs, trianglemaker, offset]
Waypoints = []

for waypoint in waypointdoc.waypoints:
    Waypoints.append([waypoint.latitude,waypoint.longitude, waypoint.comment, waypoint.description, False, int(0)])

POIs = []
print()
print("Processing " + str(len(Waypoints)) + " waypoints")
foundtenth= 5.0
prevElevation = 0


if usesatDEM:
    elevation_data = srtm.get_data()
    elevation_data.add_elevations(gpsdoc)
else:
    for point in gpsdoc.tracks[TrackNumber].segments[0].points:
        if point.elevation is None:
            point.elevation = prevElevation
        else:
            prevElevation = point.elevation

mu = 0
for point in gpsdoc.tracks[TrackNumber].segments[0].points:
    if not FirstPass:
        CurrentPoint = (float(point.latitude), float(point.longitude))
        CurrentElevation = float(point.elevation)
        segmentlength = vincenty(PreviousPoint, CurrentPoint).miles
        TotalDistance += segmentlength
        if TotalDistance > foundtenth:
            foundtenth += 5
            print("Processed " + str("%.2f" % TotalDistance)+ " miles with "
                  + str(len(Waypoints)) + " waypoints left")
        if  segmentlength > 0.0378788:
            print("Warning: Gap detected at " + str("%.2f" % TotalDistance)
                  + " of " + str(int(5280 * segmentlength)) + " feet")
        if CurrentElevation > PreviousElevation:
            TotalElevationGain += CurrentElevation - PreviousElevation
        MaxElevation = max(MaxElevation, CurrentElevation)
        MinElevation = min(MinElevation, CurrentElevation)
        PreviousPoint = CurrentPoint
        PreviousElevation = CurrentElevation
        elevations.append((TotalDistance, CurrentElevation*FEETPERMETER,
                           CurrentPoint))

        # Match Waypoints, poor implementation, first point < MaxWaypointDistance
        skipper = int(0)
        for waypoint in range(len(Waypoints)):
            if (fastdist(point.latitude, point.longitude,
                        Waypoints[waypoint+skipper][0],
                        Waypoints[waypoint+skipper][1], mu)
                < MaxWaypointDistance): 
                if Waypoints[waypoint+skipper][2] != "":
                    POIs.append(POI(TotalDistance, CurrentElevation*FEETPERMETER,Waypoints[waypoint+skipper][2],WayPointFont, services=Waypoints[waypoint+skipper][3]))
                else:
                    print("Empty Waypoint:")
                    print(Waypoint[waypoint+skipper])
                del Waypoints[waypoint+skipper]
                skipper -= 1
        
    else:
        PreviousPoint = (float(point.latitude), float(point.longitude))
        PreviousElevation = float(point.elevation)
        MinElevation = MaxElevation = PreviousElevation
        FirstPass = False
        mu = math.cos(math.radians(point.latitude))

POIs.sort()

print()
print("Minimum Elevation: " + str(MinElevation*FEETPERMETER))
print("Maximum Elevation: " + str(MaxElevation*FEETPERMETER))



if autoMaxElev:
    print("Adjusting maximum elevation to " + str(MaxElevation*FEETPERMETER))
    maxElev = int(MaxElevation*FEETPERMETER)
    
if autoMinElev:
    print("Adjusting minimum elevation to " + str(MinElevation*FEETPERMETER))
    minElev = int(MinElevation*FEETPERMETER)
    
if autoMinElev or autoMaxElev:
    print("Adjusting elevation interval to " + str(int((maxElev-minElev)/5)))
    ElevationInterval = int((maxElev-minElev)/5)

if autoAdjustPagination:
    Pagination = TotalDistance/max(1,round(TotalDistance/Pagination))
    print("Distance per page (miles): " + str(Pagination))

if len(Waypoints) > 0:
    print("Warning: Unmatched waypoints-")
    print(Waypoints)

NumPages = math.ceil(TotalDistance/Pagination)
print("Generating " + str(NumPages) + " pages")

PageNumber = list(set(range(1, NumPages + 1 + len(PageSkips))).difference(PageSkips))


for Page in range(math.ceil(TotalDistance/Pagination)):
    print("Rendering Page: ", Page + 1, sep='')
    pagewidth = LeftBuffer + RightBuffer + HorPixels
    pageheight = BottomBuffer + TopBuffer + VertPixels
    elevplot = Image.new('RGB', (pagewidth, pageheight), BackgroundColor)
    txtplot = Image.new('RGBA', (pageheight, pagewidth), (0,0,0,0))
    draw = ImageDraw.Draw(elevplot)
    drawtxt = ImageDraw.Draw(txtplot)

    if oddSwap and PageNumber[Page] %2 != 0:
        # Page Number Box
        boxside = pagewidth - PageNumberBoxRight
        boxbottom = pageheight - PageNumberBoxBottom
        draw.rectangle([boxside, boxbottom - PageNumberBoxHeight,
                       boxside + PageNumberBoxWidth, boxbottom],
                       PageNumberBoxColor)

        # PageNumber[Page]   YAxisLabelEdge-ElevationAxisFont.font.ascent
        txtWidth, txtHeight = PageNumberFont.getsize(str(PageNumber[Page]))
        draw.text((int(boxside + PageNumberBoxWidth/2.0 - txtWidth/2), boxbottom - PageNumberBoxHeight + PageNumberOffset - PageNumberFont.font.ascent), str(PageNumber[Page]),'white', PageNumberFont)

        # LeftBorder
        draw.line([pagewidth - LeftLine, TopLeftLine, elevplot.size[0] - LeftLine, elevplot.size[1] - BottomLeftLine],
                  LeftBorderColor, LeftBorderWeight)

        # RightBorder
        elevdelta = float(maxElev - minElev)
        plotbottom = TopBuffer + VertPixels
        draw.line([RightLine, plotbottom / elevdelta * (elevdelta%ElevationInterval), RightLine, plotbottom], RightBorderColor, RightBorderWeight)

        # Elevation intervals
        PixelPerElev = VertPixels / float(maxElev - minElev)
        for elevation in range(minElev, maxElev, ElevationInterval):
            ElevPixel = plotbottom - int(PixelPerElev*elevation)
            draw.line([RightLine, ElevPixel, pagewidth - LeftBuffer, ElevPixel],
                      ElevationIntervalColor, ElevationIntervalWeight)
            txtWidth, txtHeight = ElevationAxisFont.getsize(str(int(elevation)))
            if not skipzero or abs(elevation) > 0.1: #Add elevation axis labels if non-zero or zero label flag set
                draw.text((pagewidth - LeftLine + ElevationAxisBuffer, int(ElevPixel-txtHeight*ElevationAxisCenteringScalar)), str(int(elevation)),'black',ElevationAxisFont)

    else:
        # Page Number Box
        draw.rectangle([PageNumberBoxRight-PageNumberBoxWidth, elevplot.size[1]-PageNumberBoxBottom-PageNumberBoxHeight,\
                        PageNumberBoxRight, elevplot.size[1]-PageNumberBoxBottom],PageNumberBoxColor)

        # PageNumber[Page]   YAxisLabelEdge-ElevationAxisFont.font.ascent
        txtWidth, txtHeight = PageNumberFont.getsize(str(PageNumber[Page]))
        draw.text((int(PageNumberBoxRight-PageNumberBoxWidth/2.0-txtWidth/2),elevplot.size[1]-PageNumberBoxBottom-PageNumberBoxHeight + PageNumberOffset - PageNumberFont.font.ascent),str(PageNumber[Page]),'white', PageNumberFont)

        # LeftBorder
        draw.line([LeftLine, TopLeftLine, LeftLine, elevplot.size[0] - BottomLeftLine], LeftBorderColor, LeftBorderWeight)

        # RightBorder
        draw.line([elevplot.size[0]-RightLine, TopBuffer+VertPixels / float(maxElev - minElev)*((maxElev-minElev)%ElevationInterval), elevplot.size[0]-RightLine, TopBuffer+VertPixels], RightBorderColor, RightBorderWeight)

        # Elevation intervals
        PixelPerElev = VertPixels / float(maxElev - minElev)
        for elevation in range(minElev, maxElev, ElevationInterval):
            ElevPixel = TopBuffer+VertPixels-int(PixelPerElev*elevation)
            draw.line([LeftBuffer, ElevPixel, elevplot.size[0] - RightLine, ElevPixel], ElevationIntervalColor, ElevationIntervalWeight)
            txtWidth, txtHeight = ElevationAxisFont.getsize(str(int(elevation)))
            if not skipzero or abs(elevation) > 0.1: # Add elevation axis labels if non-zero or zero label flag set
                draw.text((LeftLine-txtWidth-ElevationAxisBuffer, int(ElevPixel-txtHeight*ElevationAxisCenteringScalar)), str(int(elevation)),'black',ElevationAxisFont)
            
    PreviousPoint = (0,0)
    elevPlot = []
    for trackpoint in elevations:
        if int(trackpoint[0]/Pagination) == Page:
            if oddSwap and PageNumber[Page] %2 != 0:
                CurrentPoint = (RightLine+int(((trackpoint[0] - Page*Pagination)/Pagination)*HorPixels), TopBuffer+VertPixels-int(PixelPerElev*trackpoint[1]))
            else:
                CurrentPoint = (LeftBuffer+int(((trackpoint[0] - Page*Pagination)/Pagination)*HorPixels), TopBuffer+VertPixels-int(PixelPerElev*trackpoint[1]))                
            elevPlot.append(CurrentPoint)
            PreviousPoint = CurrentPoint

    draw.line(elevPlot, ElevationColor, ElevationWeight)
    for joint in elevPlot[1:-1]:
        draw.ellipse((joint[0]-ElevationWeight/2, joint[1]-ElevationWeight/2, joint[0]+ElevationWeight/2, joint[1]+ElevationWeight/2), ElevationColor)

    # Potential rendering error if the font with the highest ascender is different than the one with the lowest descender and text of one section overlaps with another 
    LineSpace = max(WayPointFont.font.height, WayPointFontBold.font.height, ServiceGlyphs.font.height)

    # Y-Axis Labels
    if oddSwap and PageNumber[Page] %2 != 0:
        txtWidth, txtHeight = ElevationAxisFont.getsize(dtsLabel)
        drawtxt.text((dtsEdge-txtWidth, txtplot.size[1] - YAxisLabelEdge), dtsLabel,'black', ElevationAxisFont)
        txtWidth, txtHeight = ElevationAxisFont.getsize(dteLabel)
        drawtxt.text((dteEdge-txtWidth,txtplot.size[1] - YAxisLabelEdge), dteLabel,'black', ElevationAxisFont)
        txtWidth, txtHeight = ElevationAxisFont.getsize(elevLabel)
        drawtxt.text((txtplot.size[0]-ElevationEdge-txtWidth,txtplot.size[1] - YAxisLabelEdge), elevLabel, 'black', ElevationAxisFont)

    else:
        txtWidth, txtHeight = ElevationAxisFont.getsize(dtsLabel)
        drawtxt.text((dtsEdge-txtWidth,YAxisLabelEdge-ElevationAxisFont.font.ascent), dtsLabel, 'black', ElevationAxisFont)
        txtWidth, txtHeight = ElevationAxisFont.getsize(dteLabel)
        drawtxt.text((dteEdge-txtWidth,YAxisLabelEdge-ElevationAxisFont.font.ascent), dteLabel, 'black', ElevationAxisFont)
        txtWidth, txtHeight = ElevationAxisFont.getsize(elevLabel)
        drawtxt.text((txtplot.size[0]-ElevationEdge-txtWidth,YAxisLabelEdge-ElevationAxisFont.font.ascent), elevLabel, 'black', ElevationAxisFont)

    # Calculate Offsets
    # Dumb implementation right now, no end bounds
    # Linespace?
    FirstPOI = True
    EndBoundPass = False
    for index in range(len(POIs)-1):
        #check if first entry
        if FirstPOI and int(POIs[index].distance/Pagination) == Page:
            FirstPOI = False
            if int(((POIs[index].distance - Page*Pagination)/Pagination)*HorPixels) - max(WayPointFont.font.ascent,WayPointFontBold.font.ascent,ServiceGlyphs.font.ascent) < 0:
                POIs[index].offset = max(WayPointFont.font.ascent,WayPointFontBold.font.ascent,ServiceGlyphs.font.ascent) - int(((POIs[index].distance - Page*Pagination)/Pagination)*HorPixels)
        if int(POIs[index+1].distance/Pagination) == Page and \
           int((POIs[index].distance/Pagination)*HorPixels) + POIs[index].offset + POIs[index].getheight([DescriptionMaxLength]) > int((POIs[index+1].distance/Pagination)*HorPixels):
            POIs[index+1].offset =  int((POIs[index].distance/Pagination)*HorPixels) + POIs[index].offset + POIs[index].getheight([DescriptionMaxLength]) - int((POIs[index+1].distance/Pagination)*HorPixels)
       # check bottom (only on last one needed)
    
    # Render
    for waypoint in POIs:
        if int(waypoint.distance/Pagination) == Page:
            lineX = LeftBuffer + int(((waypoint.distance - Page*Pagination)/Pagination)*HorPixels)
            draw.line([lineX, TopBuffer+VertPixels-int(PixelPerElev*waypoint.elevation)+ MarkerLength,\
                       lineX, TopBuffer+VertPixels-int(PixelPerElev*waypoint.elevation)],\
                      ElevationColor, MarkerWeight)
            if waypoint.marker is not None: # Special Triangle Marker
                draw.polygon([lineX, TopBuffer+VertPixels-int(PixelPerElev * waypoint.elevation) + MarkerLength - MarkerWeight, lineX - int(TriangleMarkerSize/2), TopBuffer+VertPixels-int(PixelPerElev*waypoint.elevation)+TriangleMarkerSize + MarkerLength - MarkerWeight, lineX+int(TriangleMarkerSize/2), TopBuffer+VertPixels-int(PixelPerElev*waypoint.elevation)+TriangleMarkerSize + MarkerLength - MarkerWeight], ElevationColor)

            # Distance to end (SOBO on a NOBO guide)
            DTE = "%.1f" % (TotalDistance - waypoint.distance)
            txtWidth, txtHeight = WayPointFont.getsize(DTE)
            drawtxt.text((dteEdge-txtWidth, lineX + waypoint.offset - WayPointFont.font.ascent), DTE, 'black', WayPointFont)

            # Distance to start (NOBO on a NOBO guide)
            DTS = "%.1f" % waypoint.distance
            txtWidth, txtHeight = WayPointFontBold.getsize(DTS)
            drawtxt.text((dtsEdge-txtWidth, lineX + waypoint.offset - WayPointFontBold.font.ascent), DTS, 'black', WayPointFontBold)

            # Description of waypoint
            VertAdv = 156  # fix this
            Advance = 0
            lengths = []
            if waypoint.services is not None:
                lengths.append(min(txtplot.width - ServicesEdge - ServiceGlyphs.getsize(waypoint.services)[0] - DescriptionEdge, DescriptionMaxLength))
            lengths.append(DescriptionMaxLength)
            for line in waypoint.wordwrap(lengths):
                txtWidth, txtHeight = WayPointFont.getsize(line)
                if Advance == 0:
                    EndDesc = DescriptionEdge + txtWidth
                drawtxt.text((DescriptionEdge, lineX + waypoint.offset - WayPointFont.font.ascent + Advance), line, 'black', WayPointFont)
                Advance += VertAdv

            # Elevation
            Elevation = "%.0f" % round(waypoint.elevation)
            txtWidth, txtHeight = WayPointFont.getsize(Elevation)
            drawtxt.text((txtplot.width - ElevationEdge - txtWidth, lineX + waypoint.offset - WayPointFont.font.ascent), Elevation, 'black', WayPointFont)

            # Services
            if waypoint.services is not None:
                txtWidth, txtHeight = ServiceGlyphs.getsize(waypoint.services)
                BeginService = txtplot.width - ServicesEdge - txtWidth
                drawtxt.text((BeginService, lineX + waypoint.offset - ServiceGlyphs.font.ascent), waypoint.services, 'black', ServiceGlyphs)
            else:
                BeginService = txtplot.width - ServicesEdge

            # Readability dots
            txtWidth, txtHeight = WayPointFont.getsize(DotLineSymbol)
            if not EndDesc % PixelsPerDotLine == 0:
                EndDesc += PixelsPerDotLine - EndDesc % PixelsPerDotLine
            assert (EndDesc % PixelsPerDotLine) == 0
            for dot in range(0, BeginService - EndDesc - txtWidth, PixelsPerDotLine):
                    drawtxt.text((EndDesc + dot, lineX + waypoint.offset - WayPointFont.font.ascent), waypoint.fill, 'black', WayPointFont)

    # Rotate and merge text
    txtplot = txtplot.rotate(90, "1", True)
    elevplot.paste(txtplot, None, txtplot)

    del draw
    del drawtxt
    elevplot = elevplot.convert('P')
    elevplot.save(imageFile + str(PageNumber[Page]).zfill(3) + imageExt,
                  dpi=(DPI, DPI))
