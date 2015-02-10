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
    def __init__(self, region, beds, initMeds, initVaccines):
        self.region = region
        self.numBeds = beds
        self.meds = initMeds
        self.vaccines = initVaccines

'''
Region (node): represents a region (location), has parameters relating to 
number of hospitals, population density, etc.
'''

class Region():
    def __init__(self, name, location, isHub, params):
        self.name = name
        self.location = location
        self.isHub = isHub    #True if hub (deleveries from overseas)
        self.hospitals = []  #List of hospital objects
        self.people = []
        self.regionConnections = None
        self.regionShippingTo = None
        self.regionVaccineShippingPercentage = 0
        self.regionMedsShippingPercentage = 0
        self.vaccines = 0
        self.meds = 0
        self.doctors = 0    #Number of doctors in region
        self.popDens = 0  #Population 
        self.fear = 1     #<1 for bad area, >1 for safe area
        self.beta_c1 = params[0]
        self.beta_c2 = params[1]
        self.beta_f = params[2]
        self.beta_h1 = params[3]
        self.beta_h2 = params[4]
        self.gamma_h1 = params[5]
        self.gamma_h2 = params[6]
        self.gamma_dh = params[7]
        self.gamma_d = params[8]
        self.gamma_f = params[9]
        self.gamma_R = params[10]
        self.RC_1 = params[11]
        self.RC_2 = params[12]
        self.beta_v = params[13]
        self.beta_h3 = params[14]
        self.total_i1 = 0
        self.total_i2 = 0
        self.total_u = 0
        self.total_h = 0

    def updateTotals(self):
        self.total_i1 = 0
        self.total_i2 = 0
        self.total_u = 0
        self.total_h = 0
        self.doctors = 0
        self.numBeds = 0
        self.vaccines = 0
        self.meds = 0
        self.popDens = len(self.people)
        for p in self.people:
            if p.occupation == "d":
                self.doctors = self.doctors + 1
            if p.state == "i1":
                self.total_i1 = self.total_i1 + 1
            elif p.state == "i2":
                self.total_i2 = self.total_i2 + 1
            elif p.state == "u":
                self.total_u = self.total_u + 1
            elif p.state == "h":
                self.total_h = self.total_h + 1
        for h in self.hospitals:
            self.numBeds = self.numBeds + h.numBeds
            self.vaccines = self.vaccines + h.vaccines
            self.meds = self.meds + h.meds
        self.numBeds = self.numBeds - self.total_h  #Subtract how many are taken
        print("numBeds: " + str(self.numBeds))
        self.fear = math.exp((self.total_i1 + self.total_i2 + self.total_u 
                              - self.numBeds - self.doctors)/self.popDens)
       
        if len(self.regionShippingTo) == 0:
            return
        vaccinesToShip = (self.regionVaccineShippingPercentage 
                         * self.vaccines / len(self.regionShippingTo))   #Ship this many to each
        medsToShip = (self.regionMedsShippingPercentage
                     * self.meds / len(self.regionShippingTo))
        suscSum = 0
        vaccSum = 0
        medsSum = 0

        for r in self.regionShippingTo:
            r.vaccines = r.vaccines + vaccinesToShip
            self.vaccines = self.vaccines - vaccinesToShip
            r.meds = r.meds + medsToShip
            self.meds = self.meds - medsToShip


'''
Parameters for different countries
'''
LiberiaParams = ([0.16, 0.32, 0.489, 0.062, 0.062, 0.197/3.24, 0.197/3.24, 
                0.0551, 0.0335, 1/2.01, 0.028, 0, 0, 0, 
                0.062])

SierraParams = ([0.128,0.256,0.111,0.080,0.080,.197/4.12,2*.197/4.12,.75/6.26,
                 0.803*.75/10.38,1/4.50,.75/15.88,0.10,0.10,0,0.080])

