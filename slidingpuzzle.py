#-------------------------------------------------------------------------------
# Name:        Sliding Puzzle
# Purpose:
#
# Author:      David Muller
#
# Created:     06/03/2014
# Copyright:   (c) David Muller 2014
# Licence:     <your license>
#-------------------------------------------------------------------------------
from tkinter import *
from random import *
from PIL import Image, ImageTk

class Tile(object):
    """
    An object of this class represents a tile in the puzzle.
    Attributes:
        unit_id (int): the ID of the tile. 0 for the top-left tile, 1 for the
        one to the right of that, 2 for the next, and so on, going row by row.
            This numbering matches the original image for win-checking.
        x_loc (int): the current X coordinate of the tile, starting with 0 for
            tiles in the left-most column. This changes as the game progresses.
        y_loc (int): the current Y coordinate of the tile, starting with 0 for
            tiles in the top-most row. This changes as the game progresses.
        img_data (ImageCrop): the raw image object, providing access to
            metadata such as size.
        img (PhotoImage): the PhotoImage object for this tile, which can then
            be drawn on the canvas with create_image().
    """
    def __init__(self, unit_id, x_loc, y_loc, img):
        img.load()
        self.unit_id = unit_id
        self.x_loc = x_loc
        self.y_loc = y_loc
        self.img_data = img
        self.img = ImageTk.PhotoImage(img)

