#imports
from geopy.distance import vincenty # integrate into gpxpy?
from PIL import Image, ImageDraw, ImageFont
import math
import gpxpy
import configparser


ConfigFileName = "c:/Users/GuestUser/Documents/Nick/ProfileBuilder/TestData/NET.ini"
Config = configparser.ConfigParser()
Config.read(ConfigFileName)

#GPX File
TrackFile = Config.get("InputFiles","TrackFile")
WaypointFile = Config.get("InputFiles","WaypointFile")
if len(WaypointFile) == 0:
    WaypointFile = Trackfile
TrackNumber = int(Config.get("InputFiles","TrackNumber"))

#PlotSave
imageFile = "c:/Users/GuestUser/Documents/Nick/ProfileBuilder/Guidebook/NET Main"
imageExt = ".png"



#Display characteristics


#Areas in pixels
DPI = int(1200)
LeftBuffer = int(564)    #0.435"
RightBuffer = int(522)   #0.435"
TopBuffer = int(540)     #0.45"
BottomBuffer = int(1560) #1.3"
TopWhite= int(240)       #0.2"
BottomWhite= int(360)    #0.3"
LeftLine = int(522)
RightLine = int(522)

VertPixels = int(4140)   #3.45"
HorPixels = int(8514)    #7.095"

#Page Number Box
PageNumberBoxHeight = int(582)  #0.485
PageNumberBoxWidth = int(324)   #0.270
PageNumberBoxBottom = int(1518) #1.265
PageNumberBoxRight = int(522)   #0.435
PageNumberBoxColor = (128, 128, 128)
PageNumberOffset = int(204)
PageSkips = [] #list(range(1,22))


#Rendering Variables
autoElev = False
minElev = int(0)
maxElev = int(1700)
lowElevLine = 0.0
ElevationInterval = int(250)
autoAdjustPagination = True
Pagination = 10 #Miles per page
oddSwap = True

#Lines
BackgroundColor = (255, 255, 255)
ElevationColor = (152, 152, 152)
ElevationWeight = int(40)
ElevationIntervalColor = (128, 128, 128)
ElevationIntervalWeight = int(8)
skipzero = True
LeftBorderColor = (0, 0, 0)
LeftBorderWeight = int(8)
RightBorderColor = (128, 128, 128)
RightBorderWeight = int(8)


#Fonts

print(Config.get("Fonts","WaypointFont"))

WayPointFont = ImageFont.truetype(Config.get("Fonts","WaypointFont"), int(float(Config.get("Fonts","WaypointHeight"))*DPI))
WayPointFontBold = ImageFont.truetype(Config.get("Fonts","WaypointFontBold"), int(float(Config.get("Fonts","WaypointHeight"))*DPI))
PageNumberFont = ImageFont.truetype(Config.get("Fonts","PageNumberFont"), int(float(Config.get("Fonts","PageNumberHeight"))*DPI))
ServiceGlyphs = ImageFont.truetype(Config.get("Fonts","WaypointGlyphs"), int(float(Config.get("Fonts","WaypointHeight"))*DPI))
ElevationAxisFont = ImageFont.truetype(Config.get("Fonts","ElevationAxisFont"), int(float(Config.get("Fonts","ElevationAxisHeight"))*DPI))

ElevationAxisBuffer = int(48)
ElevationAxisCenteringScalar = (1638-1384)/(2*1638.0)+0.5 #Half height of font measured from top (as fraction of whole height)



#Waypoint Display
dteLabel = "SoBo"
dtsLabel = "NoBo"
elevLabel = "Elev"
YAxisLabelEdge = int(450)
dteEdge = int(624)  #0.52"
dtsEdge = int(1098) #0.915"
DescriptionEdge = int(1182)
ElevationEdge = int(240)
ServicesEdge = int(600)
MarkerLength = int(102) #0.085"
MarkerWeight = int(20)
TriangleMarkerSize = int(120) #0.1"
PixelsPerDotLine = int(96)
DotLineSymbol = '.'

#Constants
MeterToFoot = 3.28084
MaxWaypointDistance = 0.0094697  #50 ft (in miles)


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


