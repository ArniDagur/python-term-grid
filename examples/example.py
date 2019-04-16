from column import Column
from grid import Grid

def print_top2bottom(items):
    grid = Grid(items)
    lines = grid.create_lines(40)
    for line in lines:
        print(line)

def print_left2right(items):
    grid = Grid(items, direction='left2right')
    lines = grid.create_lines(40)
    for line in lines:
        print(line)

if __name__ == '__main__':
    items = ['january', 'febuary', 'march', 'april', 'may', 'june', 'july',
             'august', 'september', 'october', 'november', 'december']

    print_left2right(items)
    print()
    print_top2bottom(items)
