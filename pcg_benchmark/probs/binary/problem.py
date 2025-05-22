from pcg_benchmark.probs import Problem
from pcg_benchmark.spaces import ArraySpace, IntegerSpace, DictionarySpace
from pcg_benchmark.probs.utils import get_longest_path_and_coords, get_range_reward, get_number_regions, get_longest_path
import numpy as np
from PIL import Image
from pprint import pprint
import os

from PIL import ImageDraw
from enum import IntEnum

class Tile(IntEnum):
    EMPTY = 0
    WALL = 1

class BinaryProblem(Problem):
    def __init__(self, **kwargs):
        Problem.__init__(self, **kwargs)
        self._width = kwargs.get("width")
        self._height = kwargs.get("height")
        self._target = kwargs.get("path", self._width + self._height)
        self._diversity = kwargs.get("diversity", 0.4)

        self._cerror = max(int(self._target * 0.25), 1)
        self._content_space = ArraySpace((self._height, self._width), IntegerSpace(2))
        self._control_space = DictionarySpace({"path": IntegerSpace(self._target + self._cerror, int(self._width * self._height / 2))})
        

    def info(self, content):
        content = np.array(content)
        number_regions = get_number_regions(content, [Tile.EMPTY])
        # longest = get_longest_path(content, [Tile.EMPTY])
        longest, d_map = get_longest_path_and_coords(content, [Tile.EMPTY])

        return {"path": longest, 
                "regions": number_regions, 
                "flat": content.flatten(),
                "d_map": d_map,}

    def quality(self, info):
        number_regions = get_range_reward(info["regions"], 0, 1, 1, self._width * self._height / 10)
        longest = get_range_reward(info["path"], 0, self._target, self._width * self._height)
        return (number_regions + longest) / 2
    
    def diversity(self, info1, info2):
        hamming = abs(info1["flat"] - info2["flat"]).sum()
        return get_range_reward(hamming, 0, self._diversity * self._width * self._height, self._width * self._height)
    
    def controlability(self, info, control):
        longest = get_range_reward(info["path"], 0, control["path"]-self._cerror, control["path"]+self._cerror, self._width * self._height)
        return longest
    

    def render(self, content, info=None):
        scale = 16
        graphics = [
            Image.open(os.path.join(os.path.dirname(__file__), "images/empty.png")).convert('RGBA'),  # enum 0 empty
            Image.open(os.path.join(os.path.dirname(__file__), "images/solid.png")).convert('RGBA'),  # enum 1 wall
            Image.open(os.path.join(os.path.dirname(__file__), "images/path.png")).convert('RGBA'),   # enum 2 path
            Image.open(os.path.join(os.path.dirname(__file__), "images/solid.png")).convert('RGBA'),  # enum 3 border
        ]
        # Use constant_values=3 to pad with border tiles instead of empty tiles
        lvl = np.pad(np.array(content), 1, constant_values=3)
        lvl_image = Image.new("RGBA", (lvl.shape[1]*scale, lvl.shape[0]*scale), (0,0,0,255))
        for y in range(lvl.shape[0]):
            for x in range(lvl.shape[1]):
                tile_idx = lvl[y][x]
                lvl_image.paste(graphics[tile_idx], (x*scale, y*scale, (x+1)*scale, (y+1)*scale))

        # lvl_image.save('level0debug.png') 
        if info:
            d_map = info["d_map"]
            path_coords = get_path_coords(d_map)

            for coord in path_coords:
                y, x = coord
                # Add +1 to both coordinates to account for the padding offset
                lvl_image.paste(graphics[2], ((x+1)*scale, (y+1)*scale, (x+2)*scale, (y+2)*scale))
        # lvl_image.save('leveldebug.png')
        # breakpoint()
        return lvl_image

def get_path_coords(arr):
    """
    Backtrack from the maximum value in the dijkstra map to 0,
    following the descending path.
    """
    # Find the maximum value and its position
    max_val = np.max(arr)
    max_positions = np.argwhere(arr == max_val)
    
    if len(max_positions) == 0:
        raise ValueError("No maximum value found in the array!")
    
    # If multiple max positions, take the first one
    max_pos = tuple(max_positions[0])
    
    path = [max_pos]
    current = max_pos
    current_val = max_val

    # Backtrack from max_val down to 0
    while current_val > 0:
        y, x = current
        found_next = False
        
        # Check 4-neighbors (up, down, left, right)
        for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
            ny, nx = y + dy, x + dx
            
            # Check bounds
            if 0 <= ny < arr.shape[0] and 0 <= nx < arr.shape[1]:
                neighbor_val = arr[ny, nx]
                
                # Look for the neighbor with value current_val - 1
                if neighbor_val == current_val - 1:
                    current = (ny, nx)
                    path.append(current)
                    current_val -= 1
                    found_next = True
                    break
        
        if not found_next:
            print(f"Warning: No valid neighbor found at position {current} with value {current_val}")
            print(f"Neighbors: {[(y+dy, x+dx, arr[y+dy, x+dx] if 0 <= y+dy < arr.shape[0] and 0 <= x+dx < arr.shape[1] else 'OOB') for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]]}")
            break
    
    return path