PreviousPoint = (0.0, 0.0)
PreviousElevation = 0.0
FirstPass = True
TotalDistance = 0.0
TotalElevationGain = 0.0
elevations = []
foundtenth = 0.0
MinElevation = 0
MaxElevation = 0


Waypoints = []

for waypoint in waypointdoc.waypoints:
    Waypoints.append([waypoint.latitude,waypoint.longitude,waypoint.comment, "", False, int(0)])



POIs = []
print()
print("Processing " + str(len(Waypoints)) + " waypoints")
foundtenth= 5.0
prevElevation = 0


# Implement better by getting SRTM data and smoothly integrating 
for point in gpsdoc.tracks[TrackNumber].segments[0].points:
    if point.elevation is None:
        point.elevation = prevElevation
    else:
        prevElevation = point.elevation


for point in gpsdoc.tracks[TrackNumber].segments[0].points:
    if not FirstPass:
        CurrentPoint = (float(point.latitude), float(point.longitude))
        CurrentElevation = float(point.elevation)
        TotalDistance += vincenty(PreviousPoint, CurrentPoint).miles
        if TotalDistance > foundtenth:
            foundtenth += 5
            print("Processed " + str("%.2f" % TotalDistance)+ " miles with " + str(len(Waypoints)) + " waypoints left")
        if  vincenty(PreviousPoint, CurrentPoint).miles > 0.0378788:
            print("Warning: Gap detected at " + str("%.2f" % TotalDistance) + " of " + str(int(5280 * vincenty(PreviousPoint, CurrentPoint).miles)) + " feet")
        if CurrentElevation > PreviousElevation:
            TotalElevationGain += CurrentElevation - PreviousElevation
        MaxElevation = max(MaxElevation, CurrentElevation)
        MinElevation = min(MinElevation, CurrentElevation)
        PreviousPoint = CurrentPoint
        PreviousElevation = CurrentElevation
        elevations.append((TotalDistance, CurrentElevation*MeterToFoot, CurrentPoint))

        #Match Waypoints, poor implementation, first point < MaxWaypointDistance
        skipper = int(0)
        for waypoint in range(len(Waypoints)):
            if  vincenty(CurrentPoint, (Waypoints[waypoint+skipper][0],Waypoints[waypoint+skipper][1])).miles < MaxWaypointDistance:
                if Waypoints[waypoint+skipper][2] != "":
                    POIs.append([TotalDistance,CurrentElevation*MeterToFoot,Waypoints[waypoint+skipper][2],Waypoints[waypoint+skipper][3],Waypoints[waypoint+skipper][4],Waypoints[waypoint+skipper][5]])
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





POIs.sort()

print()
print("Minimum Elevation: " + str(MinElevation*MeterToFoot))
print("Maximum Elevation: " + str(MaxElevation*MeterToFoot))
if autoElev:
    ElevationInterval = int((MaxElevation-MinElevation)*MeterToFoot/5)
    minElev = int(MinElevation*MeterToFoot) - int(MinElevation*MeterToFoot)%ElevationInterval
    maxElev = int(MaxElevation*MeterToFoot)

if autoAdjustPagination:
    Pagination = TotalDistance/max(1,round(TotalDistance/Pagination))
    print("Distance per page (miles): " + str(Pagination))

if len(Waypoints) > 0:
    print("Warning: Unmatched waypoints-")
    print(Waypoints)

print("probably a bug here")
print("Generating " + str(math.ceil(TotalDistance/Pagination)) + " pages")

PageNumber = list(set(range(1,math.ceil(TotalDistance/Pagination)+1+len(PageSkips))).difference(PageSkips))


