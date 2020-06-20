import os
import random

import cherrypy

"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""


class Battlesnake(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # This function is called when you register your Battlesnake on play.battlesnake.com
        # It controls your Battlesnake appearance and author permissions.
        # TIP: If you open your Battlesnake URL in browser you should see this data
        return {
            "apiversion": "1",
            "author": "",  # TODO: Your Battlesnake Username
            "color": "#5e34eb",  # TODO: Personalize
            "head": "default",  # TODO: Personalize
            "tail": "default",  # TODO: Personalize
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        # TODO: Use this function to decide how your snake is going to look on the board.
        data = cherrypy.request.json

        print("START")
        return "ok"

    def move_to_square(self, head, direction):
        if direction == "right":
            return (head[0] + 1, head[1])
        if direction == "left":
            return (head[0] - 1, head[1])
        if direction == "up":
            return (head[0], head[1] + 1)
        if direction == "down":
            return (head[0], head[1] - 1)

        print("what the fuck was this:", head, direction)
        return (0,0)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        # TODO: Use the information in cherrypy.request.json to decide your next move.
        data = cherrypy.request.json
        #print(data)

        # Choose a random direction to move in
        possible_moves = []
        head = data['you']['head']
        board = data['board']
        bodies = set()
        for snake in board['snakes']:
            for square in snake['body'][:-1]: # no tail or other snake heads
                bodies.add((square['x'], square['y']))
            if len(snake['body']) < 3 or snake['health'] == 100:
                bodies.add((snake['body'][-1]['x'], snake['body'][-1]['y']))

        moves = {"left": 0, "right": 0, "up": 0, "down": 0}

        if head['x'] > 0 and (head['x']-1, head['y']) not in bodies:
            moves["left"] = 100
        if head['y'] > 0 and (head['x'], head['y']-1) not in bodies:
            moves["down"] = 100
        if head['x'] < board['width'] - 1 and (head['x']+1, head['y']) not in bodies:
            moves["right"] = 100
        if head['y'] < board['height'] - 1 and (head['x'], head['y']+1) not in bodies:
            moves["up"] = 100

        for snake in board['snakes']:
            s_x = snake['head']['x']
            s_y = snake['head']['y']
            h_x = head['x']
            h_y = head['y']
            s_len = snake['length']
            h_len = data['you']['length']

            if h_x - 2 == s_x and h_y == s_y:
                if s_len >= h_len:
                    moves["left"] /= 16.0
                else:
                    moves["left"] *= 4
            elif h_x + 2 == s_x and h_y == s_y:
                if s_len >= h_len:
                    moves["right"] /= 16.0
                else:
                    moves["right"] *= 4
            elif h_x == s_x and h_y - 2 == s_y:
                if s_len >= h_len:
                    moves["down"] /= 16.0
                else:
                    moves["down"] *= 4
            elif h_x == s_x and h_y + 2 == s_y:
                if s_len >= h_len:
                    moves["up"] /= 16.0
                else:
                    moves["up"] *= 4
            elif h_x - 1 == s_x and h_y - 1 == s_y:
                if s_len >= h_len:
                    moves["left"] /= 8.0
                    moves["down"] /= 8.0
                else:
                    moves["left"] *= 2
                    moves["down"] *= 2
            elif h_x + 1 == s_x and h_y + 1 == s_y:
                if s_len >= h_len:
                    moves["right"] /= 8.0
                    moves["up"] /= 8.0
                else:
                    moves["right"] *= 2
                    moves["up"] *= 2
            elif h_x - 1 == s_x and h_y + 1 == s_y:
                if s_len >= h_len:
                    moves["left"] /= 8.0
                    moves["up"] /= 8.0
                else:
                    moves["left"] *= 2
                    moves["up"] *= 2
            elif h_x + 1 == s_x and h_y - 1 == s_y:
                if s_len >= h_len:
                    moves["right"] /= 8.0
                    moves["down"] /= 8.0
                else:
                    moves["right"] *= 2
                    moves["down"] *= 2

        food = set()
        for square in board['food']:
            food.add((square['x'], square['y']))

        # if one is food eat it
        for direction in moves:
            if self.move_to_square((head['x'], head['y']), direction) in food:
                moves[direction] *= (1 + ((100 - data['you']['health'])/50.0))

        # when hungry, move towards non competing food

        # Flood fill board
        # Add axtra heads to other snakes to avoid collision
        # Determine: food or tail?

        for direction in moves:
            if moves[direction] == 0:
                continue
            score = 0
            floodfill = [[1000 for i in range(board['height'])] for j in range(board['width'])]
            starting_point = self.move_to_square((head['x'], head['y']), direction)
            floodfill[starting_point[0]][starting_point[1]] = 0
            todo = [starting_point]
            while len(todo) >= 1:
                curr = todo.pop(0)
                if curr in bodies or curr[0] < 0 or curr[0] > board['width'] - 1 or curr[1] < 0 or curr[1] > board['height'] - 1 or (floodfill[curr[0]][curr[1]] != 1000 and floodfill[curr[0]][curr[1]] != 0):
                    continue
                todo += [self.move_to_square(curr, "left"), self.move_to_square(curr, "right"), self.move_to_square(curr, "up"), self.move_to_square(curr, "down")]
                if floodfill[curr[0]][curr[1]] == 0:
                    score += 0.01
                    continue

                if curr[0] > 0:
                    floodfill[curr[0]][curr[1]] = min(floodfill[curr[0]][curr[1]], floodfill[curr[0] - 1][curr[1]] + 1)
                if curr[0] < board['width'] - 1:
                    floodfill[curr[0]][curr[1]] = min(floodfill[curr[0]][curr[1]], floodfill[curr[0] + 1][curr[1]] + 1)
                if curr[1] > 0:
                    floodfill[curr[0]][curr[1]] = min(floodfill[curr[0]][curr[1]], floodfill[curr[0]][curr[1] - 1] + 1)
                if curr[1] < board['height'] - 1:
                    floodfill[curr[0]][curr[1]] = min(floodfill[curr[0]][curr[1]], floodfill[curr[0]][curr[1] + 1] + 1)

                for snake in board['snakes']:
                    if snake["id"] == data['you']["id"]:
                        continue
                    if snake["length"] >= data['you']["length"]:
                        if abs(curr[0] - snake['head']['x']) + abs(curr[1] - snake['head']['y']) <= 2:
                            score -= 2.0/(1+floodfill[curr[0]][curr[1]])
                    else:
                        if abs(curr[0] - snake['head']['x']) + abs(curr[1] - snake['head']['y']) <= 2:
                            score += 0.5/(1+floodfill[curr[0]][curr[1]])

                if curr in food:
                    score += (1.0 + ((100 - data['you']['health'])/50.0))/(1+floodfill[curr[0]][curr[1]])
                else:
                    score += 1.0/(1+floodfill[curr[0]][curr[1]])
            moves[direction] *= score

        print(data['game']['turn'], moves)
        return {"move": max(moves, key=moves.get)}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json

        print("END")
        return "ok"


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