'''
Distance: euclidean distance between two points with [lat,long]
'''
def Distance(r1, r2):
    #return (float((r1.location[0]-r2.location[0])**2 + (r1.location[1]-r2.location[1])**2)**(0.5))
    return math.acos(math.sin(r1.location[0] * math.pi/180.0) * math.sin(r2.location[0] * math.pi/180.0)
            + (math.cos(r1.location[0] * math.pi/180.0) * math.cos(r2.location[0] * math.pi/180.0)
            * math.cos(r2.location[1] * math.pi/180.0 - r1.location[1] * math.pi/180.0))) * 6371
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
ChanceToMove: return chance for any p to move from r1 to r2 (r1 != r2)
'''
def ChanceToMove(r1, r2):
    #chance = TotalFlowRate(r)/(float(r.popDens))
    chance = 0
    a = 0.78
    b = 1.6
    y = 1.54
    
    sumDistances = 0
    sumThing = 0
    if len(r1.regionConnections) != 0:
        for rk in r1.regionConnections:
            sumDistances = sumDistances + Distance(r1,rk)**b
            sumThing = sumThing + (rk.fear * r1.popDens**a / Distance(r1, rk)**b)
    else:   #Gracefully handle divide by zero errors
        print("No connected regions.")
        return chance

    if r1 is not r2:
        chance = (r2.fear * (r2.popDens**a / Distance(r1,r2)**b) 
                            *(((r1.fear * r1.popDens**y * 2**b) / sumDistances) 
                            + sumThing)**(-1))
    elif r1 is r2:
        chance = (r1.fear * ((r1.popDens**y * 2**b)  / sumDistances)          
                             *(((r1.fear * r1.popDens**y * 2**b) / sumDistances) 
                             + sumThing)**(-1))
    return chance/5


'''
TryToMove: returns new region if p moves, None otherwise
'''
def TryToMove(p, movementProbability):
    chance = random.uniform(0,1)
    #print("Chance : " + str(chance))
    previousChances = 0
    it = iter(sorted(movementProbability.items()))
    for key, prob in it:
        for i, name in enumerate(key):      #Only use probabilities from originating from our city
            if (i == 0) and (name == p.region.name):
                chanceToBeat = previousChances + prob
                #print(key + " Probability: " + str(prob))
                
                if chance < chanceToBeat:   #Move to city
                    regionName = ""
                    for i, name in enumerate(key):
                        if i == 1:
                            regionName = name
                    for r in p.region.regionConnections:
                        if r.name == regionName:
                            #print("Travelling from p.region: " + p.region.name + " to: " + name)
                            return r
                        elif r.name == p.region.name:   #"City" to move to is your own
                            return p.region
                else:
                    previousChances = previousChances + prob    #Try for next city
    return p.region 

'''
The logic gates every person goes through on each iteration
i.e. our model
'''
#p a person or doctor in the simulation
def Activate(p, currentDataRow, movementProbability, medsEffectiveness):    
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
                if h.vaccines > 0:
                    if (chanceToVaccinate < h.vaccines/float(p.region.popDens)):
                        p.state = "v"
                        h.vaccines = h.vaccines - 1
                        currentDataRow[3] = currentDataRow[3] + 1
                        currentDataRow[9] = currentDataRow[9] + 1
                        break

            #CAN STILL GET SICK ON THIS DAY IF VACCINATED
            chanceToContact = random.uniform(0,1)
            chanceToGetSick = random.uniform(0,1)
            factor = 10.0
            if (chanceToContact < (1*p.region.total_i1/float(factor*p.region.popDens))):   
                #p contacts sick person from infectious1
                if (chanceToGetSick < p.region.beta_c1):
                    #p gets infected from infectious1 
                    p.state = "l"
            elif (chanceToContact < (p.region.total_i2/float(factor*p.region.popDens))):
                #p contacts sick person from infectious2
                if (chanceToGetSick < p.region.beta_c2):
                    #p gets infected from infectious2
                    p.state = "l"
            elif (chanceToContact < (p.region.total_u/float(factor*p.region.popDens))):
                #p contacts unburied dead
                if (chanceToGetSick < p.region.beta_f):
                    #p gets infected from the unburied dead 
                    p.state = "l"
            
            newRegion = TryToMove(p, movementProbability)
            if newRegion is not p.region:
                p.region = newRegion
                currentDataRow[7] = currentDataRow[7] + 1

        #[l]atent
        elif p.state == "l":
            chanceToProgress = random.uniform(0,1)
            
            #try to get vaccinated, EVEN THOUGH it's not useful
            for h in p.region.hospitals:
                chanceToVaccinate = random.uniform(0,1)
                if h.vaccines > 0:
                    if (chanceToVaccinate < h.vaccines/float(p.region.popDens)):
                        h.vaccines = h.vaccines - 1
                        currentDataRow[9] = currentDataRow[9] + 1
                        break
            
            if (chanceToProgress < 0.083):   #Go to i1, more symptomatic
                p.state = "i1"
                currentDataRow[1] = currentDataRow[1] + 1

            newRegion = TryToMove(p, movementProbability)
            if newRegion is not p.region:
                p.region = newRegion
                currentDataRow[7] = currentDataRow[7] + 1

        #[i]nfectious[1] - first stage, mildly symptomatic
        elif p.state == "i1":
            chanceToProgress = random.uniform(0,1)
            chanceToRecover = random.uniform(0,1)
            chanceToHospitalize = random.uniform(0,1)

            if (chanceToProgress < 0.166):    #Go to i2, most symptomatic
                p.state = "i2"
            elif (chanceToRecover < p.region.RC_1): #Spontaneously get cured
                p.state = "c"
                currentDataRow[2] = currentDataRow[2] + 1
            elif (chanceToHospitalize < p.region.gamma_h1
                  and p.region.numBeds > 0): #Get into hospital
                p.state = "h"
                p.region.numBeds = p.region.numBeds - 1
                currentDataRow[6] = currentDataRow[6] + 1
            if p.state != "i2" and p.state != "h":
                newRegion = TryToMove(p, movementProbability)
                if newRegion is not p.region:
                    p.region = newRegion
                    currentDataRow[7] = currentDataRow[7] + 1

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
            elif ((chanceToHospitalize < p.region.gamma_h2)
                  and (p.region.numBeds > 0)): #Get into hospital
                p.state = "h"
                p.region.numBeds = p.region.numBeds - 1
                currentDataRow[6] = currentDataRow[6] + 1

        #[h]ospitalized - get cured, or maybe die trying
        elif p.state == "h":
            chanceToRecover = random.uniform(0,1)
            chanceToSeeDoctor = random.uniform(0,1)
            chanceToDie = random.uniform(0,1)

            for h in p.region.hospitals:
                if ((h.meds >  0)): #and (chanceToSeeDoctor < p.region.doctors)/
                    #(p.region.total_i1 + p.region.total_i2 + 1)):
                    h.meds = h.meds - 1 #Use meds regardless of if they work
                    currentDataRow[8] = currentDataRow[8] + 1
                    if (chanceToRecover < (medsEffectiveness * p.region.gamma_R)):   #Get cured
                        p.state = "c"
                        p.region.numBeds = p.region.numBeds + 1
                        currentDataRow[2] = currentDataRow[2] + 1
                        chanceToDie = 1 #Can't die
                        chanceToRecover = 1 #Can't recover either, already did
                        break
            
            if p.state == "h":
                if (chanceToRecover < p.region.gamma_R):
                    p.state = "c"
                    p.region.numBeds = p.region.numBeds + 1
                    currentDataRow[2] = currentDataRow[2] + 1
            
                elif chanceToDie < p.region.gamma_dh: #Died in hospital
                    p.state = "u"
                    p.region.numBeds = p.region.numBeds + 1
                    currentDataRow[4] = currentDataRow[4] + 1




