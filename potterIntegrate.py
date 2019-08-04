import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.patches as patches
from scipy import integrate
import csv

def trapIntAll(ar):
    '''This function integrates the entire dataset passed to it as an array'''
    area = 0
    for i in range(1, len(ar)):
        sumHeight = ((float(ar[i-1][1])) + (float(ar[i][1])))
        width = ((float(ar[i][0])) - (float(ar[i-1][0])))
        area = area + ((sumHeight * width)/2)
    return area

#consider using binary search to find stopIndex and endIndex from potentially large datasets
def getStart(ar, s):
    '''This function gets the index of the lower bound of the integral.  Pass the same array as the one used for integration.'''
    for i in range(len(ar)):
        if float(ar[i][0]) >= s:
            if i == 0:
                return l
            else:
                return i
                 
def getStop(ar, s):
    '''This function gets the index of the upper bound of the integral.  Pass the same array as the one used for integration.'''
    for i in range(len(ar)):
        if float(ar[i][0]) > s:
            return i
    return len(ar)

def trapInt(ar, st, sp):
    '''This function integrates the dataset passed to it as an array (argument 1).The next two arguments are upper bounds of the integral, respectively.'''
    if isinstance(ar, pd.DataFrame):
        ar = ar.to_numpy()
    sArea = 0
    #print('RANGE! ', range(getStart(ar, st), getStop(ar, sp)))
    for i in range(getStart(ar, st), getStop(ar, sp)):
        sumHeight = ((float(ar[i-1][1])) + (float(ar[i][1])))
        width = abs((float(ar[i][0])) - (float(ar[i-1][0])))
        sArea = sArea + (sumHeight * width)/2
    return sArea

def drawTraps(ar, st, sp, axis):
    '''This function draws the trapezoids used to integrate the function over the selected region. First three arguments are the array containing the data used for integration.  Fourth is the object created by matplotlib.pyplot.figure()  (usually named as ax)'''
    if isinstance(ar, pd.DataFrame):
        ar = ar.to_numpy()
    for i in range(getStart(ar, st), getStop(ar, sp)):
        x = [float(ar[i-1][0]), float(ar[i][0]),float(ar[i][0]),float(ar[i-1][0])]
        if (float(ar[i][1]) + float(ar[i-1][1]))/2.0 >= 0:
            y = [0, 0, float(ar[i][1]),float(ar[i-1][1])]
        else:
            y = [float(ar[i-1][1]),float(ar[i][1]),0,0]
        axis.add_patch(patches.Polygon(xy=list(zip(x,y)), fill = False))
        
        

    
        