class SlidingPuzzle(object):
    """
    An object of this class represents a sliding puzzle game. These games were
    popular between February and July of 1880.
    Attributes:
        all_tiles (list): a list containing each Tile.
        board (Canvas): the visible board, containing Tile images.
        columns_entry (Entry): a text box for entering the number of columns.
        columns_label (Label): a label prompting the user for a column entry.
        frame (Frame): a tkinter Frame that holds the visible game
        height_entry (Entry):  a text box for entering the max height in pixels.
        height_label (Label): a label prompting the user for a max height entry.
        images (dictionary): a tuple:int dictionary, with each tuple being an
            (x,y) representation of a location on the board and each int being
            used to refer to images drawn by tkinter with create_image().
        parent (Tk): a reference to the root Tk object.
        photo_columns (int): the number of columns in the current puzzle.
        photo_entry (Entry):  a text box for entering the photo's filename.
        photo_label (Label): a label prompting the user for a filename entry.
        photo_rows (int): the number of rows in the current puzzle.
        rows_entry (Entry): a text box for entering the number of rows.
        rows_label (Label): a label prompting the user for a row entry.
        spare (Tile): the lower-right corner Tile, which is effectively removed
            from the puzzle until it's completed, at which point its image
            will be drawn.
        x_step (int): the length in pixels of each tile's x-axis.
        y_step (int): the length in pixels of each tile's y-axis.
    """
    def __init__(self, parent):
        parent.title("Sliding Puzzle") # title for the window
        self.parent = parent

        # Here's the frame:
        self.frame = Frame(parent)
        self.frame.pack()

        # Label for entering a file name
        self.photo_label = Label(self.frame, text = "Filename: ")
        self.photo_label.grid(row=1, column=0, columnspan=2)
        # Text box for entering a file name
        self.photo_entry = Entry(self.frame, width=32)
        self.photo_entry.grid(row=1, column=2, columnspan=4)

        # Label for entering rows
        self.rows_label = Label(self.frame, text = "Rows: ")
        self.rows_label.grid(row=2, column=0)
        # Text box for entering rows
        self.rows_entry = Entry(self.frame, width=3)
        self.rows_entry.grid(row=2, column=1, padx=5)

        # Label for entering columns
        self.columns_label = Label(self.frame, text = "Columns: ")
        self.columns_label.grid(row=2, column=2)
        # Text box for entering columns
        self.columns_entry = Entry(self.frame, width=3)
        self.columns_entry.grid(row=2, column=3, padx=5)

        # Label for entering a max height
        self.height_label = Label(self.frame, text = "Max height (pixels): ")
        self.height_label.grid(row=2, column=4)
        # Text box for entering a max height
        self.height_entry = Entry(self.frame, width=5)
        self.height_entry.grid(row=2, column=5, padx=5)

        self.parent.bind("<Return>", self.draw_board) # bind the Enter button

    def draw_board(self, event):
        """
        Creates the game, wiping any previous conditions.
        """

        filename = self.photo_entry.get() # get a filename from the text field
        self.photo_rows = self.rows_entry.get() # get a row from the row field
        try: # try to turn the row entry into an int
            self.photo_rows = int(self.photo_rows)
        except: # if it wasn't a number,
            self.photo_rows = 0 # set it to 0
        if self.photo_rows < 3: # if rows is too small
            self.rows_entry.delete(0, END) # wipe the entry field
            self.rows_entry.insert(0, "3") # set it to 3
            self.photo_rows = 3 # and set rows to 3

        # get columns from the columns field
        self.photo_columns = self.columns_entry.get()
        try: # try to turn that into an int
            self.photo_columns = int(self.photo_columns)
        except: # if it wasn't a number,
            self.photo_columns = 0 # set it to 0
        if self.photo_columns < 3: # if columns is too small
            self.columns_entry.delete(0, END) # wipe the entry field
            self.columns_entry.insert(0, "3") # set it to 3
            self.photo_columns = 3 # and set rows to 3

        # get a max height from the height field
        max_height = self.height_entry.get()
        try: # try to turn that into an int
            max_height = int(max_height)
        except: # if it wasn't a number,
            max_height = 0 # set it to 0
        if max_height < 10: # if height is too small
            self.height_entry.delete(0, END) # wipe the entry field
            self.height_entry.insert(0, "10") # set it to 10
            max_height = 10 # and set height to 10

        try: # try to open the image in the given filename
            master_image = Image.open(filename)
            # if it works, reset the label
            self.photo_label.config(text="Filename: ")
        except: # if that fails
            self.photo_label.config(text="Not found. ") # say so
            return # and don't create the game

        if master_image.size[1] > max_height: # if the image is too big,
            master_image = master_image.resize \
            ((int(master_image.size[0]*max_height/master_image.size[1]), \
            max_height)) # resize it according to the entered max height

        self.all_tiles = [] # create a list for the Tiles
        # this will be the width of each tile, in pixels
        self.x_step = int(master_image.size[0]/self.photo_columns)
        # this will be the height of each tile, in pixels
        self.y_step = int(master_image.size[1]/self.photo_rows)
        current_id = 0 # we'll start with an ID of 0
        for row in range(self.photo_rows): # for each row
            for column in range(self.photo_columns): # and column,
                # add a new Tile to the list, with the current ID, and a
                # column and row based on the location of the cropped image
                # within the master image
                self.all_tiles.append(Tile(current_id, column, row, \
                master_image.crop( \
                (column*self.x_step, row*self.y_step, \
                (column + 1) * self.x_step, \
                (row + 1) * self.y_step))))
                # increment the current ID for the next Tile to use
                current_id += 1

        # and now to randomize, check inversions, and fix unsolvable boards
        self.spare = self.all_tiles.pop() # remove a tile so the game can work
        shuffle(self.all_tiles) # randomize the tiles
        # look at each tile in the shuffled list
        for i in range(len(self.all_tiles)):
            # assign it an x_loc and y_loc based on its location in the
            # shuffled list
            self.all_tiles[i].y_loc, self.all_tiles[i].x_loc = \
            divmod(i,self.photo_columns)

        # an inversion is when a tile with a larger ID comes before a tile with
        # a smaller ID - their order is "inverted." This is a factor in
        # whether a given puzzle is solvable. For more information, see
        # http://www.cs.bham.ac.uk/~mdr/teaching/
        # modules04/java2/TilesSolvability.html
        inversions = 0
        for tile in range(len(self.all_tiles)): # go through each list element
            # for each element on or after the given element,
            for subsequent in range(tile,len(self.all_tiles)):
                # if the ID of that later element is smaller than the ID of
                # the one we're looking at,
                if self.all_tiles[subsequent].unit_id < \
                self.all_tiles[tile].unit_id:
                    # add to our inversion count
                    inversions += 1

        # based on the way the blank tile is always the 'last' one, in the
        # lower-right corner, we need an even number of inversions if we want
        # this to be solvable.
        if inversions % 2 == 1: # so, if it's odd,
            # switch the last two elements in the list of Tiles
            self.all_tiles[-1], self.all_tiles[-2] = \
            self.all_tiles[-2], self.all_tiles[-1]
            # and have them swap locations
            (self.all_tiles[-1].x_loc, self.all_tiles[-1].y_loc), \
            (self.all_tiles[-2].x_loc, self.all_tiles[-2].y_loc) = \
            (self.all_tiles[-2].x_loc, self.all_tiles[-2].y_loc), \
            (self.all_tiles[-1].x_loc, self.all_tiles[-1].y_loc)

        # now that we have a good set of Tiles for our puzzle, we can
        # make the board with a Canvas the size of the given (above) image
        self.board = Canvas(self.frame, width=master_image.size[0], \
        height = master_image.size[1])
        # put the Canvas into the Frame
        self.board.grid(row=0, column=0, columnspan=8)
        # create each Tile's image on the board and save it in a dictionary,
        # which we can later access with a location tuple as the key
        self.images = {(tile.x_loc,tile.y_loc):self.board.create_image \
            (tile.x_loc*self.x_step, tile.y_loc*self.y_step, \
            anchor=NW, image=tile.img) for tile in self.all_tiles}

        # bind the Enter button to drawing a new board
        self.parent.bind("<Return>", self.draw_board)
        # and left-click to move a tile
        self.board.bind("<Button-1>", self.move)

    def move(self, event):
        """
        Process the user's clicks into moves on the board.
        Parameter:
            event (sequence): data describing the input. In this case, it's
            just the mouse cursor coordinates when the mouse was left-clicked.
        """
        # Parses the mouse cursor location at the time of the click into a
        # tuple that the game's logic can handle.
        click = (event.x//self.x_step, event.y//self.y_step)

        # make a set of tuples that describe the locations of four tiles around
        # the empty space
        movable_tiles = {(self.spare.x_loc - 1, self.spare.y_loc),
        (self.spare.x_loc, self.spare.y_loc - 1),
        (self.spare.x_loc + 1, self.spare.y_loc),
        (self.spare.x_loc, self.spare.y_loc + 1)}
        # make a set of tuples to describe the locations of any supposed
        # tiles that are actually not on the board
        bad_tiles = set()
        for tile in movable_tiles: # look at each tile in movable_tiles
            # if its x is less than 0 or more than the number of columns,
            # or if its y is less than 0 or more than the number of rows,
            if tile[0] < 0 or tile[0] > self.photo_columns or \
            tile[1] < 0 or tile[1] > self.photo_rows:
                bad_tiles.add(tile) # add it to bad_tiles

        # remove any tiles in bad_tiles from movable_tiles
        movable_tiles -= bad_tiles

        # if the user didn't click a tile that can be moved,
        if click not in movable_tiles:
            return # then we're done here

        success = True # first we'll assume the user won the game with this move
        for tile in self.all_tiles: # look at each tile
            # if it's the one that was clicked on,
            if (tile.x_loc, tile.y_loc) == click:
                # its image moves to where the spare tile is, which we're using
                # as an "empty" space since we're not displaying its image
                self.board.coords(self.images.get(click), self.spare.x_loc * \
                self.x_step, self.spare.y_loc * self.y_step)
                # its location is set to where the spare tile ("empty" space)
                # currently is
                tile.x_loc, tile.y_loc = self.spare.x_loc, self.spare.y_loc
                # the spare tile now gets a location of where the moved tile
                # was, which is still described in the click location
                self.spare.x_loc, self.spare.y_loc = click[0], click[1]
                # the images dictionary has to be updated with the moved Tile's
                # new location by making that new location point to the old
                # value
                self.images[(tile.x_loc, tile.y_loc)] = self.images.get(click)
                # now to check if this was a winning move
                for tile in self.all_tiles: # look at each tile
                    # if its ID doesn't match its current location,
                    if tile.unit_id != self.photo_columns*tile.y_loc+tile.x_loc:
                        success = False # it wasn't a win

                if success: # if each Tile is now in the right place, it's a win
                    # fill in the corner piece with the spare tile's image
                    self.board.create_image((self.photo_columns-1)* \
                    self.x_step, (self.photo_rows-1)*self.y_step, anchor=NW, \
                    image=self.spare.img)
                    self.board.unbind("<Button-1>") # and unbind the mouse
                # don't keep checking whether we clicked on one of the other
                # tiles, because we already found it
                return

def main():
    root = Tk() # Create a Tk object from tkinter.
    sliding_puzzle = SlidingPuzzle(root) # Make my game inherit from that object.
    root.mainloop() # Run the main loop.

if __name__ == '__main__':
    main()
