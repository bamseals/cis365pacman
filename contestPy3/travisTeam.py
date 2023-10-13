from captureAgents import CaptureAgent
from game import Directions, Actions
from util import nearestPoint
from queue import PriorityQueue


class ReflexCaptureAgent(CaptureAgent):
    def findPathToClosestFood(self, gameState):
        def dijkstra(graph, start):
            distances = {node: float('inf') for node in graph}
            distances[start] = 0
            queue = PriorityQueue()
            queue.put((0, start))

            while not queue.empty():
                current_distance, current_node = queue.get()

                if current_distance > distances[current_node]:
                    continue

                for neighbor, weight in graph[current_node].items():
                    distance = current_distance + weight

                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        queue.put((distance, neighbor))

            return distances

        # Build a graph representing the game state
        graph = {}
        walls = gameState.getWalls()
        for x in range(walls.width):
            for y in range(walls.height):
                if not walls[x][y]:
                    neighbors = {}
                    for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
                        dx, dy = Actions.directionToVector(action)
                        next_x, next_y = int(x + dx), int(y + dy)
                        if not walls[next_x][next_y]:
                            neighbors[(next_x, next_y)] = 1
                    graph[(x, y)] = neighbors

        myPos = gameState.getAgentPosition(self.index)
        foodList = self.getFood(gameState).asList()
        targetFood = min(foodList, key=lambda x: self.getMazeDistance(myPos, x))

        # Run Dijkstra's algorithm to find the shortest path to the target food
        distances = dijkstra(graph, myPos)
        path = []

        while targetFood != myPos:
            for next_x, next_y in graph[targetFood]:
                if distances[targetFood] - distances[(next_x, next_y)] == 1:
                    action = Actions.vectorToDirection((next_x - targetFood[0], next_y - targetFood[1]))
                    path.append(action)
                    targetFood = (next_x, next_y)

        if path:
            return path[0]
        else:
            return Directions.STOP

    def explore(self, gameState):
        print("Entering explore function")
        def getValidNeighbors(position, visited):
            valid_neighbors = []
            x, y = position
            for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
                dx, dy = Actions.directionToVector(action)
                next_x, next_y = int(x + dx), int(y + dy)
                if not visited[next_x][next_y]:
                    valid_neighbors.append((next_x, next_y))
            return valid_neighbors

        def bfs(starting_position):
            visited = [[False for _ in range(gameState.data.layout.width)] for _ in range(gameState.data.layout.height)]
            queue = [(starting_position, [])]
            while queue:
                current_position, path = queue.pop(0)
                if not visited[current_position[0]][current_position[1]]:
                    visited[current_position[0]][current_position[1]] = True
                    if gameState.data.layout.isWall(current_position[0], current_position[1]):
                        continue  # Don't explore walls
                    if not gameState.data.layout.isFood(current_position[0], current_position[1]):
                        return path  # Return the first non-food path found
                    for neighbor in getValidNeighbors(current_position, visited):
                        queue.append((neighbor, path + [neighbor]))

        myPos = gameState.getAgentPosition(self.index)
        print("Current Position:", myPos)  # Debug print
        path = bfs(myPos)

        if path:
            next_position = path[0]
            dx, dy = next_position[0] - myPos[0], next_position[1] - myPos[1]
            print("Next Position:", next_position)  # Debug print
            return Actions.vectorToDirection((dx, dy))

        # Handle the case where there's no path found (e.g., continue in the current direction)
        current_direction = gameState.getAgentState(self.index).configuration.direction
        print("Current Direction:", current_direction)  # Debug print
        return current_direction

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


def createTeam(firstIndex, secondIndex, isRed,
               first='ReflexCaptureAgent', second='ReflexCaptureAgent'):
    return [eval(first)(firstIndex), eval(second)(secondIndex)]
