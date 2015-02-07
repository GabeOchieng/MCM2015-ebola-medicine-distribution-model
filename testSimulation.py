#!/bin/python
'''
A test simulation to play with
'''

#Library/file imports
from simGlobal import *


#Parameters for simulation
random.seed(sys.argv[1])

print("Random seed: " + sys.argv[1])

maxTimeSteps = 200          #In days
percentBeginLatent = 0.2    #Percent that start in latent state
percentageDoctors = 0.06    #Percentage per region that are doctors

#Create regions
A = Region("A", [0,0], True, 100000, LiberiaParams)
B = Region("B", [-5,10], True, 10000, LiberiaParams)

#Connect regions
A.connectedRegions = [B]
B.connectedRegions = [A]

#Creat people
people_A = []
for i in range(0,A.popDens):
    people_A.append(Person("p", "s", A))
    chance = random.uniform(0,1)
    if chance < percentBeginLatent:
        people_A[i].state = "l"
    
people_B = []
for i in range(0,B.popDens):
    people_B.append(Person("p", "s", B))
    chance = random.uniform(0,1)
    if chance < percentBeginLatent:
        people_B[i].state = "l"

#Create doctors
doctors_A = []
for i in range(0, math.trunc(A.popDens*percentageDoctors)):
    doctors_A.append(Person("d", "s", A))

doctors_B = []
for i in range(0, math.trunc(B.popDens*percentageDoctors)):
    doctors_B.append(Person("d", "s", B))

#Creat Hospitals
hospitals_A = []
hospitals_A.append(Hospital(A, doctors_A, 100, 100))
hospitals_A.append(Hospital(A, doctors_A, 100, 100))
A.people = people_A
A.hospitals = hospitals_A
A.doctors = doctors_A

hospitals_B = []
hospitals_B.append(Hospital(B, doctors_B, 100, 100))
hospitals_B.append(Hospital(B, doctors_B, 100, 100))
B.people = people_B
B.hospitals = hospitals_B
B.doctors = doctors_B

#Wrapping things into nice little lists
allPeople = [people_A, people_B]
allDoctors = [doctors_A, doctors_B]
allHospitals = [hospitals_A, hospitals_B] #Might not use
allRegions = [A,B]

#Data stuff
data = [["day", "numberNewlyInfected", "numberNewlyCured", "numberNewlyVaccinated",
        "numberNewlyDied", "numberNewlyBuried", "numberMoved"]]
totals = [0,0,0,0,0,0,0]
#Begin simulation
for t in range(0, maxTimeSteps):
    #[timestep, numberNewlyInfected, numberNewlyCured, numberNewlyVaccinated,
    #numberNewlyDied, numberNewlyBuried, numberMoved]
    currentDataRow = [t, 0, 0, 0, 0, 0, 0]
    
    #Let people interact
    for people in allPeople:
        for p in people:
            Activate(p, currentDataRow)
    data.append(currentDataRow)
    totals = [sum(x) for x in zip(currentDataRow, totals)]

    #Inform regions of their new people
    for r in allRegions:
        r.people = []
        total_i1 = 0
        total_i2 = 0
        total_u = 0

        for people in allPeople:
            for p in people:
                if p.region is r:
                    r.people.append(p)
                    if p.state == "i1":
                        total_i1 = total_i1 + 1
                    elif p.state == "i2":
                        total_i2 = total_i2 + 1
                    elif p.state == "u":
                        total_u = total_u + 1
        r.updateTotals(total_i1, total_i2, total_u)
    print(currentDataRow)

print(data[0])
print(totals)

