<p align="center">
	<img height="300px" src="../../../images/binarydoor/example.png"/>
</p>
<h1 align="center">
Binary Door Problem
</h1>

The binary door problem is a variant of the [binary problem](../binary/README.md) where two door openings are placed in the wall border. The goal is to generate a 2D maze of empty and solid tiles where the two doors are connected through the maze and the path between them meets a target length. Doors are placed deterministically from a seed on non-corner border positions with minimum perimeter separation.

The problem has 1 variant:
- `binarydoor-v0`: generate a maze of size 14x14 (excluding borders) with minimum door path length of 28

## Content Structure
The content is a 2D binary array of **height x width** where 0 is **empty** and 1 is **solid** (same as the binary problem). The doors are part of the border, not the content — the agent only edits the inner grid. Here is an example of a content:
```python
[
    [0,0,0,1,1,1,1,1,1,1,1,1,1,1],
    [0,1,0,0,0,0,0,0,1,1,1,1,1,1],
    [0,1,1,1,1,1,1,0,1,1,1,0,0,0],
    [0,0,0,0,0,1,1,0,1,1,1,0,1,1],
    [1,1,1,1,0,1,1,0,0,0,0,0,1,1],
    [1,1,1,1,0,0,0,0,1,1,1,1,1,1],
    [1,1,0,0,0,1,1,1,1,1,1,1,1,1],
    [1,1,0,1,1,1,1,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,1,1,1,1,1,0],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]
```

## Control Parameter
This is the control parameter of the problem. The control parameter is a dictionary with one parameter called `door_path(int)` where it indicates how long the shortest path between the two doors has to be to pass controllability criteria. Here is an example of the control parameter for 14x14:
```python
{
    "door_path": 50
}
```

## Adding a new Variant
If you want to add new variants for this framework, you can add it to [`__init__.py`](__init__.py) file. To add a new variant please try to follow the following name structure `binarydoor-{variant}-{version}` where `{version}` if first time make sure it is `v0`. The following parameters can be changed to create the variant:
- `width(int)`: the width of the maze
- `height(int)`: the height of the maze
- `door_path(float)`: the target door path length (optional=width+height)
- `door_seed(int)`: seed for deterministic door placement (optional=42)
- `diversity(float)`: the diversity percentage that if you pass it, the diversity value is equal to 1 (optional=0.4)

An easier way without editing the framework files is to use the `register` function from the `pcg_benchmark` to add the variant.
```python
from pcg_benchmark.probs.binarydoor import BinaryDoorProblem
import pcg_benchmark

pcg_benchmark.register('binarydoor-large-v0', BinaryDoorProblem, {"width": 28, "height": 28, "door_path": 56})
```

## Quality Measurement
To pass the quality criteria, you need to pass two criteria:
- have a fully connected map that consists of one region
- have a door-to-door shortest path length that is more than the target `door_path` which is 28 for `binarydoor-v0`

## Diversity Measurement
To pass the diversity criteria, you need the input levels to have at least 40% difference on the hamming distance measuring criteria.

## Controllability Measurement
To pass the controllability criteria, you need the door path length (the shortest path between the two doors) close to the control parameter `door_path` value.

## Content Info
This is all the info that you can get about any content using the `info` function:
- `door_path(int)`: the shortest path length between door1 and door2 through the augmented grid (0 if no path)
- `regions(int)`: the number of connected empty regions in the inner maze
- `flat(int[])`: the maze as a flat 1D binary array
- `d_map(int[][])`: the BFS distance map from door1 on the augmented grid (-1 for unvisited)
- `door1(tuple)`: (row, col) position of the first door in the augmented grid
- `door2(tuple)`: (row, col) position of the second door in the augmented grid