for Page in range(math.ceil(TotalDistance/Pagination)):
    print("Rendering Page: ", Page + 1, sep='')
    elevplot = Image.new('RGB', (LeftBuffer + RightBuffer + HorPixels, BottomBuffer + TopBuffer + VertPixels), BackgroundColor)
    txtplot = Image.new('RGBA', (BottomBuffer + TopBuffer + VertPixels, LeftBuffer + RightBuffer + HorPixels),BackgroundColor + (int(0),))
    draw = ImageDraw.Draw(elevplot)
    drawtxt = ImageDraw.Draw(txtplot)

    if oddSwap and PageNumber[Page] %2 != 0:
        #Page Number Box
        draw.rectangle([elevplot.size[0] - PageNumberBoxRight, elevplot.size[1] - PageNumberBoxBottom - PageNumberBoxHeight,\
                        elevplot.size[0] - PageNumberBoxRight + PageNumberBoxWidth, elevplot.size[1] - PageNumberBoxBottom], PageNumberBoxColor)

        #PageNumber[Page]   YAxisLabelEdge-ElevationAxisFont.font.ascent
        txtWidth, txtHeight = PageNumberFont.getsize(str(PageNumber[Page]))
        draw.text((int(elevplot.size[0] - PageNumberBoxRight + PageNumberBoxWidth/2.0 - txtWidth/2), \
                   elevplot.size[1] - PageNumberBoxBottom - PageNumberBoxHeight + PageNumberOffset - PageNumberFont.font.ascent),\
                  str(PageNumber[Page]),'white', PageNumberFont)

        #LeftBorder
        draw.line([elevplot.size[0] - LeftLine, TopWhite, elevplot.size[0] - LeftLine, elevplot.size[1] - BottomWhite], LeftBorderColor, LeftBorderWeight)

        #RightBorder
        draw.line([RightLine, TopBuffer+VertPixels / float(maxElev - minElev)*((maxElev-minElev)%ElevationInterval), RightLine, TopBuffer+VertPixels], RightBorderColor, RightBorderWeight)

        #Elevation intervals
        PixelPerElev = VertPixels / float(maxElev - minElev)
        for elevation in range(minElev, maxElev, ElevationInterval):
            ElevPixel = TopBuffer+VertPixels-int(PixelPerElev*elevation)
            #print([LeftLine, ElevPixel, RightLine, ElevPixel])
            draw.line([RightLine, ElevPixel, elevplot.size[0] - LeftBuffer, ElevPixel], ElevationIntervalColor, ElevationIntervalWeight)
            txtWidth, txtHeight = ElevationAxisFont.getsize(str(int(elevation)))
            if not skipzero or abs(elevation) > 0.1: #Add elevation axis labels if non-zero or zero label flag set
                draw.text((elevplot.size[0] - LeftLine + ElevationAxisBuffer, int(ElevPixel-txtHeight*ElevationAxisCenteringScalar)), str(int(elevation)),'black',ElevationAxisFont)


    else:
        #Page Number Box
        draw.rectangle([PageNumberBoxRight-PageNumberBoxWidth, elevplot.size[1]-PageNumberBoxBottom-PageNumberBoxHeight,\
                        PageNumberBoxRight, elevplot.size[1]-PageNumberBoxBottom],PageNumberBoxColor)

        #PageNumber[Page]   YAxisLabelEdge-ElevationAxisFont.font.ascent
        txtWidth, txtHeight = PageNumberFont.getsize(str(PageNumber[Page]))
        draw.text((int(PageNumberBoxRight-PageNumberBoxWidth/2.0-txtWidth/2),elevplot.size[1]-PageNumberBoxBottom-PageNumberBoxHeight + PageNumberOffset - PageNumberFont.font.ascent),str(PageNumber[Page]),'white', PageNumberFont)

        #LeftBorder
        draw.line([LeftLine, TopWhite, LeftLine, elevplot.size[0] - BottomWhite], LeftBorderColor, LeftBorderWeight)

        #RightBorder
        draw.line([LeftBuffer+HorPixels+RightBuffer-RightLine, TopBuffer+VertPixels / float(maxElev - minElev)*((maxElev-minElev)%ElevationInterval), LeftBuffer+HorPixels+RightBuffer-RightLine, TopBuffer+VertPixels], RightBorderColor, RightBorderWeight)


        #Elevation intervals
        PixelPerElev = VertPixels / float(maxElev - minElev)
        for elevation in range(minElev, maxElev, ElevationInterval):
            ElevPixel = TopBuffer+VertPixels-int(PixelPerElev*elevation)
            draw.line([LeftBuffer, ElevPixel, elevplot.size[0] - RightLine, ElevPixel], ElevationIntervalColor, ElevationIntervalWeight)
            txtWidth, txtHeight = ElevationAxisFont.getsize(str(int(elevation)))
            if not skipzero or abs(elevation) > 0.1: #Add elevation axis labels if non-zero or zero label flag set
                draw.text((LeftLine-txtWidth-ElevationAxisBuffer, int(ElevPixel-txtHeight*ElevationAxisCenteringScalar)), str(int(elevation)),'black',ElevationAxisFont)
            
    PreviousPoint = (0,0)
    elevPlot = []
    for trackpoint in elevations:
        if int(trackpoint[0]/Pagination) == Page:
            if oddSwap and PageNumber[Page] %2 != 0:
                CurrentPoint = (RightLine+int(((trackpoint[0] - Page*Pagination)/Pagination)*HorPixels),TopBuffer+VertPixels-int(PixelPerElev*trackpoint[1]))
            else:
                CurrentPoint = (LeftBuffer+int(((trackpoint[0] - Page*Pagination)/Pagination)*HorPixels),TopBuffer+VertPixels-int(PixelPerElev*trackpoint[1]))                
            elevPlot.append(CurrentPoint)
            PreviousPoint = CurrentPoint

    draw.line(elevPlot,ElevationColor, ElevationWeight)
    
    #for joint in elevPlot[1:-1]:
        #draw.ellipse([joint[0]-ElevationWeight/2,joint[1]-ElevationWeight/2,joint[0]+ElevationWeight/2,joint[1]+ElevationWeight/2],ElevationColor)
        

    # Waypoint plotter
    # (Dist from 0, elevation, desc, services, special marker, renderoffset)


    #Potential rendering error if the font with the highest ascender is different than the one with the lowest descender and text of one section overlaps with another 
    LineSpace = max(WayPointFont.font.height, WayPointFontBold.font.height, ServiceGlyphs.font.height)

    #Y-Axis Labels
    if oddSwap and PageNumber[Page] %2 != 0:
        txtWidth, txtHeight = ElevationAxisFont.getsize(dtsLabel)
        drawtxt.text((dtsEdge-txtWidth, txtplot.size[1] - YAxisLabelEdge),dtsLabel,'black', ElevationAxisFont)
        txtWidth, txtHeight = ElevationAxisFont.getsize(dteLabel)
        drawtxt.text((dteEdge-txtWidth,txtplot.size[1] - YAxisLabelEdge),dteLabel,'black', ElevationAxisFont)
        txtWidth, txtHeight = ElevationAxisFont.getsize(elevLabel)
        drawtxt.text((txtplot.size[0]-ElevationEdge-txtWidth,txtplot.size[1] - YAxisLabelEdge),elevLabel,'black', ElevationAxisFont)

    else:
        txtWidth, txtHeight = ElevationAxisFont.getsize(dtsLabel)
        drawtxt.text((dtsEdge-txtWidth,YAxisLabelEdge-ElevationAxisFont.font.ascent),dtsLabel,'black', ElevationAxisFont)
        txtWidth, txtHeight = ElevationAxisFont.getsize(dteLabel)
        drawtxt.text((dteEdge-txtWidth,YAxisLabelEdge-ElevationAxisFont.font.ascent),dteLabel,'black', ElevationAxisFont)
        txtWidth, txtHeight = ElevationAxisFont.getsize(elevLabel)
        drawtxt.text((txtplot.size[0]-ElevationEdge-txtWidth,YAxisLabelEdge-ElevationAxisFont.font.ascent),elevLabel,'black', ElevationAxisFont)




    #Calculate Offsets
    #Dumb implementation right now, no end bounds, no recursive checking
    for index in range(len(POIs)-1):
        if LeftBuffer + int((POIs[index][0]/Pagination)*HorPixels) + POIs[index][5] + LineSpace > LeftBuffer + int((POIs[index+1][0]/Pagination)*HorPixels):
            POIs[index+1][5] =  int((POIs[index][0]/Pagination)*HorPixels) + POIs[index][5] + LineSpace - int((POIs[index+1][0]/Pagination)*HorPixels)
       


    #Render
    for waypoint in POIs:
        if int(waypoint[0]/Pagination) == Page:
            lineX = LeftBuffer + int(((waypoint[0] - Page*Pagination)/Pagination)*HorPixels)
            draw.line([lineX,TopBuffer+VertPixels-int(PixelPerElev*waypoint[1])+ MarkerLength,\
                       lineX,TopBuffer+VertPixels-int(PixelPerElev*waypoint[1])],\
                      ElevationColor, MarkerWeight)
            if waypoint[4]: #Special Triangle Marker
                draw.polygon([lineX,TopBuffer+VertPixels-int(PixelPerElev*waypoint[1])+ MarkerLength - MarkerWeight,\
                          lineX-int(TriangleMarkerSize/2),TopBuffer+VertPixels-int(PixelPerElev*waypoint[1])+TriangleMarkerSize + MarkerLength - MarkerWeight,\
                          lineX+int(TriangleMarkerSize/2),TopBuffer+VertPixels-int(PixelPerElev*waypoint[1])+TriangleMarkerSize + MarkerLength - MarkerWeight],\
                         ElevationColor)

            #Distance to end (SOBO on a NOBO guide)
            DTE = "%.1f" % (TotalDistance - waypoint[0])
            txtWidth, txtHeight = WayPointFont.getsize(DTE)
            drawtxt.text((dteEdge-txtWidth,lineX + waypoint[5]-WayPointFont.font.ascent),DTE,'black', WayPointFont)

            #Distance to start (NOBO on a NOBO guide)
            DTS = "%.1f" % waypoint[0]
            txtWidth, txtHeight = WayPointFontBold.getsize(DTS)
            drawtxt.text((dtsEdge-txtWidth,lineX + waypoint[5]-WayPointFontBold.font.ascent),DTS,'black', WayPointFontBold)

            #Description of waypoint
            txtWidth, txtHeight = WayPointFont.getsize(waypoint[2])
            EndDesc = DescriptionEdge+txtWidth
            drawtxt.text((DescriptionEdge,lineX + waypoint[5]-WayPointFont.font.ascent),waypoint[2],'black', WayPointFont)

            #Elevation
            Elevation = "%.0f" % round(waypoint[1])
            txtWidth, txtHeight = WayPointFont.getsize(Elevation)
            drawtxt.text((TopBuffer + VertPixels + BottomBuffer - ElevationEdge - txtWidth,lineX + waypoint[5]-WayPointFont.font.ascent),Elevation,'black', WayPointFont)
            #print(Elevation)

            #Services
            txtWidth, txtHeight = WayPointFont.getsize(waypoint[3])
            BeginService = TopBuffer + VertPixels + BottomBuffer - ServicesEdge - txtWidth
            drawtxt.text((BeginService,lineX + waypoint[5]-ServiceGlyphs.font.ascent),waypoint[3],'black', ServiceGlyphs)

            #Readability dots
            txtWidth, txtHeight = WayPointFont.getsize(DotLineSymbol)
            if not EndDesc % PixelsPerDotLine == 0:
                EndDesc = EndDesc + PixelsPerDotLine - EndDesc % PixelsPerDotLine
            assert (EndDesc % PixelsPerDotLine) == 0
            for dot in range(0,BeginService - EndDesc - txtWidth,PixelsPerDotLine):
                    drawtxt.text((EndDesc + dot,lineX + waypoint[5]-WayPointFont.font.ascent),DotLineSymbol,'black', WayPointFont)


    #Rotate and merge text
    txtplot = txtplot.rotate(90,"1",True)
    elevplot.paste(txtplot,None, txtplot)

    del draw
    del drawtxt

    elevplot.save(imageFile + str(PageNumber[Page])+ imageExt, dpi = (1200, 1200))

