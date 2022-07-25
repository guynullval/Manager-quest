from __future__ import annotations
from abc import ABC, abstractmethod
import pygame
import pprint
from pygame.locals import *
import numpy
from collections.abc import Callable
from functools import reduce, cache, wraps, partial
import json
from dataclasses import dataclass, field
import operator

CELLSIZE = 32
FONTFILE = "terminal8x8_gs_ro.png"

def Cell(cell : (int, int)) -> (int, int):
    return tuple(map(lambda n : n * CELLSIZE, cell))

def collision(xy, _xy):
    return xy == _xy

def move(xy : (int,int), _xy : (int, int)) -> (int, int):
    acc = []
    for n, _n in zip(xy, _xy):
        if n > _n:
            n = n - 2
        elif n < _n:
            n = n + 2
        acc.append(n)
    return tuple(acc)

@dataclass(frozen=True)
class Vector:
    x : int
    y : int
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

def getInput(ev):
    inputList = { pygame.K_UP : (0,-1),
                  pygame.K_DOWN : (0,1),
                  pygame.K_LEFT : (-1, 0),
                  pygame.K_RIGHT : (1, 0),
    }
    return inputList.get(ev.key, (0,0))

def loadFiles() -> ConfigFile:
    _fontImage = pygame.image.load("terminal8x8_gs_ro.png")
    _fontImage.set_colorkey((0,0,0))
    with open('conf.json', 'r') as _file:
        config = json.load(_file)
    return ConfigFile(_fontImage, config)

@dataclass(frozen=True)
class ConfigFile:
    _image : pygame.Surface
    _conf : dict
    def image(self) -> pygame.Surface:
        return self._image
    def config(self) -> dict:
        return self._conf

@dataclass(frozen=True)
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

def View(actor : Actor,
         surface : pygame.Surface,
         view : pygame.Rect) -> pygame.Surface:
    _view = view
    _view.center = actor.currxy()
    return surface.subsurface(_view)

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

def makeActors(amount : int, playerIndex : int) -> [Player]:
    pass

def GameLoop(window, _map, tiles):
    running = True
    player = Actor('@',(32,32), (32,32))
    currVec = player.currxy()
    nxtVec = player.nxtxy()
    log = []
    cl = pygame.time.Clock()
    while(running):
        movVec = (0,0)
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.KEYDOWN:
                    movVec = getInput(event)
        if player.arrived():
            nxtVec = tuple(map(lambda n, _n: n + ( _n * CELLSIZE), nxtVec, movVec))           
        currVec = move(player.currxy(), nxtVec)
        player = Actor( '@',currVec, nxtVec)
        window.surface().blit(_map.map(), (0,0))
        drawing(str(player), [player.currxy()], tiles._tiles, window.surface())
        pygame.display.flip()
        log.append("current vector : " + str(currVec) + "nxtVector : " + str(nxtVec) + "has player arrived: " + str(player.arrived()))
        cl.tick_busy_loop(60)
    pprint.pprint(_map.map())

@dataclass(frozen=True)
class Actor:
    _c : chr = field(init=True)
    xy : (int, int) = field(init=True)
    _xy : (int, int) = field(init=True)
    def arrived(self) -> bool:
        return self.xy == self._xy

    def currxy(self):
        return self.xy

    def nxtxy(self):
        return self._xy

    def __repr__(self):
        return self._c

def updateActor(lstOfActors : [Actor]) -> [Actor]:
    # retLst = []
    # #check collision
    # lstCollision
    # for nxt in lstOfActors:
    #     lstCollision.append(nxt.
    # for actor in lstOfActors:
    #     currVec = move(actor.currxy(), actor.nxtxy())
    pass

def main():
    pygame.init()
    pygame.font.init()
    # -------
    _files = loadFiles()
    _tiles = TileSheet(_files.image(), 8, 8, 16, 16)
    window = Window(800, 600)
    map = Map(_tiles._tiles)
    GameLoop(window, map, _tiles)
    # -------
    pygame.quit()

if __name__=="__main__":
    main()
