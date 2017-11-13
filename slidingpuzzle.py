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
from PIL import Image, ImageTk, ImageSequence
from tkinter import colorchooser
import os
import urllib.request
import io

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
        seq (list): all of this tile's PhotoImage objects (for animations)
    """
    def __init__(self, unit_id, x_loc, y_loc, img, seq):
        self.unit_id = unit_id
        self.x_loc = x_loc
        self.y_loc = y_loc
        self.img_data = img
        self.seq = seq
        self.img = img

class SlidingPuzzle(object):
    """
    An object of this class represents a sliding puzzle game. These games were
    popular between February and July of 1880.
    Attributes:
        all_tiles (list): a list containing each Tile.
        bgcolor (str): a string representing the canvas bg color, or None.
        board (Canvas): the visible board, containing Tile images.
        color_chooser (Button): a button to choose the bg color.
        columns_entry (Entry): a text box for entering the number of columns.
        columns_label (Label): a label prompting the user for a column entry.
        frame (Frame): a tkinter Frame that holds the visible game.
        height_entry (Entry):  a text box for entering the max height in pixels.
        height_label (Label): a label prompting the user for a max height entry.
        images (dictionary): a tuple:int dictionary, with each tuple being an
            (x,y) representation of a location on the board and each int being
            used to refer to images drawn by tkinter with create_image().
        img_folder (str): a string of the current image folder path, or None.
        img_toggle (Button): a button to show/hide the image.
        labels (dictionary): a tuple:int dictionary, with each tuple being an
            (x,y) representation of a location on the board and each int being
            used to refer to text labels drawn by tkinter with create_text().
        last_piece (int): the ID of the last (lower-right corner) image.
        parent (Tk): a reference to the root Tk object.
        photo_columns (int): the number of columns in the current puzzle.
        photo_entry (Entry):  a text box for entering the photo's filename.
        photo_label (Label): a label prompting the user for a filename entry.
        photo_rows (int): the number of rows in the current puzzle.
        rows_entry (Entry): a text box for entering the number of rows.
        rows_label (Label): a label prompting the user for a row entry.
        show_image (bool): whether the image is displayed.
        show_text (bool): whether the numbering is displayed.
        spare (Tile): the lower-right corner Tile, which is effectively removed
            from the puzzle until it's completed, at which point its image
            will be drawn.
        success (bool): whether the game has been won yet.
        text_bgs (dictionary): a tuple:int dictionary, with each tuple being an
            (x,y) representation of a location on the board and each int being
            used to refer to label bgs drawn by tkinter with create_rectangle().
        text_toggle (Button): a button to show/hide the numbering.
        x_step (int): the length in pixels of each tile's x-axis.
        y_step (int): the length in pixels of each tile's y-axis.
    """
    def __init__(self, parent):
        parent.title("Sliding Puzzle") # title for the window
        self.parent = parent
        self.bgcolor = None
        self.img_folder = None
        self.all_tiles = None
        self.success = False
        self.last_piece = None
        # Here's the frame:
        self.frame = Frame(parent)
        self.frame.pack()

        # Label for entering a file name
        self.photo_label = Label(self.frame, text = "Filename: ")
        self.photo_label.grid(row=1, column=0, columnspan=2)
        # Text box for entering a file name
        self.photo_entry = Entry(self.frame, width=50)
        self.photo_entry.grid(row=1, column=2, columnspan=3)
        self.photo_entry.insert(0, 'Enter to load file, mouse/arrow keys to move, F1 for help.')
        self.photo_entry.selection_range(0, END)
        self.photo_entry.focus_set()
        
        # Text box for entering animation FPS
        self.fps_entry = Entry(self.frame, width=3)
        self.fps_entry.grid(row=1, column=5)
        self.fps_entry.insert(0, 'FPS')
        
        # Button for choosing FPS
        self.fps_button = Button(self.frame, text='>', command=self.update_fps)
        self.fps_button.grid(row=1, column=5, sticky=E)

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
        self.height_entry.insert(0, '600')
        self.height_entry.grid(row=2, column=5, padx=5)
        
        # Button for choosing bg
        self.color_chooser = Button(self.frame, text='BG Color', command=self.choose_color)
        self.color_chooser.grid(row=3, column=0, columnspan=2)
        
        # Button for toggling text
        self.text_toggle = Button(self.frame, text='Toggle Numbering', command=self.toggle_text)
        self.text_toggle.grid(row=3, column=2, columnspan=2)
        self.show_text = True
        
        # Button for toggling image
        self.img_toggle = Button(self.frame, text='Toggle Image', command=self.toggle_image)
        self.img_toggle.grid(row=3, column=4, columnspan=1)
        self.show_image = True
        
        # Button for toggling key axis inversion
        self.key_toggle = Button(self.frame, text='Invert keys', command=self.toggle_keys)
        self.key_toggle.grid(row=3, column=5, columnspan=1)
        self.key_axis = True
        
        self.animation_schedule = lambda: None

        self.parent.bind("<Return>", self.draw_board) # bind the Enter button
        self.parent.bind("<F1>", self.show_help)
    
    def show_help(self, event=None):
        '''
        Pops a basic help window.
        '''
        t = Toplevel(self.parent)
        m = Message(t, text='''\tEnter a local file path or a URL, then right-click or press Enter to begin. '''
        '''For example, C:\\Users\\photos\\myphoto.jpg or http://www.example.com/photo.jpg. '''
        '''You can specify a local folder for randomly-selected photos by entering the path. For example, C:\\Users\\photos\\.\n\t'''
        '''Enter the number of rows and columns for your puzzle (minimum 3 for each) and select a maximum height for the board in pixels.'''
        '''If your chosen image is taller than the maximum height, it will be automatically scaled down. Images below this maximum '''
        '''height will be displayed at their full size.\n\t'''
        '''You can start/restart by pressing Enter or right-clicking the game board. '''
        '''To move, click a valid tile. You can move quickly by clicking and dragging through the game board. You can also move '''
        '''with the keyboard's arrow keys. If they seem backwards, click the Invert Keys button.\n\t'''
        '''You can choose a different color for the empty background tile with the BG Color button. '''
        '''You can toggle the tile numbers with the Toggle Numbering button, '''
        '''or show/hide the image itself with the Toggle Image button.\n\t'''
        '''If your image is an animation (such as a GIF), it will animate at a default of 30 FPS. '''
        '''You can choose a custom framerate between 1 and 120 FPS by entering it to the '''
        '''right of the filename entry box and either restarting (with Enter or right click) or '''
        '''clicking the ">" button just to the right of the FPS entry box.''', width=300)
        m.pack()

    def toggle_keys(self):
        '''
        Inverts the keyboard control axis.
        '''
        if self.key_axis: # if it's at the standard,
            self.key_axis = False # set it to inverted and invert them
            self.board.bind("<Left>", lambda x: self.move((max(0,self.spare.x_loc-1), self.spare.y_loc)))
            self.board.bind("<Up>", lambda x: self.move((self.spare.x_loc, max(0,self.spare.y_loc-1))))
            self.board.bind("<Right>", lambda x: self.move((min(self.photo_columns-1,self.spare.x_loc+1), self.spare.y_loc)))
            self.board.bind("<Down>", lambda x: self.move((self.spare.x_loc, min(self.photo_rows-1,self.spare.y_loc+1))))
        else: # otherwise,
            self.key_axis = True # set it to normal and reset to default
            self.board.bind("<Left>", lambda x: self.move((min(self.photo_columns-1,self.spare.x_loc+1), self.spare.y_loc)))
            self.board.bind("<Up>", lambda x: self.move((self.spare.x_loc, min(self.photo_rows-1,self.spare.y_loc+1))))
            self.board.bind("<Right>", lambda x: self.move((max(0,self.spare.x_loc-1), self.spare.y_loc)))
            self.board.bind("<Down>", lambda x: self.move((self.spare.x_loc, max(0,self.spare.y_loc-1))))
        if self.success: # if the board is complete at this point, unbind everything
            self.board.unbind("<Left>")
            self.board.unbind("<Up>")
            self.board.unbind("<Down>")
            self.board.unbind("<Right>")
    
    def choose_color(self):
        '''
        Pops a color chooser for the background.
        '''
        temp = colorchooser.askcolor()[1] # pop a chooser
        if temp: # if a choice was made,
            self.board.config(bg=temp) # use it
            self.bgcolor = temp # and save it
            
    def toggle_text(self):
        '''
        Toggles the tile numbering labels.
        '''
        if self.show_text: # if text is currently on,
            newstate = HIDDEN # choose the other state
            self.show_text = False # and turn it off
        else: # otherwise,
            newstate = NORMAL # choose the other state
            self.show_text = True # and turn it on
        for t in self.labels.values(): # go through all the text labels
            self.board.itemconfig(t, state=newstate) # and set them to the new state
        for b in self.text_bgs.values(): # go through all the label bgs
            self.board.itemconfig(b, state=newstate) # and set them to the new state
    
    def toggle_image(self):
        '''
        Show/hide the puzzle's image.
        '''
        if self.show_image: # if it's on,
            newstate = HIDDEN # choose the other state
            self.show_image = False # and turn it off
        else: # otherwise,
            newstate = NORMAL # choose the other state
            self.show_image = True # and turn it on
        for t in self.images.values(): # go through each image
            self.board.itemconfig(t, state=newstate) # and set it to the new state
        if self.success: # if the board is complete,
            self.board.itemconfig(self.last_piece, state=newstate) # change the last tile too
    
    def draw_board(self, event):
        """
        Creates the game, wiping any previous conditions.
        """
        try: # try to wipe the board
            self.board.destroy()
        except AttributeError:
            pass # as long as there's no board
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

        if filename.startswith('http'): # if it's a URL
            try: # try to download and open it
                orig = Image.open(io.BytesIO(urllib.request.urlopen(filename).read()))
            except: # if it fails,
                self.photo_label.config(text="Not found. ") # say so
                return
            else:
                # if it works, reset the label
                self.photo_label.config(text="Filename: ")
        else: # if it's not a URL
            try: # try to open the image in the given filename
                orig = Image.open(filename)
            except: # if that fails
                try:
                    newname = os.path.dirname(filename) # get a path
                    if self.img_folder != newname: # if it's new,
                        self.img_folder = newname # save it
                        self.img_folder_contents = os.listdir(self.img_folder) # save the contents
                    f = choice(self.img_folder_contents) # choose an image
                    orig = Image.open(os.path.join(self.img_folder, f)) # and load it
                except: # if something's wrong there,
                    self.photo_label.config(text="Not found. ") # say so
                    return # and don't create the game
                else: # if it worked, say which file this is
                    self.photo_label.config(text="File {} in: ".format(f))
            else:
                # if it works, reset the label
                self.photo_label.config(text="Filename: ")
        sequence = list(ImageSequence.Iterator(orig)) # exhaust the iterator to find the animation length
        master_image = sequence[0] # get a base image
        if master_image.size[1] > max_height: # if the image is too big,
            width = int(master_image.size[0]*max_height/master_image.size[1])
            for i in range(len(sequence)):
                sequence[i] = sequence[i].resize((width, max_height),
                                                 resample=Image.ANTIALIAS) # resize it according to the entered max height
            master_image = master_image.resize((int(master_image.size[0]*max_height/master_image.size[1]),
                                                   max_height),
                                                   resample=Image.ANTIALIAS)
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
                # within the master image, and a sequence of the crops
                dim = (column*self.x_step,
                       row*self.y_step,
                       (column + 1) * self.x_step,
                       (row + 1) * self.y_step
                      )
                s = [ImageTk.PhotoImage(img.crop(dim))
                            for img in ImageSequence.Iterator(orig)]
                self.all_tiles.append(Tile(current_id,
                                           column,
                                           row,
                                           master_image.crop(dim),
                                           s
                                           )
                                       )
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
        if inversions % 2: # so, if it's odd,
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
        height = master_image.size[1], bg=self.bgcolor)
        # put the Canvas into the Frame
        self.board.grid(row=0, column=0, columnspan=7)
        
        # create each Tile's image on the board and save it in a dictionary,
        # which we can later access with a location tuple as the key
        self.images = {(tile.x_loc,tile.y_loc):self.board.create_image \
            (tile.x_loc*self.x_step, tile.y_loc*self.y_step, \
            anchor=NW, image=tile.seq[0]) for tile in self.all_tiles}
        # create each Tile's coordinate label and save it in a dictionary,
        # which we can later access with a location tuple as the key
        self.labels = {(tile.x_loc,tile.y_loc):self.board.create_text \
            (tile.x_loc*self.x_step, tile.y_loc*self.y_step, \
            anchor=NW, text=' %d' % (tile.unit_id+1),
            font=('Arial', 14)) for tile in self.all_tiles}
        # create each Tile's coordinate label background and save it in a dictionary,
        # which we can later access with a location tuple as the key
        self.text_bgs = {(tile.x_loc,tile.y_loc):self.board.create_rectangle \
            (self.board.bbox(self.labels[(tile.x_loc,tile.y_loc)]), \
            outline='white', fill='white') for tile in self.all_tiles}
        for l in self.labels.values():
            self.board.tag_raise(l) # put the numbers above the bgs
        
        # turn off the text/image if we're not supposed to show them
        if not self.show_text:
            self.show_text = True
            self.toggle_text()
        if not self.show_image:
            self.show_image = True
            self.toggle_image()
        
        # bind the Enter button and right-click-release button to drawing a new board
        self.parent.bind("<Return>", self.draw_board)
        self.board.bind("<ButtonRelease-3>", self.draw_board)
        # and left-click, drag, and arrow keys to move a tile
        self.board.bind("<Button-1>", self.move)
        self.board.bind("<B1-Motion>", self.move)
        self.board.bind("<Left>", lambda x: self.move((min(self.photo_columns-1,self.spare.x_loc+1), self.spare.y_loc)))
        self.board.bind("<Up>", lambda x: self.move((self.spare.x_loc, min(self.photo_rows-1,self.spare.y_loc+1))))
        self.board.bind("<Right>", lambda x: self.move((max(0,self.spare.x_loc-1), self.spare.y_loc)))
        self.board.bind("<Down>", lambda x: self.move((self.spare.x_loc, max(0,self.spare.y_loc-1))))
        self.board.focus_set()
        self.parent.after_cancel(self.animation_schedule)
        if len(sequence) > 1:
            self.update_fps()
            self.animate(1)
    
    def update_fps(self):
        """
        Updates the animation's FPS value.
        """
        fps = self.fps_entry.get()
        self.fps_ms = 1000//min(max(1, int(fps)), 120) if fps.isdigit() else 33
    
    def move(self, event):
        """
        Process the user's clicks into moves on the board.
        Parameter:
            event (sequence): data describing the input. In this case, it's
            just the mouse cursor coordinates when the mouse was left-clicked.
        """
        if isinstance(event, tuple): # if it's a tuple,
            click = event # perfect
        else: # if not...
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

        self.success = True # first we'll assume the user won the game with this move
        for tile in self.all_tiles: # look at each tile
            # if it's the one that was clicked on,
            if (tile.x_loc, tile.y_loc) == click:
                # its image, label, and label bg move to where the spare tile is,
                # which we're using as an "empty" space since we're not displaying its image
                self.board.coords(self.images.get(click), self.spare.x_loc * \
                self.x_step, self.spare.y_loc * self.y_step)
                self.board.coords(self.labels.get(click), self.spare.x_loc * \
                self.x_step, self.spare.y_loc * self.y_step)
                self.board.itemconfig(self.labels.get(click), state=NORMAL)
                self.board.coords(self.text_bgs.get(click), self.board.bbox(self.labels[click]))
                self.board.itemconfig(self.labels.get(click), state=NORMAL if self.show_text else HIDDEN)
                # its location is set to where the spare tile ("empty" space)
                # currently is
                tile.x_loc, tile.y_loc = self.spare.x_loc, self.spare.y_loc
                # the spare tile now gets a location of where the moved tile
                # was, which is still described in the click location
                self.spare.x_loc, self.spare.y_loc = click[0], click[1]
                # the images, labels, and text_bgs dictionaries have to be updated
                # with the moved Tile's new location by making that new location
                # point to the old value
                self.images[(tile.x_loc, tile.y_loc)] = self.images.get(click)
                self.labels[(tile.x_loc, tile.y_loc)] = self.labels.get(click)
                self.text_bgs[(tile.x_loc, tile.y_loc)] = self.text_bgs.get(click)
                # now to check if this was a winning move
                for tile in self.all_tiles: # look at each tile
                    # if its ID doesn't match its current location,
                    if tile.unit_id != self.photo_columns*tile.y_loc+tile.x_loc:
                        self.success = False # it wasn't a win
                        break # so stop looking
                else: # if we didn't break on failure, then each Tile is now in the
                      # right place, so it's a win
                    # fill in the corner piece with the spare tile's image
                    
                    self.all_tiles.append(self.spare)
                    self.spare.y_loc = self.photo_rows-1
                    self.spare.x_loc = self.photo_columns-1
                    self.images[(self.spare.x_loc, self.spare.y_loc)] = self.board.create_image(
                        self.spare.x_loc*self.x_step, self.spare.y_loc*self.y_step, anchor=NW, image=self.spare.seq[0],
                        state=NORMAL if self.show_image else HIDDEN)
                    # and unbind all the movement keys
                    self.board.unbind("<Button-1>")
                    self.board.unbind("<B1-Motion>")
                    self.board.unbind("<Left>")
                    self.board.unbind("<Up>")
                    self.board.unbind("<Down>")
                    self.board.unbind("<Right>")
                # don't keep checking whether we clicked on one of the other
                # tiles, because we already found it
                return
        
    def animate(self, counter):
        """
        Animates the image sequence.
        Parameter:
            counter: the index of the next image from the sequence list
        """
        for tile in self.all_tiles:
            tile.img = tile.seq[counter]
            self.board.itemconfig(self.images[(tile.x_loc,tile.y_loc)], image=tile.img)
        self.animation_schedule = self.parent.after(self.fps_ms, self.animate, (counter+1) % len(tile.seq))

def main():
    root = Tk() # Create a Tk object from tkinter.
    sliding_puzzle = SlidingPuzzle(root) # Make my game inherit from that object.
    root.mainloop() # Run the main loop.

if __name__ == '__main__':
    main()
