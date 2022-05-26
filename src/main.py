import pygame as pg
from GLWindow import *
import sys

def main():
	""" The main method where we create and setup our PyGame program """
	try:
		if len(sys.argv[1]) > 0 and len(sys.argv[2]) > 0 and len(sys.argv[3]) > 0:
			filename = sys.argv[1]
			diffuseMap = sys.argv[2]
			normalMap = sys.argv[3]
	except:
		filename = "sphere.obj"
		diffuseMap = "brickwall.jpg"
		normalMap = "brickwall_normal.jpg"

	window = OpenGLWindow()
	window.initGL(objectname = filename, diffuseMap=diffuseMap, normalMap=normalMap)
	running = True

	count = 0
	# Game loop runs for ever
	rotate = -1
	scale = 1
	rotateCam = False
	rotateLights = False
	while running:


		for event in pg.event.get(): # Grab all of the input events detected by PyGame
			if event.type == pg.QUIT:  # This event triggers when the window is closed
				running = False
			elif event.type == pg.KEYDOWN:
				if event.key == pg.K_q:  # This event triggers when the q key is pressed down
					running = False
				elif event.key == pg.K_y: # Changes Rotation to Y axis
					rotate = 2
				elif event.key == pg.K_z: # Changes Rotation to Z axis
					rotate = 1
				elif event.key == pg.K_x: # Changes Rotation to X axis
					rotate = 0
				elif event.key == pg.K_s: # Stops Rotation
					rotate = -1
				elif event.key == pg.K_EQUALS:     # Scale up the size of the objects
					if scale < 2.5:
						scale = scale + 0.1
					#print(scale)
				elif event.key == pg.K_MINUS: # Scale down the size of the objects
					if scale > 0:
						scale = scale - 0.1
					#print(scale)
				elif event.key == pg.K_r:    # Reset Scene -> Need to fix
					window.initGL(objectname=filename, diffuseMap=diffuseMap, normalMap=normalMap)
					rotate = -1     # Stops object rotatiom
					window.scene.cube.eulers=[0, 0, 0]
					rotateCam = False   # Stops camera Rotation
					window.cameraTheta = 0  # Resets Camera Position
					rotateLights = False # Stop light rotation
					window.lightTheta = 0 # Reset light position
				elif event.key == pg.K_c:
					if not rotateCam:
						rotateCam = True
					else:
						rotateCam = False
				elif event.key == pg.K_l:
					if not rotateLights:
						rotateLights = True
					else:
						rotateLights = False

		window.render(rotate, scale, rotateCam = rotateCam, rotateLights = rotateLights) # Refresh screen

	window.cleanup()
	pg.quit


if __name__ == "__main__":
	main()
