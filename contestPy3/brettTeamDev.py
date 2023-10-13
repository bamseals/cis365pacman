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
               first='OffensiveReflexAgent', second='OffensiveReflexAgent'):
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

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""                                                   """
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
'''THIS FILE IS NOT IN ANY WAY A MAJOR SUBMISSION FILE. THIS IS A VARIATION OF THE TEAMCIS457_FINAL_BOT WITH TODOs 
AND FIXMEs USED FOR DEVELOPMENT AND KEEPING TRACK OF WHAT CAN BE DONE STILL
please dont grade us harshly cause this is messy with comments, this file is basically just for my reference
'''
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""                                                   """
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""

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

        #if self.index == 1:
        print(values, file=sys.stderr)
            # print(self.getPreviousObservation(), file=sys.stderr)

        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        # if self.index == 1: # This line prints only the first blue agent's information
            # print(bestActions, file=sys.stderr)

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

        #  if self.index == 1: # This line prints only the first blue agent's information
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
        if len(self.getCapsules(gameState)) > 0:
            PC = self.getCapsules(gameState)[0]
            myPos = gameState.getAgentState(self.index).getPosition()
            return self.getMazeDistance(myPos, PC)
        else:
            return -1

    def estEnemyDist(self, gameState):
        """
        Finds the noisy distances for each opponent and states whether they are pacmen or not
        """
        enemies = self.getOpponents(gameState)
        enem1 = gameState.getAgentState(enemies[0])
        enem2 = gameState.getAgentState(enemies[1])

        noisedistances = gameState.getAgentDistances()

        data = [[enem1.isPacman, noisedistances[enemies[0]], enemies[0]],
                [enem2.isPacman, noisedistances[enemies[0]], enemies[1]]]

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
        foodList = self.getFood(successor).asList()

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
            # TODO - optimize notInWay - currently less linear blocking, more just whether the enemy is closer
            # ex. way home could be wide open, but agent doesn't take it because a pacman is on
            # the border
            notInWay = (self.getMazeDistance(chasers[0].getPosition(), self.start) >
                        self.getMazeDistance(myPos, self.start))
            if successor.getAgentState(self.index).isPacman:  # and notInWay:
                # RUN HOME
                if close_dist < 5:  # TODO adjust for if enemy is pacman - flee towards
                    features['fleeHome'] = self.getMazeDistance(myPos, self.start)
            elif not successor.getAgentState(self.index).isPacman:  # and notInWay:
                # If you are a ghost, you are only in danger if you cross the border
                if(self.index == 0 or self.index == 2):
                    if action == Directions.WEST and close_dist < 4:  # TODO adjust for if enemy is pacman - kill
                        # TODO move one more away first to prevent deadlocks
                        features['settle'] = 1
                elif (self.index == 1 or self.index == 3):
                        if action == Directions.EAST and close_dist < 4:
                            features['settle'] = 1
                    # features['fleeEnemy'] = 1.0 / close_dist
                #if action == Directions.EAST and (self.index == 0 or self.index == 2):
                #    features['settle'] = -1
                #elif action == Directions.WEST and (self.index == 1 or self.index == 3):
                #    features['settle'] = -1
            # elif successor.getAgentState(self.index).isPacman and not notInWay:
                # TODO if notInWay is fixed, this is viable
            #    features['fleeEnemy'] = 1.0 / close_dist
            elif not successor.getAgentState(self.index).isPacman and not notInWay:
                # Their turn to run, now.
                features['defend'] = close_dist
            
            # Calculate distance to the Power Capsule for leverage against enemies
            distToPC = self.getDistToPC(successor)
            if len(chasers) > 1 and distToPC < close_dist:
                features['PCDistance'] = distToPC  # TODO Use this

        # View the action and close distance information for each
        # possible move choice.
        print("Action: " + str(action))
        print("\t\t" + str(close_dist), sys.stderr)
        ''' ----END OF FEATURE---- '''

        ''' FOOD FEATURE '''
        # Compute distance to the nearest food
        if len(foodList) > 0:
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance

        # Head to most food-dense area
        features['denseFoodDist'] = self.getDensestFoodDistance(successor)  # TODO - actually make this functional
        # - 218 base val
        ''' ----END OF FEATURE---- '''

        ''' SCORE FEATURE '''
        features['successorScore'] = -len(foodList)
        ''' ----END OF FEATURE---- '''

        ''' ENEMY AREA FEATURE '''
        # If the enemy is in the top half, then go for bottom half
        # TODO: Add enemy area function - go to opposite area
        # print(self.estEnemyDist(gameState))
        ''' ----END OF FEATURE---- '''

        ''' NUM OF AVAILABLE ACTIONS FEATURE '''
        # If available actions is <= 2, reverse regardless of whether an enemy is there or not (will save time)
        # (Implication is that you are in a dead end -- one move is STOP, another is return the way you entered)
        # (Also, implication is that if you entered the dead end, possible to get stuck - reverse, return, reverse...)
        # TODO
        ''' ----END OF FEATURE---- '''

        return features

    def getWeights(self, gameState, action):
        return {'successorScore': 100, 'distanceToFood': -1, 'fleeEnemy': -100.0, 'fleeHome': -100,
                'defend': -1000, 'settle': 1000} #FIXME changes defend from -100 to -1000


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

        # TODO Noise means these dont always change between moves. TL;DR no effect

        # Maps estimated enemy distances to features
        # Allows defending ghost to 'track' enemies down
        if(enemyinfo[0][0] == True):
            features['enemyADistance'] = -enemyinfo[0][1]*10  # TODO optimize #TODO possiblity for null if enemy dies
        elif enemyinfo[0][0] == False:
            features['enemyADistance'] = -enemyinfo[0][1]
        if (enemyinfo[1][0] == True):
            features['enemyBDistance'] = -enemyinfo[1][1]*10
        elif enemyinfo[1][0] == False:
            features['enemyBDistance'] = -enemyinfo[1][1]

        if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)
        ''' ----END OF FEATURE---- '''

        ''' CLOSEST/DENSITY OF FOOD FEATURE '''
        # Move agent toward other side (LOW PRIORITY)
        # Essentially camps the food closest to enemy side, by focusing on its reflection.
        foodList = self.getFood(successor).asList()
        # Compute distance to the nearest food
        if len(foodList) > 0:  # This should always be True,  but better safe than sorry
            # Gets location on board
            myPos = successor.getAgentState(self.index).getPosition()
            # Minimum of distances to each food
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance

        # Guard food from enemies
        # TODO
        ''' ----END OF FEATURE---- '''

        ''' POWER PILL DISTANCE '''
        # Keep enemies away from the power pill if possible, or get them to use it early on
        # TODO
        ''' ----END OF FEATURE---- '''

        ''' SCORE FEATURE '''
        # Option to either go on full offensive, pull back offensive agent, or leave it and attempt to take on enemy
        # (with higher food?)
        # TODO
        ''' ----END OF FEATURE---- '''

        ''' AVAILABLE ACTIONS FEATURE '''

        ''' ----END OF FEATURE---- '''

        ''' STOP/REVERSE FEATURES '''  # TODO: keeps defender moving unless there is an invader
        if action == Directions.STOP:
            features['stop'] = 1
        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        if action == rev:
            features['reverse'] = 0  # TODO changed this from a 1 to a 0 for testing
        ''' ----END OF FEATURE---- '''

        return features

    def getWeights(self, gameState, action):
        # TODO: set weight for enemy pacman to be higher than enemy ghost - chase pacman b4 ghost
        return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'enemyADistance': 1,
                'enemyBDistance': 1, 'distanceToFood': -1, 'stop': -100, 'reverse': -2}

