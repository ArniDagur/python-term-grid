# Python Term Grid

## Usage
```python
from termgrid import Grid

# Items 
items = ['january', 'febuary', 'march', 'april', 'may', 'june', 'july',
         'august', 'september', 'october', 'november', 'december']

# Create grid
grid = Grid(items, seperator=' | ', margins=('-> ', ' <-'), direction='left2right')

# Fit grid into 40 horizontal cells and print to stdout
lines = grid.create_lines(40)
for line in lines:
    print(line)
```
Output:
```
-> january | febuary  | march <-
-> april   | may      | june <-
-> july    | august   | september <-
-> october | november | december <-
```

## Installation
```bash
python setup.py install --optimize=1
```
