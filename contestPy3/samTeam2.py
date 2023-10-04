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
  def __eq__(self, other) : 
    return self.__dict__ == other.__dict__

    

#################
# Team creation #
#################

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
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
 
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    self.walls = gameState.data.layout.walls
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    print(gameState.getAgentState(self.index))
    actions = gameState.getLegalActions(self.index)
    values = [self.getFeatures(gameState, a) for a in actions]
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
    while cell.prev != None:
      path.append(cell.value)
      cell = cell.prev
    return path.reverse()

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
    best = values[0]
    print('---------------')
    for action in values:
      print(action)
      if action['distanceFromFood'] < best['distanceFromFood']:
        best = action
    return best['action']

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    features['action'] = action
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    
    # offense or defense
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0
    
    # if food will be consumed on the next movement the distance from food is zero
    if len(self.getFood(gameState).asList()) > len(self.getFood(successor).asList()):
      features['distanceFromFood'] = 0
    else:
      # Compute distance to the nearest food
      foodList = self.getFood(successor).asList()  
      if len(foodList) > 0: 
        features['closestFood'] = self.astar(myPos, min(foodList, key=lambda x: self.getMazeDistance(myPos, x)))
        features['distanceFromFood'] = features['closestFood'].td

    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [p for p in enemies if p.getPosition() != None and p.isPacman]
    if len(invaders) > 0:
      features['invaderPositions'] = map(lambda x: x.getPosition(), invaders)
      features['closestInvader'] = self.astar(myPos, min(features['invaderPositions'], key=lambda x: self.getMazeDistance(myPos, x)))

    ### Offense only calculations ###
    if features['onDefense'] == 0:
      capsules = self.getCapsules(successor)
      if len(capsules) > 0:  
        features['closestCapsule'] = self.astar(myPos, min(capsules, key=lambda x: self.getMazeDistance(myPos, x)))
      ghosts = [p for p in enemies if p.getPosition() != None and not p.isPacman]
      if len(ghosts) > 0:
        features['ghostPositions'] = map(lambda x: x.getPosition(), ghosts)
        features['closestGhost'] = self.astar(myPos, min(features['ghostPositions'], key=lambda x: self.getMazeDistance(myPos, x)))

    return features
