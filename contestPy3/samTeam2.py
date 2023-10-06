# baselineTeam.py
# ---------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from capture import AgentRules
from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Actions, Directions
import game
from util import nearestPoint

class Cell():
  def __init__(self, value, dfs, dfe, prev):
    self.value = value
    self.dfs = dfs
    self.dfe = dfe
    self.td = self.dfs + self.dfe
    self.prev = prev

#################
# Team creation #
#################
global index1
global index2
global redTeam

def createTeam(firstIndex, secondIndex, isRed,
               first = 'ReflexCaptureAgent', second = 'ReflexCaptureAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """
  global index1
  global index2
  index1 = firstIndex
  index2 = secondIndex
  global redTeam
  redTeam = isRed
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
 
  def registerInitialState(self, gameState):
    global index1
    global index2
    global redTeam
    self.start = gameState.getAgentPosition(self.index)
    self.walls = gameState.data.layout.walls
    self.isRed = redTeam
    self.teamIndex = self.index == index1 and index2 or index1
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    # print(gameState.getAgentState(self.index))
    actions = gameState.getLegalActions(self.index)
    values = [self.survey(gameState, a) for a in actions]
    bestAction = self.evaluate(values)
    return bestAction
  
  def astar(self, p1, p2):
    walls = self.walls
    current = Cell(p1, 0, self.getMazeDistance(p1,p2), None)
    open = [current]
    closed = []
    while len(open) > 0:
      closest = min(open, key=lambda x: x.td)
      if closest.value == p2:
        return closest
      open.remove(closest)
      closed.append(closest)
      x = closest.value[0]
      y = closest.value[1]
      neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
      for n in neighbors:
        if not walls[int(n[0])][int(n[1])] and not any(x.value == n for x in closed):
          newcell = Cell(n,closest.dfs+1,self.getMazeDistance(n,p2),closest)
          open.append(newcell)
    return None
  
  def buildPath(self, cell):
    path = []
    while not cell.prev == None:
      path.append(cell.value)
      cell = cell.prev
    path.reverse()
    return path

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, values):
    # determine which action is best based on calculated values
    weights = {'special': 200, "retreat": 100, "defense": 2, "offense": 1}
    best = values[0]
    bestweight = 9999
    for action in values:
      # high priority actions like eating capsule of enemy is near
      if action['special'] != None and (action['special'] / weights['special']) <  bestweight:
        bestweight = (action['special'] / weights['special'])
        best = action
      if action['retreat'] != None and (action['retreat'] / weights['retreat']) <  bestweight:
        bestweight = (action['retreat'] / weights['retreat'])
        best = action
      if action['defense'] != None and (action['defense'] / weights['defense']) <  bestweight:
        bestweight = (action['defense'] / weights['defense'])
        best = action
      if action['offense'] != None and (action['offense'] / weights['offense']) <  bestweight:
        bestweight = (action['offense'] / weights['offense'])
        best = action
    return best['action']

  def survey(self, gameState, action):
    """
    Returns a counter of data for the state
    """
    data = {}
    data['action'] = action
    data['offense'] = None
    data['defense'] = None
    data['retreat'] = None
    data['special'] = None

    successor = self.getSuccessor(gameState, action)
    prevState = gameState.getAgentState(self.index)
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    
    # offense or defense
    data['onDefense'] = 1
    if myState.isPacman: data['onDefense'] = 0
    data['foodCarrying'] = myState.numCarrying
    data['prevFoodCarrying'] = prevState.numCarrying

    data['distanceFromFood'] = 9999
    # find food
    foodList = self.getFood(successor).asList()  
    # if food will be consumed on the next movement the distance from food is zero
    if len(self.getFood(gameState).asList()) > len(self.getFood(successor).asList()):
      data['distanceFromFood'] = 0
    else:
      # Compute distance to the nearest food
      if len(foodList) > 0: 
        data['closestFood'] = self.astar(myPos, min(foodList, key=lambda x: self.getMazeDistance(myPos, x)))
        data['distanceFromFood'] = data['closestFood'].td

    ### find enemies ###
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    prevEnemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    invaders = [p for p in enemies if p.getPosition() != None and p.isPacman]
    prevInvaders = [p for p in prevEnemies if p.getPosition() != None and p.isPacman]
    data['numInvaders'] = len(invaders)
    data['numPrevInvaders'] = len(prevInvaders)
    if len(invaders) > 0:
      data['invaderPositions'] = list(map(lambda x: x.getPosition(), invaders))
      data['closestInvader'] = self.astar(myPos, min(data['invaderPositions'], key=lambda x: self.getMazeDistance(myPos, x)))
      data['distanceToInvader'] = data['closestInvader'].td

    ### Offense only calculations ###
    ghosts = []
    if data['onDefense'] == 0:
      capsules = self.getCapsules(successor)
      if len(capsules) > 0:  
        data['closestCapsule'] = self.astar(myPos, min(capsules, key=lambda x: self.getMazeDistance(myPos, x)))
        data['distanceToCapsule'] = data['closestCapsule'].td
      ghosts = [p for p in enemies if p.getPosition() != None and not p.isPacman]
      if len(ghosts) > 0:
        data['ghostPositions'] = list(map(lambda x: x.getPosition(), ghosts))
        data['closestGhost'] = self.astar(myPos, min(data['ghostPositions'], key=lambda x: self.getMazeDistance(myPos, x)))
        data['distanceToGhost'] = data['closestGhost'].td
      # if you can get to a pellet before the closest defender, go for it
      if 'distanceToGhost' in data and 'distanceToCapsule' in data and data['distanceToGhost'] < 10 and data['distanceToCapsule'] < data['distanceToGhost']:
        data['special'] = data['distanceToCapsule']
      # if a move would deposit food on your side
        # retreat based on number of food carried versus how close defenders are
      if ('distanceToGhost' in data and data['distanceToGhost'] < (data['foodCarrying'] * 2)) or data['foodCarrying'] >= 1:
        print(action)
        data['retreat'] = self.getMazeDistance(myPos,self.start)
    ### Defense only calculations ###
    else:
      if data['numPrevInvaders'] > 0:
        # this move would kill an enemy
        if data['numPrevInvaders'] > data['numInvaders']:
          data['defense'] = 0
        else:
          data['defense'] = data['distanceToInvader']
      # moving back onto defense would deposit carried food
      if data['prevFoodCarrying'] > 0 and data['foodCarrying'] == 0:
        data['retreat'] = 0

    ## check if teammate or ghosts block the path to closest food, if so find a clear path
    if 'closestFood' in data and data['distanceFromFood'] > 1:
      obstacles = [successor.getAgentState(self.teamIndex).getPosition()]
      if len(ghosts) > 0:
        for g in data['ghostPositions']:
          obstacles.append(g)
      foodPath = self.buildPath(data['closestFood'])
      while any(i in foodPath for i in obstacles) and len(foodList) > 1:
        foodList.remove(data['closestFood'].value)
        data['closestFood'] = self.astar(myPos, min(foodList, key=lambda x: self.getMazeDistance(myPos, x)))
        data['distanceFromFood'] = data['closestFood'].td
    data['offense'] = data['distanceFromFood']

    return data
