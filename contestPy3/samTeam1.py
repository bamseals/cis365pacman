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
from __future__ import print_function
from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions
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
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
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
    actions = gameState.getLegalActions(self.index)
    # print(gameState.getAgentState(self.index).numCarrying) # get number of food
    # self.start = where you start, move to here
    # self.isPacman = offense or defense

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    
    values = [self.evaluate(gameState, a) for a in actions]
    if self.index == 1:
      print(actions)
      print(values)
      # print(self.getPreviousObservation(), file=sys.stderr)

    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    # if self.index == 1:
    #   print(bestActions, file=sys.stderr)

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2 or gameState.getAgentState(self.index).numCarrying > 5:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

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

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """

    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)

    if self.index == 1:
      print(str(features) + str(weights), file=sys.stderr)
      # print(gameState.getAgentState(self.index)) # Print out a text representation of the world.

    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)

    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}
  
  def astarDistance2(self, p1, p2):
    walls = self.walls
    current = Cell(p1, 0, self.getMazeDistance(p1,p2), None)
    open = [current]
    closed = []
    while len(open) > 0:
      closest = min(open, key=lambda x: x.td)
      if closest.value == p2:
        return closest.dfs
      open.remove(closest)
      closed.append(closest)
      x = closest.value[0]
      y = closest.value[1]
      neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
      for n in neighbors:
        if not walls[int(n[0])][int(n[1])] and not any(x.value == n for x in closed):
          newcell = Cell(n,closest.dfs+1,self.getMazeDistance(n,p2),closest)
          open.append(newcell)
    return 9999

class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    foodList = self.getFood(successor).asList()    
    features['successorScore'] = -len(foodList)#self.getScore(successor)

    # Compute distance to the nearest food
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.astarDistance2(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance

    # Determine if the enemy is closer to you than they were last time
    # and you are in their territory.
    # Note: This behavior isn't perfect, and can force Pacman to cower 
    # in a corner.  I leave it up to you to improve this behavior.
    close_dist = 9999.0
    if self.index == 1 and gameState.getAgentState(self.index).isPacman:
      opp_fut_state = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      chasers = [p for p in opp_fut_state if p.getPosition() != None and not p.isPacman]
      if len(chasers) > 0:
        close_dist = min([float(self.getMazeDistance(myPos, c.getPosition())) for c in chasers])

      # View the action and close distance information for each 
      # possible move choice.
      print("Action: "+str(action))
      print("\t\t"+str(close_dist), sys.stderr)

    features['fleeEnemy'] = 1.0/close_dist

    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1, 'fleeEnemy': -100.0}

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.astarDistance2(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}
