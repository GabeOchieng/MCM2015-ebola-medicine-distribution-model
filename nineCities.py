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
maxTimeSteps = 365/2          #In days
vaccinePumpTime = 5        #In days
vaccinePumpAmount = 100 * 9 *0 #In doses
medsPumpTime = 5           #In days
medsPumpAmount = 1000 * 9 *0       #In doses (all will be split amongst hubs!)
medsEffectiveness = 5 
initVaccinesPerRegion = [0,0,0,0,0,0,0,0,0] #Array, #vaccines/region
initMedsPerRegion = [0,0,0,0,0,0,0,0,0]  #Array, #meds/region

#Population parameters
percentBeginLatent = ([0.05, 0.05, 0.05, 
                       0.05, 0.05, 0.05, 
                       0.05, 0.05, 0.05])    #Percent that start in latent state
percentDoctors = 0.0002    #Percentage per region that are doctors

#Region paramters
regionNames = (["A", "B", "C", 
                "D", "E", "F", 
                "G", "H", "I"])     #Names of regions

locations = ([[11.318,-12.283], [9.31,-12.16], [10.898, -12.63], 
              [8.484,-13.23], [8.669,-12.75], [7.88,-11.19],
              [6.301,-10.797], [4.754,-7.846], [6.259,-10.514]])  #Array of arrays- coordinates

populations = ([25000, 17000, 176000, 
                80000, 27000, 50000,
                94000, 27500, 5700])   #Array of initial populations
'''
isHub = ([False, False, True, 
         True, False, False,
         True, False, False])    #Array of bools, true if recieves large shipments  
'''
#Rurals are hubs
isHub = ([False, True, False, 
         True, False, False,
         False, False, True])    #Array of bools, true if recieves large shipments  

#Hospital parameters
numHospitalsPerRegion = [4,4,4,
                         4,4,4,
                         4,4,4]  #Array of values, number in each region
bedsPerHospital = 8 * 2          #Maybe array at some point?

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
paramsLists = [LiberiaParams, LiberiaParams, LiberiaParams, 
               SierraParams, SierraParams, SierraParams,
               LiberiaParams, LiberiaParams, LiberiaParams]    #Array of arrays of parameters

for i in range(0, len(regionNames)):
    regions.append(Region(regionNames[i], locations[i], isHub[i], paramsLists[i]))

#Parameter DON'T FORGAYT
a = regions #alias to make things easier, 0 -> A, 1 -> B, etc.
regionConnections = ([[a[1]],                   [a[0],a[2],a[5],a[7]],  [a[1],a[3]],
                      [a[2],a[4],a[5],a[6]],    [a[3]],                 [a[1],a[3],a[7]],
                      [a[3],a[7]],              [a[1],a[5],a[8]],       [a[7]]])       

'''
#Urbans are hubs
regionShippingTo = ([[],                [a[0]],     [a[1]],
                     [a[4],a[5]],       [],         [],
                     [a[7]],            [a[8]],     []])   #What regions do each other region ship meds to

regionVaccineShippingPercentage = ([0.5,0.5,0.5,
                                    0.5,0.5,0.5,
                                    0.5,0.5,0.5])
regionMedsShippingPercentage =  ([0.5,0.5,0.5,
                                  0.5,0.5,0.5,
                                  0.5,0.5,0.5])

'''
#Rurals are hubs
regionShippingTo = ([[],                        [a[0],a[2],a[7]],               [a[3]],
                    [a[2], a[4],a[5],a[6]],      [],                             [a[3]],
                    [a[3]],                     [a[6],a[8],a[5]],               []])   #What regions do each other region ship meds to
regionVaccineShippingPercentage = ([0.5,0.5,0.5,
                                    0.5,0.5,0.5,
                                    0.5,0.5,0.5])
regionMedsShippingPercentage =  ([0.5,0.5,0.5,
                                  0.5,0.5,0.5,
                                  0.5,0.5,0.5])

log.write("regionConnections: " + str(regionConnections) + "\n")
log.write("regionShippingTo: " + str(regionShippingTo) + "\n")
log.write("regionVaccineShippingPercentage: " + str(regionVaccineShippingPercentage) + "\n")
log.write("regionMedsShippingPercentage: " + str(regionMedsShippingPercentage) + "\n")

#Create people
allPeople = []    #List for each region
for i in range(0, len(regions)):
    allPeople.append([])
    for j in range(0, populations[i]):
        allPeople[i].append(Person("p", "s", regions[i]))
        chance = random.uniform(0,1)
        if chance < percentBeginLatent[i]:
            allPeople[i][j].state = "l"
        elif chance < (percentBeginLatent[i] + percentDoctors):
            allPeople[i][j].occupation = "d"

#Create hospitals
allHospitals = []     #List for each region
for i in range(0, len(regions)):
    allHospitals.append([])
    for j in range(0, numHospitalsPerRegion[i]):
        allHospitals[i].append(Hospital(regions[i], bedsPerHospital,
                               float(initMedsPerRegion[i])/numHospitalsPerRegion[i],
                               float(initVaccinesPerRegion[i])/numHospitalsPerRegion[i]))


#Associate hospitals/people with regions
for i in range(0, len(regions)):
    regions[i].hospitals = allHospitals[i]
    regions[i].people = allPeople[i]
    regions[i].regionConnections = regionConnections[i]
    regions[i].regionShippingTo = regionShippingTo[i]
    regions[i].regionVaccineShippingPercentage = regionVaccineShippingPercentage[i]    # %Total shipped out per day
    regions[i].regionMedsShippingPercentage = regionMedsShippingPercentage[i]    # %Total shipped out per day
    regions[i].updateTotals()


#Data stuff
data = [["Day", "NumberNewlyInfected", "NumberNewlyCured", "NumberNewlyVaccinated",
        "NumberNewlyDied", "NumberNewlyBuried", "NumberHospitalized", "NumberMoved, NumberMedsUsed, NumberVaccinesUsed"]]
totals = [0,0,0,0,0,0,0,0,0,0]

#################################
#Begin simulation
#################################
for t in range(0, maxTimeSteps):
    currentDataRow = [t, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    
    #Recalculate probabilities to move
    movementProbability = dict() 
    for ri in regions:
        for rj in regions:
            movementProbability[ri.name + rj.name] = ChanceToMove(ri, rj)
   
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
            Activate(p, currentDataRow, movementProbability, medsEffectiveness)

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

#######################
#End simulation
#######################

#Print to screen and file
print(data[0])
for r in regions:
    print("People in region " + r.name + " : " + str(len(r.people)))


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
