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

    def square_to_move(self, head, move):
        if move[0] == head["x"] + 1:
            return "left"
        if move[0] == head["x"] - 1:
            return "right"
        if move[1] == head["y"] + 1:
            return "up"
        if move[1] == head["y"] - 1:
            return "down"
        print("what the fuck was this:", head, move)
        return ""

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        # TODO: Use the information in cherrypy.request.json to decide your next move.
        data = cherrypy.request.json

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

        if head['x'] > 0 and (head['x']-1, head['y']) not in bodies:
            # left
            possible_moves += [(head['x']-1, head['y'])]
        if head['y'] > 0 and (head['x'], head['y']-1) not in bodies:
            # up
            possible_moves += [(head['x'], head['y']-1)]
        if head['x'] < board['width'] - 1 and (head['x']+1, head['y']) not in bodies:
            # right
            possible_moves += [(head['x']+1, head['y'])]
        if head['y'] < board['height'] - 1 and (head['x'], head['y']+1) not in bodies:
            # down
            possible_moves += [(head['x'], head['y']+1)]

        """
        for snake in board['snakes']:
            if abs(snake['head']['x'] - head[0]) + abs(snake['head']['y'] - head[1]) == 2:
                if snake['length'] >= data['you']['length']:
                    # run away
                    
                else:
                    # eat it
        """

        food = set()
        for square in board['food']:
            food.add((square['x'], square['y']))

        # if one is food eat it
        for move in possible_moves:
            if move in food:
                print("ate food")
                return {"move": self.square_to_move(head, possible_moves[0])}
        print(possible_moves)
        print(self.square_to_move(head, possible_moves[0]))
        return {"move": self.square_to_move(head, possible_moves[0])}

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
