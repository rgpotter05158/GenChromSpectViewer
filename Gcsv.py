import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.patches as patches
from scipy import integrate
from scipy.signal import find_peaks
import csv
import potterIntegrate as pint
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

class App(object):#swapped out object, tk.Frame
    def __init__(self, master):
        self.rt = master
        self.rt.protocol("WM_DELETE_WINDOW", self.onClosing)
        self.menu = tk.Menu(self.rt) 
        self.rt.title('NMR GUI - Potter')
        self.rt.config(menu = self.menu)
        self.filemenu = tk.Menu(self.menu)
        self.menu.add_cascade(label = 'File', menu = self.filemenu)
        self.Master = master
        self.filemenu.add_command(label = 'New')
        self.filemenu.add_command(label = 'Open', command = self.openFile)
        self.filemenu.add_separator()
        self.filemenu.add_command(label = 'Exit', command = lambda:[root.quit(), root.destroy()])
        self.helpmenu = tk.Menu(self.menu)
        self.menu.add_cascade(label = 'Help', menu = self.helpmenu)
        self.helpmenu.add_command(label = 'About', command = self.launchHelpWindow)
        self.analysismenu = tk.Menu(self.menu)
        self.menu.add_cascade(label = 'Analysis', menu = self.analysismenu)
        self.analysismenu.add_command(label = 'Integrate', command = self.openIntegrationModule)
        self.analysismenu.add_command(label = 'EditIntegralList', command = self.showIntegralList)
        self.analysismenu.add_command(label = 'Calibrate', command = self.calibrate)
        self.xShift = 0.0    
        self.showIntVar1 = tk.IntVar()
        self.calOn = 0
        self.intVar1 = tk.IntVar()
        self.showPeakVar1 = tk.IntVar()
        self.calVar1 = tk.IntVar()
        self.startCoords = []
        self.endCoords = []
        self.integrals = []
        self.intListVar = []
        self.intGraphics1 = []
        self.intGraphics2 = []
        self.peakList = []
        self.peakGraphics1 = []
        self.intCheckBoxes = []
        self.intDeleteButtons = []
        
        self.rt.mainloop()

    def openFile(self):
        
        self.filename = askopenfilename(parent = self.rt)
        with open(self.filename, mode = 'r') as file:
            self.data = pd.read_csv(file, names = ['x', 'y'])
        self.th = 0.0
        self.t1Top = tk.Frame(self.rt)     
        self.t1Bottom = tk.Frame(self.rt)
        self.t1Top.pack(side = tk.TOP)
        self.t1Bottom.pack(side = tk.BOTTOM)
        self.t1Left = tk.Frame(self.t1Top)
        self.t1Right = tk.Frame(self.t1Top)
        self.t1Left.pack(side = tk.LEFT)
        self.t1Right.pack(side = tk.RIGHT)
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(self.data['x'].max(), self.data['x'].min())
        self.ax.plot(self.data['x'], self.data['y'])
        self.canvas = FigureCanvasTkAgg(self.fig, master = self.rt) 
        self.canvas.draw()
        #self.canvas.get_tk_widget().pack(in_ = self.t1Right, fill = tk.BOTH, expand = 1)
        self.canvas.get_tk_widget().pack(in_ = self.t1Right, fill = tk.BOTH, expand = True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.rt)
        self.toolbar.update()
        #self.canvas.get_tk_widget().pack(in_ = self.t1Right, fill = tk.BOTH, expand = 1)
        self.canvas.get_tk_widget().pack(in_ = self.t1Right, fill = tk.BOTH, expand = True) 
        self.xShiftScale = tk.Scale(self.rt, from_ = self.data['y'].max(), to_ = self.data['y'].min())
        self.xShiftScale.pack(in_ = self.t1Left)     
        self.showIntToggle = tk.Checkbutton(self.rt, text = 'Show Integrals', variable = self.showIntVar1, command = self.showIntegrals)
        self.showIntToggle.pack(in_ = self.t1Bottom, side = tk.RIGHT)
        self.showPeaksToggle = tk.Checkbutton(self.rt, text = 'Show Peaks', variable = self.showPeakVar1, command = self.showPeaks)
        self.showPeaksToggle.pack(in_ = self.t1Bottom, side = tk.RIGHT)

        
    def openIntegrationModule(self):
        self.t = tk.Toplevel(self.rt)
        self.t.protocol("WM_DELETE_WINDOW", self.onIntClosing)
        self.t.wm_title("Integration Module")
        self.intFig = plt.figure()
        self.intAx = self.intFig.add_subplot(111)
        self.intAx.set_xlim(self.data['x'].max(), self.data['x'].min())
        self.intAx.plot(self.data['x'], self.data['y'])
        self.canvas2 = FigureCanvasTkAgg(self.intFig, master = self.t)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack(side = tk.TOP, fill = tk.BOTH, expand = 1)
        self.toolbar2 = NavigationToolbar2Tk(self.canvas2, self.t)
        self.toolbar2.update()
        self.canvas2.get_tk_widget().pack(side = tk.TOP, fill = tk.BOTH, expand = 1)
        self.intToggle = tk.Checkbutton(self.t, text="Integration Mode", variable=self.intVar1, command = self.integrate)
        self.intToggle.pack(side = tk.LEFT)

    def onclick(self, event):
        ix = event.xdata
        self.startCoords.append(ix)

    def onrelease(self, event):
        ix = event.xdata
        self.endCoords.append(ix)
        pint.drawTraps(self.data, min([self.startCoords[-1], self.endCoords[-1]]), max([self.startCoords[-1], self.endCoords[-1]]), self.intAx)
        self.canvas2.draw()

    def integrate(self):
        if self.intVar1.get() == 1:
            self.cid1 = self.canvas2.mpl_connect('button_press_event', self.onclick)
            self.cid2 = self.canvas2.mpl_connect('button_release_event', self.onrelease)
        else:
            self.canvas2.mpl_disconnect(self.cid1)
            self.canvas2.mpl_disconnect(self.cid2)

    def onClosing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.rt.quit()
            self.rt.destroy()

    def onIntClosing(self):
        if messagebox.askokcancel("Quit", "Save integrals?"):
            tempInts = []
            for i in range(len(self.startCoords)):
                tempInts.append(min([self.startCoords[i], self.endCoords[i]]))
                tempInts.append(max([self.startCoords[i], self.endCoords[i]]))
                tempInts.append(pint.trapInt(self.data, tempInts[0], tempInts[1]))
                tempInts.append(1)
                self.integrals.append(tempInts.copy())
                tempInts.clear()
            self.startCoords.clear()
            self.endCoords.clear()
        self.t.destroy()

    def showIntegrals(self):                                
        if self.showIntVar1.get() == 1:
            for i in range(len(self.integrals)):  #this is the region marker
                if (self.integrals[i][3] == 1 and not self.intListVar) or (self.integrals[i][3] == 1 and self.intListVar[i].get() == 1):
                    self.intGraphics1.append(self.ax.annotate('', xy = (self.integrals[i][0], 0), xytext = (self.integrals[i][1], 0), arrowprops = dict(arrowstyle = '<->', facecolor = 'red'),
                                                       annotation_clip = False))
            for i in range(len(self.integrals)):  #this is the line connecting the integral value
                if (self.integrals[i][3] == 1 and not self.intListVar) or (self.integrals[i][3] == 1 and self.intListVar[i].get() == 1):
                    self.intGraphics2.append(self.ax.annotate('{:.2f}'.format(self.integrals[i][2]), xy = (self.integrals[i][0] + ((self.integrals[i][1] - self.integrals[i][0])/2), 0), xytext = (self.integrals[i][0] + ((self.integrals[i][1] - self.integrals[i][0])/2), -3), arrowprops = dict(arrowstyle = '-', facecolor = 'red'),
                                                       annotation_clip = False))
            self.canvas.draw()
        else:
            for i in self.intGraphics1:
                i.remove()
            for i in self.intGraphics2:
                i.remove()
            self.intGraphics1.clear()
            self.intGraphics2.clear()
            self.canvas.draw()

    def showIntegralList(self):
        self.t2 = tk.Toplevel(self.rt)
        self.t2.protocol("WM_DELETE_WINDOW", self.onCloseIntegralListWindow)
        self.t2.wm_title("Integrals")
        self.t2Top = tk.Frame(self.t2)
        self.t2Bottom = tk.Frame(self.t2)
        self.t2Top.pack(side=tk.TOP)
        self.t2Bottom.pack(side = tk.BOTTOM)

        self.t2Left = tk.Frame(self.t2Bottom)
        self.t2Right = tk.Frame(self.t2Bottom)

        self.t2Left.pack(side = tk.LEFT)
        self.t2Right.pack(side = tk.RIGHT)

        for i in range(len(self.integrals)):
            self.intListVar.append(tk.IntVar(value = 1))
            self.intCheckBoxes.append(tk.Checkbutton(self.t2Left, text = str(len(self.integrals)-i) + '\t' + '{:.2f}'.format(self.integrals[i][0]) +
                                                     '\t' + '{:.2f}'.format(self.integrals[i][1]) + '\t' + '{:.2f}'.format(self.integrals[i][2]),
                                                            variable = self.intListVar[i], width = 40))
            self.intDeleteButtons.append(tk.Button(self.t2Right, text = 'Delete: ' + str((len(self.integrals)-i)),
                                                   command = lambda c=i:self.deleteInt(self.integrals, c))) # why not lambda:self.integrals[len(self.integrals)-i-1] ????
            self.intCheckBoxes[i].pack(in_ = self.t2Left, side = tk.BOTTOM, fill = tk.X)
            self.intDeleteButtons[i].pack(in_ = self.t2Right, side = tk.BOTTOM)
            
    def deleteInt(self, ar, inx):
        del self.integrals[int(inx)]

    def onCloseIntegralListWindow(self):
        self.intCheckBoxes.clear()
        self.intDeleteButtons.clear()
        self.canvas.draw()
        self.t2Left.destroy()
        self.t2Right.destroy()
        self.t2Bottom.destroy()
        self.t2Top.destroy()
        self.t2.destroy()
        
    def showPeaks(self): # removed parameter th
        self.th = self.xShiftScale.get()
        self.peakList = find_peaks(self.data['y'].to_numpy(), self.th)
        if self.showPeakVar1.get() == 1:
            a = 0
            for i in range(len(self.peakList[0])):
                if ((self.data.iloc[self.peakList[0][i-1]][1] < self.data.iloc[self.peakList[0][i]][1]) and
                    ((self.data.iloc[self.peakList[0][i-1]][1]) >= (self.data.iloc[self.peakList[0][i]][1] - 0.1)) or
                    ((self.data.iloc[self.peakList[0][i-1]][1] > (self.data.iloc[self.peakList[0][i]][1])) and
                        ((self.data.iloc[self.peakList[0][i-1]][1]) <= (self.data.iloc[self.peakList[0][i]][1] + 0.1)))):
                    a = a + 1
                else:
                    a = a + 0
                self.peakGraphics1.append(self.ax.annotate('{:.2f}'.format(self.data.iloc[self.peakList[0][i]][0]), xy = (self.data.iloc[self.peakList[0][i]][0], self.data.iloc[self.peakList[0][i]][1]), xytext = (self.data.iloc[self.peakList[0][i]][0], self.data.iloc[self.peakList[0][i]][1] + a)))
            self.canvas.draw()
        else:
            for i in self.peakGraphics1:
                i.remove()
            self.peakGraphics1.clear()
            self.canvas.draw()

    def onclick2(self, event):
        ix = event.xdata
        self.xShift = ix
        self.data['x'] = self.data['x'] - self.xShift
        self.shiftIntegrals(self.integrals, self.xShift)
        self.calOn = 0
        self.canvas.mpl_disconnect(self.cid3)
        self.rt.config(cursor='')

    def shiftIntegrals(self, iL, sh):
        msgBox = tk.messagebox.askquestion('Shift Integrals', 'Shift integrals along with spectrum?', icon = 'warning')
        if msgBox == 'yes':
            self.integralShift(iL, sh)
            self.ax.cla()
            self.ax.set_xlim(self.data['x'].max(), self.data['x'].min())
            self.ax.plot(self.data['x'], self.data['y'])
            self.canvas.draw()
        else:
            self.ax.cla()
            self.ax.set_xlim(self.data['x'].max(), self.data['x'].min())
            self.ax.plot(self.data['x'], self.data['y'])
            self.canvas.draw()

    def integralShift(self, ints, xsh):
        for i in range(len(self.integrals)):
            self.integrals[i][0] = self.integrals[i][0] - xsh
            self.integrals[i][1] = self.integrals[i][1] - xsh
        


    def calibrate(self):
        self.rt.config(cursor = 'cross')
        self.calOn = 1
        self.cid3 = self.canvas.mpl_connect('button_press_event', self.onclick2)

    def onHelpClosing(self):
        self.t3.destroy()

    def launchHelpWindow(self):
        self.t3 = tk.Toplevel(self.rt)
        self.t3.protocol("WM_DELETE_HELPWINDOW", self.onHelpClosing)
        self.helpText = tk.Text(self.t3, height = 10, width = 30, wrap = 'word')
        self.helpText.pack(expand=True, fill = tk.BOTH)
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        aboutFile = open(os.path.join(__location__, 'about.rtf'))
        self.helpText.insert(tk.END, aboutFile.read())
        aboutFile.close()
        
                    
root = tk.Tk() 
app = App(root)


            
