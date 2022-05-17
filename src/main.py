import pygame as pg
from GLWindow import *
import sys

def main():
	""" The main method where we create and setup our PyGame program """
	try:
		if len(sys.argv[1]) > 0:
			filename = sys.argv[1]
			print(filename)
	except:
		filename = "cube.obj"
		print(filename)

	window = OpenGLWindow()
	window.initGL(objectname = filename)
	running = True

	count = 0
	# Game loop runs for ever
	rotate = -1
	scale = 1
	x = 0
	y = 0
	z = 0
	while running:


		for event in pg.event.get(): # Grab all of the input events detected by PyGame
			if event.type == pg.QUIT:  # This event triggers when the window is closed
				running = False
			elif event.type == pg.KEYDOWN:
				if event.key == pg.K_q:  # This event triggers when the q key is pressed down
					running = False
				elif event.key == pg.K_c: # Change colours: Red, Green, Blue and White
					if count % 4 == 0:
						colorLoc = glGetUniformLocation(window.shader, "objectColor")
						glUniform3f(colorLoc, 1, 0, 0)
						count = count + 1
					elif count % 4 == 1:
						colorLoc = glGetUniformLocation(window.shader, "objectColor")
						glUniform3f(colorLoc, 0, 1, 0)
						count = count + 1
					elif count % 4 == 2:
						colorLoc = glGetUniformLocation(window.shader, "objectColor")
						glUniform3f(colorLoc, 0, 0, 1)
						count = count + 1
					elif count % 4 == 3:
						colorLoc = glGetUniformLocation(window.shader, "objectColor")
						glUniform3f(colorLoc, 1, 1, 1)
						count = count + 1
				elif event.key == pg.K_z: # Changes Rotation to Z axis
					rotate = 2
				elif event.key == pg.K_y: # Changes Rotation to Y axis
					rotate = 1
				elif event.key == pg.K_x: # Changes Rotation to X axis
					rotate = 0
				elif event.key == pg.K_s: # Stops Rotation
					rotate = -1
				elif event.key == pg.K_EQUALS:     # Scale up the size of the objects
					scale = scale + 0.1
					print(scale)
				elif event.key == pg.K_MINUS: # Scale down the size of the objects
					scale = scale - 0.1
					print(scale)
				elif event.key == pg.K_UP:  # Move Objects along y axis
					y = y + 0.1
				elif event.key == pg.K_DOWN:
					y = y - 0.1
				elif event.key == pg.K_LEFT: # Move Objects along x axis
					x = x - 0.1
				elif event.key == pg.K_RIGHT:
					x = x + 0.1
				elif event.key == pg.K_a:     # Add object and reset scene
					window.initGL(addSwitch=True, objectname=filename)
					rotate = -1
				elif event.key == pg.K_r:    # Reset Scene -> Need to fix
					window.initGL(objectname=filename)
					rotate = -1
		window.render(rotate, scale, x, y, z) # Refresh screen
	
	window.cleanup()
	pg.quit


if __name__ == "__main__":
	main()
