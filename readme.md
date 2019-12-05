# WebSketch

Created as a CMU 15-112 term project. WebSketch allows a user to lay out a website via a Photoshop-like software, including rectangles, text, and images, and export that to HTML and CSS. 

## Getting Started
This project utilizes Python 3. In addition to Python 3, you will need the following modules installed:

* Pillow
* TKinter (preferably 8.6)
* _pickle
* requests

TKinter and _pickle should come native with Python 3, so you may need to install Pillow and requests via the following commands in terminal:
```
python3 -m pip install pillow
python3 -m pip install requests
```

Once this is set up, you can clone the repository into a directory of your choice via
```
git clone git@github.com:harvzheng/15112_term_project.git
```

To run, change the directory into the project and execute the following line in a terminal:
```
python3 main.py
```
## Shortcuts for the Editor
* Cursor tool: c
* Rectangle tool: r
* Text tool: t
* Image tool: i
* Undo: shift + z
* Redo: shift + y
* Selecting multiple objects: press 's' to toggle shift, and click on objects *with cursor tool*
* Deselect all objects: esc
* Help mode: h