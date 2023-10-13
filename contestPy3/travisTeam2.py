from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint


class ReflexCaptureAgent(CaptureAgent):
    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        self.isOffensive = gameState.getAgentState(self.index).isPacman
        CaptureAgent.registerInitialState(self, gameState)

    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        # print(gameState.getAgentState(self.index).numCarrying) # get number of food
        # self.start = where you start, move to here
        # self.isPacman = offense or defense

        for action in actions:
            successor = self.getSuccessor(gameState, action)
            score = self.evaluateOffensive(gameState, action)

            if score > bestScore:
                bestScore = score
                bestAction = action

        return bestAction

    def evaluateOffensive(self, gameState, action):
        # Implement improved offensive evaluation here
        features = self.getOffensiveFeatures(gameState, action)
        weights = self.getOffensiveWeights(gameState, action)
        return features * weights

    def defensiveAction(self, gameState, actions):
        # Implement improved defensive strategy here
        bestAction = Directions.STOP  # Default to STOP
        bestScore = -float("inf")

        for action in actions:
            successor = self.getSuccessor(gameState, action)
            score = self.evaluateDefensive(gameState, action)

            if score > bestScore:
                bestScore = score
                bestAction = action

        return bestAction

    def evaluateDefensive(self, gameState, action):
        # Implement improved defensive evaluation here
        features = self.getDefensiveFeatures(gameState, action)
        weights = self.getDefensiveWeights(gameState, action)
        return features * weights

    def getSuccessor(self, gameState, action):
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    # Implement feature functions for offense and defense
    def getOffensiveFeatures(self, gameState, action):
        features = util.Counter()

        # Implement offensive feature functions here
        # Example: features['featureName'] = featureValue

        return features

    def getOffensiveWeights(self, gameState, action):
        weights = util.Counter()

        # Implement offensive weights here
        # Example: weights['featureName'] = featureWeight

        return weights

    def getDefensiveFeatures(self, gameState, action):
        features = util.Counter()

        # Implement defensive feature functions here
        # Example: features['featureName'] = featureValue

        return features

    def getDefensiveWeights(self, gameState, action):
        weights = util.Counter()

        # Implement defensive weights here
        # Example: weights['featureName'] = featureWeight

        return weights


class OffensiveReflexAgent(ReflexCaptureAgent):
    def getOffensiveFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)

        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

        foodList = self.getFood(successor).asList()
        features['successorScore'] = -len(foodList)

        # Compute distance to the nearest food
        if len(foodList) > 0:
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance

        # Implement additional offensive features here

        return features

    def getOffensiveWeights(self, gameState, action):
        weights = util.Counter()
        weights['successorScore'] = 100
        weights['distanceToFood'] = -1

        # Implement additional offensive weights here

        return weights


class DefensiveReflexAgent(ReflexCaptureAgent):
    def getDefensiveFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)

        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() is not None]
        features['numInvaders'] = len(invaders)
        if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)

        if action == Directions.STOP:
            features['stop'] = 1
        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        if action == rev:
            features['reverse'] = 1

        return features

    def getDefensiveWeights(self, gameState, action):
        weights = util.Counter()
        weights['numInvaders'] = -1000
        weights['stop'] = -100
        weights['invaderDistance'] = -10
        weights['reverse'] = -2

        return weights


# The createTeam function remains unchanged
def createTeam(firstIndex, secondIndex, isRed,
               first='OffensiveReflexAgent', second='DefensiveReflexAgent'):
    return [eval(first)(firstIndex), eval(second)(secondIndex)]
