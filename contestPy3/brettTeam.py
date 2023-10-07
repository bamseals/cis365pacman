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
               first='OffensiveReflexAgent', second='DefensiveReflexAgent'):
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
        actions = gameState.getLegalActions(self.index)
        # print(gameState.getAgentState(self.index).numCarrying) # get number of food
        # self.start = where you start, move to here
        # self.isPacman = offense or defense

        # You can profile your evaluation time by uncommenting these lines
        # start = time.time()

        values = [self.evaluate(gameState, a) for a in actions]

        if self.index == 1:
            print(values, file=sys.stderr)
            # print(self.getPreviousObservation(), file=sys.stderr)
        # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        # if self.index == 1:
        #   print(bestActions, file=sys.stderr)

        foodLeft = len(self.getFood(gameState).asList())

        # Prioritizes returning if under winning condition or if you have lots of food
        if foodLeft <= 2 or gameState.getAgentState(self.index).numCarrying > 5:
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

    def getEnemyPacmans(self, successor):
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() is not None]
        return invaders

    def getEnemyGhosts(self, successor):
        # Gets future states of all opponents
        opp_fut_state = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        # Only lists ghosts
        chasers = [p for p in opp_fut_state if p.getPosition() is not None and not p.isPacman]
        return chasers


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
        # Determine if the enemy is closer to you than they were last time,
        # and you are in their territory.
        # Note: This behavior isn't perfect, and can force Pacman to cower
        # in a corner.  I leave it up to you to improve this behavior.
        close_dist = 9999.0
        if self.index == 1 and gameState.getAgentState(self.index).isPacman:
            chasers = self.getEnemyGhosts(successor)

            features['nearbyEnemies'] = len(chasers)
            # TODO: Find distance from power capsule, decide if viable (within 2.5 moves)
            #  (2.5 moves is because
            #  pacmen move at half speed, enemy detection is at 5 spaces, so any visible enemies will catch up in ~
            #  2.5 moves)

            # Finds the closest opponent in range
            if len(chasers) > 0:
                # Measures distance from agent to each enemy, minimum of those
                close_dist = min([float(self.getMazeDistance(myPos, c.getPosition())) for c in chasers])

            # View the action and close distance information for each
            # possible move choice.
            print("Action: " + str(action))
            print("\t\t" + str(close_dist), sys.stderr)

        features['fleeEnemy'] = 1.0 / close_dist  # TODO: why flee and not closest enemy?
        ''' --------------------------- '''

        ''' FOOD FEATURE '''
        foodList = self.getFood(successor).asList()
        # Compute distance to the nearest food
        if len(foodList) > 0:  # This should always be True,  but better safe than sorry
            # Gets location on board
            myPos = successor.getAgentState(self.index).getPosition()
            # Minimum of distances to each food
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance
        # Head to most food-dense area
        # TODO - add function to calculate food density - probably put in getActions
        ''' --------------------------- '''

        ''' SCORE FEATURE '''
        features['successorScore'] = -len(foodList)  # self.getScore(successor)
        ''' --------------------------- '''

        ''' ENEMY AREA FEATURE '''
        # If the enemy is in the top half, then go for bottom half
        # TODO: Add enemy area function - go to opposite area
        ''' --------------------------- '''

        ''' NUM OF AVAILABLE ACTIONS FEATURE '''
        # If available actions is <= 2, reverse regardless of whether an enemy is there or not (will save time)
        # (Implication is that you are in a dead end -- one move is STOP, another is return the way you entered)
        # (Also, implication is that if you entered the dead end, possible to get stuck - reverse, return, reverse...)
        # TODO
        ''' --------------------------- '''

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

        ''' DEFENSE FEATURE '''
        # Computes whether we're on defense (1) or offense (0)
        # Keeps Agent in Base
        features['onDefense'] = 1
        if myState.isPacman:
            features['onDefense'] = 0
        ''' --------------------------- '''

        ''' CLOSEST/AMOUNT OF ENEMY/IES FEATURES '''
        # Computes distance to invaders we can see
        invaders = self.getEnemyPacmans(successor)
        features['numInvaders'] = len(invaders)

        if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)
        ''' --------------------------- '''

        ''' POTENTIAL ENEMY LOCATION/ENTRY FEATURE '''
        # TODO
        ''' --------------------------- '''

        ''' CLOSEST/DENSITY OF FOOD FEATURE '''
        # Guard food from enemies if possible
        # TODO
        ''' --------------------------- '''

        ''' POWER PILL DISTANCE '''
        # Keep enemies away from the power pill if possible, or get them to use it early on
        # TODO
        ''' --------------------------- '''

        ''' SCORE FEATURE '''
        # Option to either go on full offensive, pull back offensive agent, or leave it and attempt to take on enemy
        # (with higher food?)
        # TODO
        ''' --------------------------- '''

        ''' AVAILABLE ACTIONS FEATURE '''

        ''' --------------------------- '''

        ''' STOP/REVERSE FEATURES '''  # TODO: just keeps defender in place...
        if action == Directions.STOP:
            features['stop'] = 1
        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        if action == rev:
            features['reverse'] = 1
        ''' --------------------------- '''

        return features

    def getWeights(self, gameState, action):
        return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}

