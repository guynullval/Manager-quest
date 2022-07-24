from __future__ import annotations
from abc import ABC, abstractmethod
import pygame
import pprint
from pygame.locals import *
import numpy
from collections.abc import Callable
from functools import reduce, cache
import json
from dataclasses import dataclass

CELLSIZE = 32
FONTFILE = "terminal8x8_gs_ro.png"

class FileLoader():
    _fontimage : pygame.Surface
    def __init__(self, filename : str):
        self._fontimage = pygame.image.load("terminal8x8_gs_ro.png")
        self._fontimage.set_colorkey((0,0,0))

    def GetTileSet(self):
        pass

class TileSheet:
    _tiles = [pygame.Surface]
    def __init__(self,
                 file : pygame.Surface,
                 width : int,
                 height : int,
                 rows : int,
                 columns : int):
        for x in range(rows):
            for y in range(columns):
                self._tiles.append(
                    pygame.transform.scale(
                        file.subsurface(y * width, x * height, width, height),
                        (CELLSIZE, CELLSIZE)
                    )
                )

class Window():
    _size = (int, int)
    _surface = pygame.Surface
    def __init__(self, width, height) -> None:
        self._surface = pygame.display.set_mode((width, height), 0, 32)

        
    def surface(self) -> pygame.Surface:
        return self._surface

class View:
    _camera : pygame.Rect
    _trackingObject = None
    def __init__(self,
                 topx : int,
                 topy : int,
                 cameraWidth : int,
                 cameraHeight : int,
                 trackingObject = None):
        self._camera = pygame.Rect(topx, topy, topx+cameraWidth, topycameraHeight)
        if trackingObject is not None:
            self._trackingObject = trackingObject

    def slice(self, surface : pygame.Surface):
        return surface.Subsurface(self._camera)

    def trackObject(self, surface : pygame.Surface):
        pass

    def checkCenterObject(self):
        pass

    def update(self) -> pygame.Surface:
        pass

def drawMap(map : str,
            pos : [(int, int)],
            tiles : [pygame.Surface],
            destination :pygame.Surface):
    _drawingList : [(pygame.Surface,(int,int))] = []
    x = 0
    y = 0
    for ind, c in enumerate(map):
        _drawingList.append((tiles[ord(c)+1], pos[ind]))
    destination.blits(_drawingList)

def drawing(chars : str,
            pos : [(int, int)],
            tiles : [pygame.Surface],
            destination :pygame.Surface):
    _drawingList : [(pygame.Surface,(int,int))] = []
    x = 0
    y = 0
    for ind, c in enumerate(chars):
        _drawingList.append((tiles[ord(c)+1], pos[ind]))
    destination.blits(_drawingList)

class Map:
    _str : str
    _pos : [(int,int)] = []
    _map : pygame.Surface
    def __init__(self, tiles):
        # TEMP map
        self._str = ""
        tempMap = [ "################################",
                    "#       #             #        #",
                    "#       #             #        #",
                    "#       #             #        #",
                    "#       #             #        #",
                    "#                              #",
                    "#                              #",
                    "#           y                  #",
                    "#      Hello                   #",
                    "#       p                      #",
                    "#                              #",
                    "#                              #",
                    "#                              #",
                    "#                              #",
                    "#                              #",
                    "################################"
        ]
        w = len(tempMap[0]) * CELLSIZE
        h = len(tempMap) * CELLSIZE
        self._map = pygame.Surface((w, h))
        
        for i, s in enumerate(tempMap):
            self._str = self._str + s
            for string_i, _ in enumerate(s):
                self._pos.append((string_i*CELLSIZE, i*CELLSIZE))
        drawMap(self._str, self._pos, tiles, self._map)

    def map(self):
        return self._map

def GameLoop(window, map, tiles):
    running = True
    player = Player((32,32), (32,32), '@')
    movVec = (0,0)
    currVec = player.xy()
    nxtVec = player._xy()
    while(out):
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.KEYDOWN:
                    movVec = getInput(event)
        if player.arrived():
            nxtVec = tuple(map(lambda n, _n: n + ( _n * CELLSIZE), nxtVec, movVec))           
        currVec = move(player.xy(), nxtVec)
        player = Player(currVec, nxtVec, '@')
        window.surface().blit(map.map(), (0,0))
        drawing(player._char(), [player.xy()], tiles._tiles, window.surface())
        pygame.display.flip()
    pprint.pprint(str(player.xy()) + ", " + str(player._xy()))
    #pprint.pprint(map._pos)
        # Run game

@dataclass(frozen=True)
class Player:
    xy : (int, int)
    _xy : (int, int)
    _c : chr

    def arrived(self) -> bool:
        return self.xy() == self._xy()

    def xy(self):
        return self.xy

    def _xy(self):
        return self._xy

    def _char(self):
        return self._c

def getInput(ev):
    inputList = { pygame.K_UP : (0,-1),
                  pygame.K_DOWN : (0,1),
                  pygame.K_LEFT : (-1, 0),
                  pygame.K_RIGHT : (1, 0),
    }
    return inputList.get(ev.key, (0,0))

def move(xy : (int, int), _xy : (int, int)) -> (int, int):
    acc = []
    for n, _n in zip(xy, _xy):
        if n > _n:
            n = n - 1
        elif n < _n:
            n = n + 1
        acc.append(n)
    return tuple(lst)

def main():
    pygame.init()
    pygame.font.init()
    # -------
    _files = FileLoader("terminal8x8_gs_ro.png")
    _tiles = TileSheet(_files._fontimage, 8, 8, 16, 16)
    window = Window(800, 600)
    map = Map(_tiles._tiles)
    GameLoop(window, map, _tiles)
    # -------
    pygame.quit()

if __name__=="__main__":
    main()
