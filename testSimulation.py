#!/bin/python
'''
A test simulation to play with
'''

#Library/file imports
from simGlobal import *


#Parameters for simulation
simName = (sys.argv[1])
random.seed(sys.argv[2])
time = open("../data/" + simName + "_time.csv", "w")
total = open("../data/" + simName + "_total.csv", "w")
log = open("../data/" + simName + "_log.csv", "w")

print("Simulation name: " + sys.argv[1])
print("Random seed: " + sys.argv[2])
log.write("Simulation name: " + sys.argv[1] + "\n")
log.write("Random seed: " + sys.argv[2] + "\n")

#Global parameters
maxTimeSteps = 365          #In days
vaccinePumpTime = 30        #In days
vaccinePumpAmount = 400     #In doses
medsPumpTime = 30           #In days
medsPumpAmount = 10000       #In doses (all will be split amongst hubs!)
initVaccinesPerRegion = [1000, 500] #Array, #vaccines/region
initMedsPerRegion = [1000, 500]  #Array, #meds/region

#Population parameters
percentBeginLatent = 0.1    #Percent that start in latent state
percentDoctors = 0.06    #Percentage per region that are doctors

#Region paramters
regionNames =["A", "B"]     #Names of regions
locations = [[0,0], [-50,100]]  #Array of arrays of coordinates
populations = [100000, 20000]   #Array of initial populations
isHub = [True, True]    #Array of bools, true if recieves large shipments  

#Hospital parameters
numHospitalsPerRegion = [2, 1]  #Array of values, number in each region
bedsPerHospital = 2000          #Maybe array at some point?

log.write("vaccinePumpTime: " + str(vaccinePumpTime) + "\n")
log.write("vaccinePumpAmount: " + str(vaccinePumpAmount) + "\n")
log.write("medsPumpTime: " + str(medsPumpTime) + "\n")
log.write("initVaccinesPerRegion: " + str(initVaccinesPerRegion) + "\n")
log.write("initMedsPerRegion: " + str(initMedsPerRegion) + "\n")
log.write("percentBeginLatent: " + str(percentBeginLatent) + "\n")
log.write("percentDoctors: " + str(percentDoctors) + "\n")
log.write("regionNames: " + str(regionNames) + "\n")
log.write("locations: " + str(locations) + "\n")
log.write("populations: " + str(populations) + "\n")
log.write("isHub: " + str(isHub) + "\n")
log.write("numHospitalsPerRegion: " + str(numHospitalsPerRegion) + "\n")
log.write("bedsPerHospital: " + str(bedsPerHospital) + "\n")

#Create regions
regions = []
paramsLists = [LiberiaParams, LiberiaParams]    #Array of arrays of parameters
for i in range(0, len(regionNames)):
    regions.append(Region(regionNames[i], locations[i], isHub[i], paramsLists[i]))

#Parameter DON'T FORGAYT
regionConnections = ([[regions[1]], 
                      [regions[0]]])  #List of list of connections
log.write("regionConnections: " + str(regionConnections) + "\n")

#Create people
allPeople = []    #List for each region
for i in range(0, len(regions)):
    allPeople.append([])
    for j in range(0, populations[i]):
        allPeople[i].append(Person("p", "s", regions[i]))
        chance = random.uniform(0,1)
        if chance < percentBeginLatent:
            allPeople[i][j].state = "l"
        elif chance < (percentBeginLatent + percentDoctors):
            allPeople[i][j].occupation = "s"

#Create hospitals
allHospitals = []     #List for each region
for i in range(0, len(regions)):
    allHospitals.append([])
    for j in range(0, numHospitalsPerRegion[i]):
        allHospitals[i].append(Hospital(regions[i], bedsPerHospital,
                               float(initVaccinesPerRegion[i])/numHospitalsPerRegion[i],
                               float(initMedsPerRegion[i])/numHospitalsPerRegion[i]))


#Associate hospitals/people with regions
for i in range(0, len(regions)):
    regions[i].hospitals = allHospitals[i]
    regions[i].people = allPeople[i]
    regions[i].updateTotals()


#Data stuff
data = [["Day", "NumberNewlyInfected", "NumberNewlyCured", "NumberNewlyVaccinated",
        "NumberNewlyDied", "NumberNewlyBuried", "NumberHospitalized", "NumberMoved"]]
totals = [0,0,0,0,0,0,0,0]

#################################
#Begin simulation
#################################
for t in range(0, maxTimeSteps):
    currentDataRow = [t, 0, 0, 0, 0, 0, 0, 0]
   
    #Add vaccines/meds if they've arrived
    if (t % vaccinePumpTime) == 0:    #Deliver vaccines to hubs
        for r in regions:
            if r.isHub:
                for h in r.hospitals:
                    h.vaccines = (h.vaccines + vaccinePumpAmount/len(r.hospitals))

    if (t % medsPumpTime) == 0:       #Deliver meds to hubs
        for r in regions:
            if r.isHub:
                for h in r.hospitals:
                    h.meds = (h.meds + medsPumpAmount/len(r.hospitals))
    
    #Let people interact
    for people in allPeople:
        for p in people:
            Activate(p, currentDataRow)

    data.append(currentDataRow) #Append data to time-resolved list
    totals = [sum(x) for x in zip(currentDataRow, totals)]  #Add new data to total

    #Update region population/infection totals
    for r in regions:
        r.people = []
        total_i1 = 0
        total_i2 = 0
        total_u = 0

        for people in allPeople:
            for p in people:
                if p.region is r:
                    r.people.append(p)
        r.updateTotals()
    print(currentDataRow)

#Print to screen and file
print(data[0])
print(totals)

for row in data:
    for item in row:
        time.write(str(item) + ",")
    time.write("\n")

totals_titled = []
totals_titled.append(data[0])
totals_titled.append(totals)
for row in totals_titled:
    for item in row:
        total.write(str(item) + ",")
    total.write("\n")

log.close()
time.close()
total.close()
