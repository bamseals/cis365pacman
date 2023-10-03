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
  def __init__(self, value, state, dfs, dfe, prev):
    self.value = value
    self.state = state
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
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    print(gameState.getAgentState(self.index))
    actions = gameState.getLegalActions(self.index)
    randomFood = random.sample(self.getFood(gameState).asList(), 4)
    values = [self.getFeatures(gameState, a, randomFood) for a in actions]
    bestAction = self.evaluate(values)
    return bestAction
  
  def astarDistance(self, gameState, p2):
    loc = gameState.getAgentState(self.index).getPosition()
    pos = Cell(loc, gameState, 0, self.getMazeDistance(loc,p2), None)
    openqueue = [pos]
    closedqueue = []
    successor = gameState
    eval = 0
    while len(openqueue) > 0:
      eval += 1
      if pos.value == p2:
        return pos.dfs
      closedqueue.append(pos.value)
      openqueue.remove(pos)
      legalActions = successor.getLegalActions(self.index)
      for a in legalActions:
        if not a == 'Stop':
          next = self.getSuccessor(successor, a)
          val = next.getAgentState(self.index).getPosition()
          if not val in closedqueue:
            dfe = self.getMazeDistance(val,p2)
            cell = Cell(val, next, (pos.dfs + 1), dfe, pos)
            openqueue.append(cell)
      closest = min(openqueue, key=lambda x: x.td)
      pos = closest
      successor = closest.state

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
    for action in values:
      if action['distanceFromFood'] < best['distanceFromFood']:
        best = action
    return best['action']

  def getFeatures(self, gameState, action, foodList):
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

    # Compute distance to the nearest food
    features['distanceFromFood'] = 9999
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      for food in foodList: 
        d = self.astarDistance(successor, food)
        print(d)
        # d = self.getMazeDistance(myPos, food)
        if d < features['distanceFromFood']:
          features['distanceFromFood'] = d

    # Computer distance to nearest enemy
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    features['distanceFromEnemy'] = 9999
    for enemy in enemies:
      if enemy.getPosition() != None:
        # d = self.astarDistance(successor, enemy)
        d = self.getMazeDistance(myPos ,enemy.getPosition())
        if d < features['distanceFromEnemy']:
          features['distanceFromEnemy'] = d

    return features
