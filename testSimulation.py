#!/bin/python
'''
A test simulation to play with
'''

#Library/file imports
from simGlobal import *


#Parameters for simulation
random.seed(sys.argv[1])

print("Random seed: " + sys.argv[1])

timeStep = 1        #In days
maxTimeSteps = 20   #In days
maxPeople = 10000    #Initial number
gridCenter = [0,0]  #Center of grid
gridStdDev = [10, 10] #StdDev in each direction
contactThresh = 0.8 #If chanceToContact > this, they meet
infectionInitial = 0.5 #0.2 -> 20% infection at start

#Create nodes (people/healers)
#These arrays mirror one another index-wise; the Node ones
#are simply used in the graph explicitly.
people = []
peopleNodes = []    #Can't explicitly use people/healers as nodes

for i in range(0,maxPeople):
    people.append(Person("p" + str(i), gridCenter, gridStdDev))
    if i > maxPeople * infectionInitial:
        people[i].becomeInfected(0)
    peopleNodes.append("p" + str(i))

print("Number of people: " + str(len(people)))

#Add hospitals to this scenario
h1 = Hospital([0,0], 10, 10)
h2 = Hospital([15,-16], 10, 10)

#Create graph, add nodes
G = nx.DiGraph()
G.add_nodes_from(peopleNodes)

#Begin simulation
for t in range(0, maxTimeSteps):
    print("Day: " + str(t))
    print("Number of new infections: " + str(len(G.edges())))
    #Interactions between people and hospitals

    #Interactions between people and people
    for i in range(0, len(people)):
        person1 = people[i]
        if person1.infected is True:
            person1.updateTimeInfected(t)
        
        for j in range(i+1, len(people)):
            person2 = people[j]
            if person2.infected is True:
                person2.updateTimeInfected(t)
            
            chanceToContact = person1.chanceToContact(person2, gridStdDev)
            if chanceToContact > contactThresh:
                #They contact
                if person1.infected is True and person2.infected is False and person2.immune is False:
                    if person1.chanceToInfect() > person2.chanceToResist():
                        person2.becomeInfected(t)
                        G.add_edge(peopleNodes[i], peopleNodes[j])
                        print("Infection occurs")
                elif person2.infected is True and person1.infected is False and person1.immune is False:
                    if person2.chanceToInfect() > person1.chanceToResist():
                        person1.becomeInfected(t)
                        G.add_edge(peopleNodes[j], peopleNodes[i])
                        print("Infection occurs")
                else:
                    print("No infection occurs.")



