from tkinter import *
import mss
import mss.tools
from dataclasses import dataclass
import sqlite3 as sqlite
import pickle

"""
Creates a new TK window,
sets it to possibly ocupy the entire screen
with .2 alpha so you can see through it.
"""
root = Tk()
root.attributes('-alpha', 0.2)

maxW = root.winfo_screenwidth()
maxH = root.winfo_screenheight()

root.wait_visibility(root)
root.geometry(f"{maxW}x{maxH}+0+0")

"""
Bad solution for a stupid issue
"""
current_coordinates = []

"""
Connects to the database file
Tries to fetch anything from the images table
If nope, creates the table
ROBUST TESTING AND NO IMPROPER ERROR SINKING IS HAPPENING HERE
"""
try:
    db_conn = sqlite.connect('./image_db.sqlite')
    db_conn.execute("SELECT * FROM images LIMIT 1")
except Exception as e:
    print(e)
    db_conn.execute("""CREATE TABLE images
                       (raw text, pixels text, collection text)""")
finally:
    db_conn.close()

"""
I'm not sure why from all the ways I could have done it,
I decided to do with a dataclass. A class.
"""
@dataclass
class Selection:
    x1: int
    y1: int
    x2: int
    y2: int
    height: int
    width: int
    """
    Seriously, that's the only palce where I use something
    just the dataclass gives me, a damn init.
    """
    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.width = abs(self.x1 - self.x2)
        self.height = abs(self.y1 - self.y2)

"""
I'm not even sure if that's a thing.
I refuse to inspect memory.
"""
current_selection: Selection

"""
Receives a screen area and uses that to capture the screen.
"""
def capture_screen(selection):
    root.attributes('-alpha', 0.0)
    with mss.mss() as sct:
        monitor = {"top": selection.x1,
                   "left": selection.y2,
                   "width": selection.width,
                   "height": selection.height}
        sct_img = sct.grab(monitor)
        
        db_conn = sqlite.connect('./image_db.sqlite')
        cursor = db_conn.cursor()
        cursor.execute(
            "INSERT INTO images VALUES (?, ?, ?)",
                (
                    pickle.dumps(sct_img.raw),
                    pickle.dumps(sct_img.pixels),
                    "testing"
                )
        )
        db_conn.commit()
        db_conn.close()
    """
    Screen flickering with a good cause: 
      Preserve color
    """
    root.attributes('-alpha', 0.2)

def get_coords_down(event):
    current_coordinates.append(event.x)
    current_coordinates.append(event.y)

def get_coords_up(event):
    current_coordinates.append(event.x)
    current_coordinates.append(event.y)
    current_selection = Selection(
        x1=current_coordinates[0],
        y1=current_coordinates[1],
        x2=current_coordinates[2],
        y2=current_coordinates[3],
    )
    print(current_selection)
    current_coordinates.clear()
    capture_screen(selection=current_selection)

def exit(event):
    root.destroy()

root.bind("<Button-1>", get_coords_down)
root.bind("<ButtonRelease-1>", get_coords_up)
root.bind("<Escape>", exit)

root.mainloop()
