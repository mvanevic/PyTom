import numpy
import os
from pytom.gui.additional.tiltAlignmentFunctions import markerResidual
from pytom.gui.additional.imageStructures import ImageStack
from pytom.gui.additional.TiltAlignmentStructures import TiltAlignmentParameters, TiltSeries, TiltAlignment
from pytom.basic.functions import initSphere, taper_edges

def refineMarkerPositions( tiltSeriesName, markerFileName, firstProj, 
                           lastProj, finealigfile, dimBox=32, projIndices=None, tiltSeriesFormat='em',ret=False,write=True,ireftilt=21,size=30000):
    """
    refine coordinates of markers
    """
    mask = None

    #read data
    MyTiltAlignmentParas=TiltAlignmentParameters(
        dmag=False, drot=False, dbeam=False,
    finealig=True, finealigfile=finealigfile,
    grad=False,
    irefmark=1, ireftilt=ireftilt, r=None, cent= [1025,1025],
    handflip=False,
    optimizer='leastsq', maxIter=0)
    MyTiltSeries= TiltSeries(tiltSeriesName=tiltSeriesName,
        TiltAlignmentParas=MyTiltAlignmentParas,
        alignedTiltSeriesName='dummy',
        markerFileName=markerFileName,
                             firstProj=firstProj, lastProj=lastProj,projIndices=projIndices,tiltSeriesFormat=tiltSeriesFormat)
    MyTiltAlignment = TiltAlignment(MyTiltSeries)
    MyTiltAlignment.computeCoarseAlignment( MyTiltSeries)
    #MyTiltAlignment.alignFromFiducials()

    dxdy_markers = numpy.zeros((len(projIndices),len(MyTiltSeries._Markers),2),dtype=float)
    missing = []
    for (imark, marker) in enumerate(MyTiltSeries._Markers):
        markerImageStack = ImageStack(verbose=False)
        len_stack = 0
        for itilt in range(0,len(marker._projIndices)):
            x = round(marker.get_xProj(itilt))
            y = round(marker.get_yProj(itilt))

            if (x> 0.01) and ( y  > 0.01):
                proj = MyTiltSeries._ProjectionList[itilt]
                filename = proj.getFilename()
                #copy data to ImageStack

                xmin, ymin = x-dimBox//2-2, y-dimBox//2-2
                xend, yend= min(xmin+dimBox, size), min(ymin+dimBox,size)
                xoff, yoff = dimBox-(xend-xmin), dimBox-(yend-ymin)

                markerImageStack.addImageFromFile(filename=filename, boxCoords=[max(0,xmin), max(0,ymin), 0],
                                                  dims=[int(dimBox+min(0,xmin)-xoff), int(dimBox+min(0,yoff)-xoff), 1], shiftX=0, shiftY=0, rotation=0,
                                                  appliedShiftX=0, appliedShiftY=0, index=itilt)



                len_stack +=1
            else:
                proj = MyTiltSeries._ProjectionList[itilt]
                print("marker not clicked in "+proj.getFilename())
        #markerImageStack.normalize( normtype="StdMeanInMask", mask=mask)
        if len_stack == 0:
            continue
        markerImageStack.bandpass( lowfreq=dimBox/32., hifreq=6.*dimBox/32.,
        smooth=2.*dimBox/32., bpf=None)
        markerImageStack.normalize( normtype="StdMean")
        # smoothen edges
        markerImageStack.taper_edges( width=dimBox/8.)
        markerImageStack.exMaxAlign( niter=10, mask=mask)
        if write:
            dirname = os.path.dirname(tiltSeriesName)
            markerImageStack.writeWorkingCopies( filename="{}/Marker_{:02d}.em".format(dirname,imark) )
            markerImageStack.writeAverage( filename='{}/av_{:02d}.em'.format(dirname,imark) )

        # set new coordinates
        irun = 0

        for itilt in range(0,len(marker._projIndices)):

            x = round(marker.get_xProj(itilt))
            y = round(marker.get_yProj(itilt))

            if ( x > -1 ) and ( y > -1 ):
                try:
                    dx = x+markerImageStack.images[irun].shiftX
                    dy = y+markerImageStack.images[irun].shiftY
                except: continue
                dxdy_markers[itilt][imark][0] = dy
                dxdy_markers[itilt][imark][1] = dx
                marker.set_xProj(itilt, x+ markerImageStack.images[irun].shiftX)
                marker.set_yProj(itilt, y+ markerImageStack.images[irun].shiftY)
                irun = irun + 1
    #(psiindeg, shiftX, shiftY, x, y, z, distLine, diffX, diffY,
    #     shiftVarX, shiftVarY) = MyTiltAlignment.computeCoarseAlignment( MyTiltSeries)

    #for i in range(len(MyTiltSeries._Markers)):
    errors = MyTiltAlignment.alignmentResidual()
    transX = MyTiltAlignment._alignmentTransY - MyTiltAlignment.TiltSeries_._TiltAlignmentParas.cent[0]
    transY = MyTiltAlignment._alignmentTransX - MyTiltAlignment.TiltSeries_._TiltAlignmentParas.cent[1]

    if ret:
        return dxdy_markers, errors, transX, transY

