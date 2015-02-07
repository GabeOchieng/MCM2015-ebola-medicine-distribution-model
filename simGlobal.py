#!/bin/python
'''
Contains global parameters/definitions for simulation
'''

#Library imports
#import numpy as np
#import networkx as nx
#import sympy as sp
import random
import sys
import math
#import multiprocessing

'''
Person (node): represents an individual which could possibly become
infected.
'''
class Person:
    #Global Parameters
    #Individual Parameters
    def __init__(self, occupation, state, region):
        self.occupation = occupation    #[p]erson, [d]octor   
        self.state = state   #[s]usceptible, [l]atent, [i]nfection[1], 
                             #[i]nfectious[2], [h]ospitalized, [c]ured,
                             #[v]accinated, [d]ead, [b]uried
        self.region = region #Abstration of their location  



'''
Hospital (node): a place where people can recieve medicine/vaccines, but
with a limited supply.
'''
class Hospital():
    def __init__(self, region, doctors, initMeds, initVaccines):
        self.region = region
        self.doctors = doctors      #Array of doctors
        self.meds = initMeds
        self.vaccines = initVaccines

'''
Region (node): represents a region (location), has parameters relating to 
number of hospitals, population density, etc.
'''

class Region():
    def __init__(self, name, location, isHub, popDens, params):
        self.name = name
        self.location = location
        self.isHub = isHub    #True if hub (deleveries from overseas)
        self.hospitals = []  #List of hospital objects
        self.doctors = []  #List of doctors in this region
        self.people = []
        self.popDens = popDens  #Population 
        self.beta_c1 = params[0]
        self.beta_c2 = params[1]
        self.beta_f = params[2]
        self.gamma_h1 = params[3]
        self.gamma_h2 = params[4]
        self.gamma_dh = params[5]
        self.gamma_d = params[6]
        self.gamma_f = params[7]
        self.gamma_R = params[8]
        self.RC_1 = params[9]
        self.RC_2 = params[10]
        self.beta_v = params[11]
        self.beta_h3 = params[12]

        self.total_i1 = 0
        self.total_i2 = 0
        self.total_u = 0

    def updateTotals(self, total_i1, total_i2, total_u):
        self.total_i1 = total_i1
        self.total_i2 = total_i2
        self.total_u = total_u


'''
Parameters for different countries
'''
LiberiaParams = ([0.16, 0.32, 0.489, 0.062, 0.062, 0.197/3.24, 0.197/3.24, 
                0.5/10.07, 0.803*0.5/13.31, 1/2.01, 0.5/15.88, 0, 0, 0, 
                0.062])


'''
Distance: euclidean distance between two points
'''
def Distance(r1, r2):
    return (float((r1.location[0]-r2.location[0])**2 + (r1.location[1]-r2.location[1])**2)**(0.5))


'''
FlowRate: raw flow rate between two different regions
'''
def FlowRate(r1, r2):
    return 13.83*(float(r1.popDens)**(0.86) + float(r2.popDens)**(0.78))/((Distance(r1,r2)**(-1.52)))


'''
TotalFlowRate: sum of all flow rates from region r
'''
def TotalFlowRate(r):
    total = 0
    for region in r.connectedRegions:
        total = total + FlowRate(r, region)
    return total


'''
ChanceToMove: return chance for any p to move somewhere
'''
def ChanceToMove(r):
    chance = TotalFlowRate(r)/(float(r.popDens))
    return chance


'''
TryToMove: returns new region if p moves, None otherwise
'''
def TryToMove(p):
    chance = random.uniform(0,1)
    #print("DEBUG: ChanceToMove: " + str(ChanceToMove(p.region)))
    if chance < ChanceToMove(p.region):
        chance = random.uniform(0,1)
        previousChances = 0
        for r in p.region.connectedRegions:
            currentChance = FlowRate(p.region, r)/float(p.region.popDens)
            previousChances = previousChances + currentChance
            if chance < previousChances:
                return r
        return None


