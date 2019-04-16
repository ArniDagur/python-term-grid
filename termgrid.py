#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: fenc=utf-8:et:ts=4:sts=4:sw=4:fdm=marker

# Algorithm based on https://github.com/ogham/rust-term-grid/ which is MIT
# licensed.

"""
A grid is an mutable datastructure whose items can be printed in a grid in
such a way as to minimize the number of lines.
"""
class Grid(object):
    DEFAULT_MARGIN = ' '

    """
    Arguments:
        items (list): List of strings to put in the grid. 
        seperator (str): String seperating grid columns.
        margins (tuple): A tuple of one or two strings. If length is one,
            both left margin and right margin share the same margin string.
            Otherwise, the first string is the first margin, and the second
            string the right margin.
        direction (str): Either 'top2bottom', or 'left2right'.
    """
    def __init__(self, items: list = [], seperator: str=' ',
                 margins: tuple=(' '), direction: str='top2bottom'):
        self.items = items
        self.seperator = seperator
        self.direction = direction

        if len(margins) == 1:
            self.left_margin = margins[0]
            self.right_margin = margins[0]
        elif len(margins) == 2:
            self.left_margin = margins[0]
            self.right_margin = margins[1]
        else:
            # Invalid margin supplied; ignore it and use the default
            self.left_margin = DEFAULT_MARGIN
            self.right_margin = DEFAULT_MARGIN
        self.margin_width = len(self.left_margin + self.right_margin)

    def __getitem__(self, index):
        return self.items[index]

    def __setitem__(self, index, data):
        self.items[index] = data

    def __delitem__(self, index):
        del self.items[data]

    def __len__(self):
        return len(self.items)

    def _column_widths(self, num_lines: int, num_columns: int) -> dict:
        widths: list = [0] * num_columns # Fill list with zeroes
        for i, item in enumerate(self.items):
            # Set index as column index
            if self.direction == 'top2bottom':
                i //= num_lines
            elif self.direction == 'left2right':
                i %= num_columns
            else:
                raise ValueError("Invalid direction: Must be one of "
                                 "{'top2bottom, 'left2right'}")
            widths[i] = max(widths[i], len(item))
        
        return { 'num_lines': num_lines, 'widths': widths }

    def _get_dimensions_given_num_lines_and_maxwidth(self, max_width, num_lines):
        max_width_without_margins = max_width - self.margin_width
        # The number of columns is the number of cells divided by the number
        # of lines, _rounded up_.
        num_columns: int = len(self.items) // num_lines
        if len(self.items) % num_lines != 0:
            num_columns += 1

        # Early abort: if there are so many columns that the width of the
        # _column seperators_ is bigger than the width of the screen, then
        # don't even bother.
        total_seperator_width: int = ((num_columns - 1)
                                      * len(self.seperator))
        if max_width_without_margins < total_seperator_width:
            return None
        
        # Remove the seperator width from the available space
        max_width_without_seps: int = (max_width_without_margins
                                       - total_seperator_width)

        potential_dimensions: dict = self._column_widths(
            num_lines, num_columns)
        if sum(potential_dimensions['widths']) < max_width_without_seps:
            return potential_dimensions
        else:
            return None
    
    def width_dimensions(self, max_width: int) -> dict:
        item_widths = sorted([len(item) for item in self.items],
                                  reverse=True)

        if len(self.items) == 0:
            return { 'num_lines': 0, 'widths': [] }

        if len(self.items) == 1:
            the_item: dict = self.items[0]

            if len(the_item) <= max_width:
                return { 'num_lines': 1, 'widths': [len(the_item)] }
            else:
                return None

        if item_widths[0] > max_width:
            # Largest item is bigger than max width;
            # it is impossible to fit into grid.
            return None

        if sum(item_widths) < max_width:
            # Everything fits on one line
            return { 'num_lines': 1, 'widths': [len(item)
                                                for item in self.items] }

        # Calculate theoretical mininum number of columns possible, which helps
        # optimise this function.
        theoretical_min_num_cols = 0
        col_total_width_so_far = len(self.seperator) * (-1)
        max_width_without_margins = max_width - self.margin_width
        while True:
            current_item_width = item_widths[theoretical_min_num_cols]
            current_item_width += len(self.seperator)
            if (current_item_width + col_total_width_so_far
                <= max_width_without_margins):
                theoretical_min_num_cols += 1
                col_total_width_so_far += current_item_width
            else:
                break
        theoretical_max_num_lines = len(self.items) // theoretical_min_num_cols
        if len(self.items) % theoretical_min_num_cols != 0:
            theoretical_max_num_lines += 1

        # Instead of looping upwards from 1 to len(self.items), loop downwards
        # from the theoretical maximum number of lines, to 1. On small queries,
        # this provides a marginal speed boost (create_lines() goes
        # from 54.6 usec -> 42.2 usec). On large queries, the speed boost is
        # much larger (create_lines goes from 1.95 msec -> 180 usec; 11x faster)
        latest_successful_dimensions = None
        for num_lines in reversed(range(1, theoretical_max_num_lines+1)):
            response = self._get_dimensions_given_num_lines_and_maxwidth(
                max_width, num_lines)

            if response:
                latest_successful_dimensions = response
            else:
                return latest_successful_dimensions

    """
    Returns a list of strings, each representing a line. 

    Arguments:
        max_width (int): The number of horizontal columns the grid needs to
            fit in.
    """
    def create_lines(self, max_width: int) -> list:
        dimensions: dict = self.width_dimensions(max_width)
        if dimensions == None:
            return []
        num_lines: int = dimensions['num_lines']
        widths: list = dimensions['widths']
        num_columns: int = len(widths)
                
        lines: list = []
        for row in range(num_lines):
            line: str = self.left_margin
            for col in range(num_columns):
                if self.direction == 'top2bottom':
                    num: int = col * num_lines + row
                else:
                    num: int = row * num_columns + col
                
                # Abandon a line mid-way if that's where the cells end
                if num >= len(self.items):
                    continue

                item = self.items[num]
                if col == num_columns - 1:
                    # This is the final column, do not add trailing spaces
                    line += item
                else:
                    # Add extra spaces
                    extra_spaces: str = ' ' * (widths[col] - len(item))
                    line += (item + extra_spaces + self.seperator)
            line += self.right_margin
            lines.append(line)

        return lines
