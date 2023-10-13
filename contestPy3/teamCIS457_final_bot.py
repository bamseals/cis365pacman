from __future__ import print_function

import random
import sys
import util

from captureAgents import CaptureAgent
from game import Directions
from util import nearestPoint


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='DefensiveReflexAgent', second='OffensiveReflexAgent'):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.
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
        actions = gameState.getLegalActions(self.index)

        values = [self.evaluate(gameState, a) for a in actions]

        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        foodLeft = len(self.getFood(gameState).asList())

        # Prioritizes returning if under winning condition or if you have lots of food
        if foodLeft <= 2 or gameState.getAgentState(self.index).numCarrying > 3:
            bestDist = 9999
            bestAction = actions[0]  # Line for safety - if statement has "possibility" to never be enacted.
            for action in actions:
                successor = self.getSuccessor(gameState, action)
                pos2 = successor.getAgentPosition(self.index)
                dist = self.getMazeDistance(self.start, pos2)
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

    def getEnemyPacmans(self, gameState):
        """
        Gives a list of all enemy pacmans/pacmen/pacmeese
        """
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() is not None]
        return invaders

    def getEnemyGhosts(self, gameState):
        """
        Gives a list of all enemy ghosts
        """
        # Gets future states of all opponents
        opp_fut_state = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        # Only lists ghosts
        chasers = [p for p in opp_fut_state if p.getPosition() is not None and not p.isPacman]
        return chasers

    def getDensestFoodDistance(self, gameState):
        """
        Finds the piece of food closest to the other food
        """
        foodList = self.getFood(gameState).asList()
        foodDistList = []
        for foodA in foodList:
            foodDistList.append(sum([self.getMazeDistance(foodA, foodB) for foodB in foodList]))
        # return the distance from the other food, of the piece of food closest to other pieces of food,
        # which means this is currently flawed
        return min(foodDistList)

    def getDistToPC(self, gameState):
        """
        Finds the distance from the agent to the Power Capsule
        """
        PC = self.getCapsules(gameState)[0]
        myPos = gameState.getAgentState(self.index).getPosition()
        return self.getMazeDistance(myPos, PC)

    def estEnemyDist(self, gameState):
        """
        Finds the noisy distances for each opponent and states whether they are pacmen or not
        """
        enemies = self.getOpponents(gameState)
        enemy1 = gameState.getAgentState(enemies[0])
        enemy2 = gameState.getAgentState(enemies[1])

        noisedistances = gameState.getAgentDistances()

        data = [[enemy1.isPacman, noisedistances[enemies[0]], enemies[0]],
                [enemy2.isPacman, noisedistances[enemies[0]], enemies[1]]]

        return data




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

        ''' CLOSEST/AMOUNT OF ENEMY/IES FEATURES '''
        # Determine if the enemy is closer to you than they were last time
        chasers = self.getEnemyGhosts(successor)

        features['nearbyEnemies'] = len(chasers)

        # Finds the closest opponent in range
        close_dist = 9999.0
        if len(chasers) > 0:
            # Measures distance from agent to each enemy, minimum of those
            close_dist = min([float(self.getMazeDistance(myPos, c.getPosition())) for c in chasers])
            
            # Fleeing behavior
            notInWay = (self.getMazeDistance(chasers[0].getPosition(), self.start) >
                        self.getMazeDistance(myPos, self.start))
            if successor.getAgentState(self.index).isPacman:  # and notInWay:
                # RUN HOME
                if close_dist < 4:
                    features['fleeHome'] = self.getMazeDistance(myPos, self.start)
            elif not successor.getAgentState(self.index).isPacman:  # and notInWay:
                # If you are a ghost, you are only in danger if you cross the border
                if (self.index == 0 or self.index == 2):
                    # Moving increases visible area and allows for enemies to leave radius
                    if action == Directions.WEST and close_dist < 4:
                        features['settle'] = 1
                elif (self.index == 1 or self.index == 3):
                    if action == Directions.EAST and close_dist < 4:
                        features['settle'] = 1
            elif not successor.getAgentState(self.index).isPacman and not notInWay:
                # Their turn to run, now.
                features['defend'] = close_dist
            
            # Calculate distance to the Power Capsule for leverage against enemies
            distToPC = self.getDistToPC(successor)
            if len(chasers) > 1 and distToPC < close_dist:
                features['PCDistance'] = distToPC
        ''' ----END OF FEATURE---- '''

        ''' FOOD FEATURE '''
        foodList = self.getFood(successor).asList()
        # Compute distance to the nearest food
        if len(foodList) > 0:
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance

        # Head to most food-dense area
        features['denseFoodDist'] = self.getDensestFoodDistance(successor)
        # - 218 base val - non-functional
        ''' ----END OF FEATURE---- '''

        ''' SCORE FEATURE '''
        features['successorScore'] = -len(foodList)
        ''' ----END OF FEATURE---- '''

        return features

    def getWeights(self, gameState, action):
        return {'successorScore': 100, 'distanceToFood': -1, 'fleeEnemy': -100.0, 'fleeHome': -100,
                'defend': -100, 'settle': 1000}


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

        ''' DEFENSE FEATURE '''
        # Computes whether we're on defense (1) or offense (0)
        # Keeps Agent in Base
        features['onDefense'] = 1
        if myState.isPacman:
            features['onDefense'] = 0
        ''' ----END OF FEATURE---- '''

        ''' CLOSEST/AMOUNT OF ENEMY/IES FEATURES '''
        # Computes distance to invaders we can see
        invaders = self.getEnemyPacmans(successor)
        features['numInvaders'] = len(invaders)
        enemyinfo = self.estEnemyDist(successor)

        # Maps estimated enemy distances to features
        # Allows defending ghost to 'track' enemies down
        # However, Noise means these don't always change between moves. TL;DR no effect
        if(enemyinfo[0][0] == True):
            features['enemyADistance'] = -enemyinfo[0][1]*10
        elif enemyinfo[0][0] == False:
            features['enemyADistance'] = -enemyinfo[0][1]
        if (enemyinfo[1][0] == True):
            features['enemyBDistance'] = -enemyinfo[1][1]*10
        elif enemyinfo[1][0] == False:
            features['enemyBDistance'] = -enemyinfo[1][1]

        # Calculates distance to invaders
        if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)
        ''' ----END OF FEATURE---- '''

        ''' CLOSEST FOOD FEATURE '''
        # Move agent toward other side (LOW PRIORITY)
        # Essentially camps the food closest to enemy side, by focusing on its reflection.
        foodList = self.getFood(successor).asList()
        # Compute distance to the nearest food
        if len(foodList) > 0:
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance
        ''' ----END OF FEATURE---- '''

        ''' STOP/REVERSE FEATURES '''
        # Keeps defender moving unless there is an invader,
        # effectively increasing visible area by at least 5 spaces
        if action == Directions.STOP:
            features['stop'] = 1
        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        if action == rev:
            features['reverse'] = 1
        ''' ----END OF FEATURE---- '''

        return features

    def getWeights(self, gameState, action):
        return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'enemyADistance': 1,
                'enemyBDistance': 1, 'distanceToFood': -1, 'stop': -100, 'reverse': -2}

