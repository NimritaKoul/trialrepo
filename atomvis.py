#!/usr/bin/env python

#===== atomvis.py =====
#Simple routines for visualizing a simulation of atoms.
#Requires the VPython module (version >= 5.0).


import visual as v
import numpy as np
import time

SphereList = []
BoxList = []
BoxL = None
Frequency = 0.1
LastTime = time.time()
Initialized = False


def MinImage(Pos, L):
    """Returns a new Pos array with minimum-imaged positions."""
    return Pos / L - np.round_(Pos / L)

def Init(Pos, L = None,
         AtomColor = None, AtomRadius = None,
         AtomTypes = None,
         AtomRadiusDict = {}, AtomRadiusDflt = 1.0,
         AtomColorDict = {}, AtomColorDflt = v.color.green,
         BoxColor = v.color.blue, BackColor = v.color.white,
         DisplayFreq = 0.1):
    """Initializes a 3D visualization window.
Input:
    Pos: (N,3) numpy array of atomic positions
    L: scalar or vector of box lengths
    AtomColor: N-length list of (R,G,B) tuples
    AtomRadius: N-length list of radius values
    AtomTypes: N-length list of atom types for dictionaries below
    AtomRadiusDict: Dictionary with atom type names and radii keys
    AtomRadiusDflt: Default radius for atoms not in dictionary
    AtomColorDict: Dictionary with atom type names and (R,G,B) tuple keys
    AtomColorDflt: Default (R,G,B) tuple color for atoms not in dict
    BoxColor: (R,G,B) tuple color for box; use None for no box
    BackColor: (R,G,B) tuple color for background
    DisplayFreq: frequency with which to update the display, in s
"""
    global BoxL, SphereList, BoxList, Frequency, Initialized
    
    #save box length
    if L is None:
        BoxL = None
    else:
        BoxL = np.array(L, float)
        MinL = np.min(BoxL)

    #save update frequency
    Frequency = DisplayFreq

    #minimum image
    if not BoxL is None:
        Pos = MinImage(Pos, BoxL)

    #clear the box
    del BoxList[:]
    
    #make the box walls
    if not BoxL is None and not BoxColor is None:
        #make a list of all corner points
        l = [-0.5, 0.5]
        Corners = np.array([(x,y,z) for x in l for y in l for z in l], float)
        #sort through pairs of corners; for unit length, draw a cylinder
        for (i, c1) in enumerate(Corners):
            for c2 in Corners[i+1:]:
                if sum((c1 - c2)**2) > 1.0001: continue
                BoxList.append(v.cylinder(pos = c1, axis = c2-c1, radius = 0.01, color = BoxColor))        

    #get atomic radii/colors and add spheres
    del SphereList[:]
    for (i, p) in enumerate(Pos):
        #get radius
        if not AtomRadius is None:
            r = AtomRadius[i]
        elif AtomTypes is None:
            r = AtomRadiusDflt
        else:
            r = AtomRadiusDict.get(AtomTypes[i], AtomRadiusDflt)
        #get color
        if not AtomColor is None:
            c = AtomColor[i]
        elif AtomTypes is None:
            c = AtomColorDflt
        else:
            c = AtomColorDict.get(AtomTypes[i], AtomColorDflt)
        #normalize radius to box length
        if not BoxL is None:
            r = r / MinL
        #add a sphere to the scene
        SphereList.append(v.sphere(pos = p, radius = r, color = c))

    #change the background color
    v.scene.background = BackColor

    #set autocentering and scaling
    if L is None:
        v.scene.autocenter = 1
        v.scene.autoscale = 1

    #set the initialization flag
    Initialized = True


def Update(Pos, L = None, Force = False):
    """Updates a 3D visualization window.
Input:
    Pos: (N,3) numpy array of atomic positions
    L: scalar or vector of box lengths
    Force: True will force an update despite frequency
"""
    global BoxL, SphereList, BoxList, LastTime, Frequency

    #check for update
    if not Force and LastTime + Frequency > time.time():
        return
    LastTime = time.time()

    #array-ize the box length    
    if not L is None:
        L = np.array(L, float)        
    
    #see if we need to change radii because volume changed
    Scale = None
    if not L is None and not BoxL is None:
        OldMinL = np.min(BoxL)
        NewMinL = np.min(L)
        if not np.allclose(OldMinL, NewMinL):
            Scale = OldMinL / NewMinL
        BoxL = L

    #update positions of existing spheres
    if not BoxL is None:
        Pos = MinImage(Pos, BoxL)
    NSphere = len(SphereList)
    for (i, p) in enumerate(Pos):
        if i < NSphere:
            #update existing sphere
            SphereList[i].pos = p
            if not Scale is None:
                SphereList[i].radius *= Scale
        else:
            #make a new sphere
            SphereList.append(v.sphere(pos = p,
                                       radius = SphereList[-1].radius,
                                       color = SphereList[-1].color))

    #see if we need to delete any spheres in case their number changed
    for i in range(len(Pos), NSphere):
        SphereList[-1].visible = False
        del SphereList[-1]
    
def Clear():
    """Clears objects from the visualization window."""
    global BoxL, SphereList, BoxList, Initialized
    while len(SphereList):
        SphereList.pop(-1).visible = False
    while len(BoxList):
        BoxList.pop(-1).visible = False
    Initialized = False

def Close():
    """Closes the 3D visualization window.
"""
    global BoxL, SphereList, BoxList
    Clear()
    v.scene.exit = False
    v.scene.visible = False
    v.scene = None
    