'''
The logic gates every person goes through on each iteration
i.e. our model
'''
def Activate(p, currentDataRow):    #p a person or doctor in the simulation
    if p.occupation == "p" or p.occupation == "d": #TODO: differentiate between
        #[b]uried dead
        if p.state == "b":
            pass
        
        #[u]nburied dead
        elif p.state == "u":
            chanceToGetBuried = random.uniform(0,1)
            if (chanceToGetBuried < p.region.gamma_f):
                p.state = "b"
                currentDataRow[5] = currentDataRow[5] + 1
        
        #[c]ured
        elif p.state == "c":
            pass

        #[v]accinated
        elif p.state == "v":
            pass

        #[s]usceptible to infection
        elif p.state == "s":
            #try to get vaccinated
            for h in p.region.hospitals:
                chanceToVaccinate = random.uniform(0,1)
                if h.vaccines != 0:
                    if (chanceToVaccinate < h.vaccines/float(p.region.popDens)):
                        p.state = "v"
                        h.vaccines = h.vaccines - 1
                        currentDataRow[3] = currentDataRow[3] + 1
                        #print("Vaccinated.")
                        break
                    #print("Not vaccinated.")

            #CAN STILL GET SICK ON THIS DAY IF VACCINATED
            chanceToContact = random.uniform(0,1)
            chanceToGetSick = random.uniform(0,1)
            #print("chanceToContact: " + str(chanceToContact))
            #print("chanceToGetSick: " + str(chanceToGetSick))
            #print("chanceToBeat: " + str(p.region.total_i1/float(p.region.popDens)))
            if (chanceToContact < (p.region.total_i1/float(p.region.popDens))):   
                #p contacts sick person from infectious1
                if (chanceToGetSick < p.region.beta_c1):
                    #p gets infected from infectious1 
                    p.state = "l"
                    currentDataRow[1] = currentDataRow[1] + 1
            elif (chanceToContact < (p.region.total_i2/float(p.region.popDens))):
                #p contacts sick person from infectious2
                if (chanceToGetSick < p.region.beta_c2):
                    #p gets infected from infectious2
                    p.state = "l"
                    currentDataRow[1] = currentDataRow[1] + 1
            elif (chanceToContact < (p.region.total_u/float(p.region.popDens))):
                #p contacts unburied dead
                if (chanceToGetSick < p.region.beta_f):
                    #p gets infected from the unburied dead 
                    p.state = "l"
                    currentDataRow[1] = currentDataRow[1] + 1
            #TODO: Have them try to move from region to region
            newRegion = TryToMove(p)
            if newRegion is not None:
                p.region = newRegion
                currentDataRow[6] = currentDataRow[6] + 1

        #[l]atent
        elif p.state == "l":
            chanceToProgress = random.uniform(0,1)
            #print("chanceToProgress to i1: " + str(chanceToProgress))
            if (chanceToProgress < 0.083):   #Go to i1, more symptomatic
                p.state = "i1"
            #    print("DEBUG: l -> i1")
            #TODO: Have them try to move from region to region
            newRegion = TryToMove(p)
            if newRegion is not None:
                p.region = newRegion

        #[i]nfectious[1] - first stage, mildly symptomatic
        elif p.state == "i1":
            chanceToProgress = random.uniform(0,1)
            chanceToRecover = random.uniform(0,1)
            chanceToHospitalize = random.uniform(0,1)

            if (chanceToProgress < 0.166):    #Go to i2, most symptomatic
                p.state = "i2"
            elif (chanceToRecover < p.region.RC_1): #Spontaneously get cured
                p.state = "c"
            elif (chanceToHospitalize < p.region.gamma_h1): #Get into hospital
                p.state = "h"
            #TODO: Have them try to move from region to region
            newRegion = TryToMove(p)
            if newRegion is not None:
                p.region = newRegion

        #[i]nfectious[2] - second stage, most symptomatic
        elif p.state == "i2":
            chanceToDie = random.uniform(0,1)
            chanceToRecover = random.uniform(0,1)
            chanceToHospitalize = random.uniform(0,1)

            if (chanceToDie < p.region.gamma_d):    #ded
                p.state = "u"   #[u]nburied
                currentDataRow[4] = currentDataRow[4] + 1
            elif (chanceToRecover < p.region.RC_2): #Spontaneously get cured
                p.state = "c"
                currentDataRow[2] = currentDataRow[2] + 1
            elif (chanceToHospitalize < p.region.gamma_h2): #Get into hospital
                p.state = "h"
            #Cannot move in this stage

        #[h]ospitalized - get cured, or maybe die trying
        elif p.state == "h":
            chanceToRecover = random.uniform(0,1)
            chanceToSeeDoctor = random.uniform(0,1)

            for h in p.region.hospitals:
                if ((h.meds !=  0) and (chanceToSeeDoctor < len(p.region.doctors)/
                    (p.region.total_i1 + p.region.total_i2 + 1))):
                    h.meds = h.meds - 1 #Use meds regardless of if they work
                    if (chanceToRecover < p.region.gamma_R):    #Get cured
                        p.state = "c"
                        currentDataRow[2] = currentDataRow[2] + 1
                        break
            #Cannot move in this stage




