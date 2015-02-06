#!/bin/python
'''
Contains global parameters/definitions for simulation
'''

#Library imports
import numpy as np
import networkx as nx
import sympy as sp
import random
import sys
import multiprocessing

'''
Person (node): represents an individual which could possibly become
infected.
'''
class Person:
    #Global Parameters
    timeToCure = 4

    #Individual Parameters
    def __init__(self, name, gridCenter, gridStdDev):
        self.name = name
        self.alive = True     #Not dead yet
        self.infected = False #True if infected
        self.whenInfected = 0 #Timestep when infected (from simulation)
        self.timeInfected = 0 #Time in days since infection
        self.onMeds = False   #True if medication has been administered
        self.whenOnMeds = 0   #Timestep when given meds
        self.timeOnMeds = 0   #Times in days since starting medication
        self.immune = False   #If true, remove from simulation (?)
        self.location = [random.gauss(gridCenter[0], gridStdDev[0]), 
                        random.gauss(gridCenter[1], gridStdDev[1])] #(x[0],y[1]) coordinate pair
        self.hygiene = random.uniform(0,0.1) #Factors into save/infect chance (and heal)
        self.color = "green"  #Green if not infected, red if infected
        self.chanceToLoseMeds = random.uniform(0,0.3) #If on meds, chance to forget
        self.fear = random.uniform(0, 0.1)  #Fear factor, changes movement rate
        self.myGridCenter = gridCenter
        self.myGridStdDev = gridStdDev

    #Functions
    def chanceToContact(self, n, gridStdDev): #Chance to contact another node
        dist = np.sqrt((self.location[0]-n.location[0])**2 + (self.location[1]-n.location[1])**2)
        return np.exp(-0.5*(dist/(self.fear*gridStdDev[0])**2))    #Depends on gridStdDev and fear factor

    def chanceToInfect(self):  #Chance to infect contacted node
        return (1+np.exp(-0.46*(self.timeInfected-13.3)))**(-1)

    def chanceToResist(self):    #Chance to resist infection
        return self.hygiene * random.uniform(0,1) #Should always be below 1

    def becomeInfected(self, timestep): #Called when chanceToResist < chanceToInfect
        self.whenInfected = timestep
        self.infected = True
        self.color = "red"

    def updateTimeInfected(self, timestep): #Called each timestep to find length of infection
        if self.infected == True:
            self.timeInfected = timestep - self.whenInfected

    def receiveMeds(self, timestamp): #Called when successfully given meds
        self.onMeds = True
        self.whenOnMeds = timestamp
        self.color = "orange"

    def takeMeds(self, timestep):
        if self.onMeds == True: 
            if self.hygiene * random.uniform(0,1) > self.chanceToLoseMeds: #Remember to take meds
                self.timeOnMeds = timestep - self.whenOnMeds
                if self.timeOnMeds > timeToCure: #If taken long enough, consider cured & immune
                    self.immune = True
            else:
                self.onMeds = False  #Forgot to take meds; consider inneffective


'''
Healer (node): represents person that can attempt to heal another
person (or healer). Extends Person, with attributes related to healing 
'''
class Healer(Person):
    #Individual parameters
    def __init__(self, name, gridCenter, gridStdDev):
        super(self.__class__, self).__init__(name, gridCenter, gridStdDev)
        self.maxCanHeal = 10  #Like the number of drugs they are carrying 
        self.color = "blue"
        self.hygiene = random.uniform(0.9,1) #Higher becuase they are trained

    #Functions
    def chanceToHeal(self): #Called when in contact with infected
        random.uniform(0,1)


'''
Hospital (node): a place where people can recieve medicine/vaccines, but
with a limited supply.
'''
class Hospital():
    def __init__(self, location, initMeds, initVaccines):
        self.location = location
        self.meds = initMeds
        self.vaccines = initVaccines

'''
Contact (undirected edge): represents a contact event, where node n1 contacts n2.
'''
class Contact:
    #Individual parameters
    def __init__(self, n1, n2, timestep):
        self.distance = np.sqrt((n1.location[0]-n2.location[0])**2 + (n1.location[1]-n2.location[1])**2)
        self.timeOfContact = timestep
        #Not really origin/target, just for naming really
        self.origin = n1 
        self.target = n2

'''
Infect (directed edge): represents n1 infecting n2 (n1 -> n2)
'''
class Infect:
    #Individual parameters
    def __init__(self, n1, n2, timestamp):
        self.timeOfInfection = timestamp
        self.origin = n1
        self.target = n2
