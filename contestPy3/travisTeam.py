from captureAgents import CaptureAgent
from game import Directions, Actions
from util import nearestPoint

class ReflexCaptureAgent(CaptureAgent):
    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        myState = gameState.getAgentState(self.index)
        myPos = myState.getPosition()
        foodList = self.getFood(gameState).asList()

        if not self.red:
            return self.offensiveStrategy(gameState)
        else:
            return self.defensiveStrategy(gameState)

    def offensiveStrategy(self, gameState):
        actions = gameState.getLegalActions(self.index)
        myState = gameState.getAgentState(self.index)
        myPos = myState.getPosition()
        foodList = self.getFood(gameState).asList()

        # Strategy: Seek food
        if len(foodList) > 0:
            action = self.findPathToClosestFood(gameState)
        else:
            action = self.explore(gameState)

        return action

    def defensiveStrategy(self, gameState):
        actions = gameState.getLegalActions(self.index)
        myState = gameState.getAgentState(self.index)
        myPos = myState.getPosition()

        # Strategy: Defend the base
        action = self.patrolBase(gameState)
        return action


def findPathToClosestFood(self, gameState):
    from util import Queue
    queue = Queue()
    startState = gameState.getAgentState(self.index)
    startPos = gameState.getAgentPosition(self.index)
    foodList = self.getFood(gameState).asList()
    targetFood = min(foodList, key=lambda x: self.getMazeDistance(startPos, x))
    queue.push((startPos, []))  # Queue stores position and actions
    visited = set()

    while not queue.isEmpty():
        pos, actions = queue.pop()
        if pos == targetFood:
            if actions:
                return actions[0]  # Return the first action to get to the closest food
            else:
                return Directions.STOP

        for action in gameState.getLegalActions(self.index):
            successor = Actions.getSuccessor(pos, action)
            if successor not in visited:
                queue.push((successor, actions + [action]))
                visited.add(successor)

    # If no path is found, return STOP
    return Directions.STOP

def findPathToClosestFood(self, gameState):
    from util import Queue
    queue = Queue()
    startState = gameState.getAgentState(self.index)
    startPos = gameState.getAgentPosition(self.index)
    foodList = self.getFood(gameState).asList()
    targetFood = min(foodList, key=lambda x: self.getMazeDistance(startPos, x))
    queue.push((startPos, []))  # Queue stores position and actions
    visited = set()

    while not queue.isEmpty():
        pos, actions = queue.pop()
        if pos == targetFood:
            if actions:
                return actions[0]  # Return the first action to get to the closest food
            else:
                return Directions.STOP

        for action in gameState.getLegalActions(self.index):
            successor = Actions.getSuccessor(pos, action)
            if successor not in visited:
                queue.push((successor, actions + [action]))
                visited.add(successor)

    # If no path is found, return STOP
    return Directions.STOP

def explore(self, gameState):
    # Basic exploration strategy: choose a random legal action
    actions = gameState.getLegalActions(self.index)
    return random.choice(actions)

def patrolBase(self, gameState):
    # Basic defensive strategy: move between two predefined positions
    if gameState.isOnRedTeam(self.index):
        positions = [(10, 5), (10, 6)]  # Example positions for red team
    else:
        positions = [(17, 6), (17, 5)]  # Example positions for blue team

    if self.patrolTarget == positions[0]:
        self.patrolTarget = positions[1]
    else:
        self.patrolTarget = positions[0]

    return self.findPathToClosestFood(gameState)

def explore(self, gameState):
    # Basic exploration strategy: choose a random legal action
    actions = gameState.getLegalActions(self.index)
    return random.choice(actions)


def patrolBase(self, gameState):
    # Basic defensive strategy: move between two predefined positions
    if gameState.isOnRedTeam(self.index):
        positions = [(10, 5), (10, 6)]  # Example positions for red team
    else:
        positions = [(17, 6), (17, 5)]  # Example positions for blue team

    if self.patrolTarget == positions[0]:
        self.patrolTarget = positions[1]
    else:
        self.patrolTarget = positions[0]

    return self.findPathToClosestFood(gameState)


def createTeam(firstIndex, secondIndex, isRed,
               first='ReflexCaptureAgent', second='ReflexCaptureAgent'):
    return [eval(first)(firstIndex), eval(second)(secondIndex)]
