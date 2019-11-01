# Modified Flood Fill algorithm based on http://ijcte.org/papers/738-T012.pdf
# Flood Fill algorithm based on https://github.com/bblodget/MicromouseSim
# Written by Matthew Tran

import turtle, sys

SCREEN_HEIGHT = 512
SCREEN_WIDTH = 512
CANVAS_BUFFER = 0
BOX_SIZE = 32

turtle.colormode(255)
turtle.speed(0)
turtle.delay(0)
turtle.screensize(SCREEN_WIDTH+2*CANVAS_BUFFER, SCREEN_HEIGHT+2*CANVAS_BUFFER)
turtle.setworldcoordinates(-CANVAS_BUFFER-BOX_SIZE//2,-CANVAS_BUFFER-BOX_SIZE//2,SCREEN_WIDTH+CANVAS_BUFFER-BOX_SIZE//2,SCREEN_HEIGHT+CANVAS_BUFFER-BOX_SIZE//2)

# Helper Functions

# 8 = North, 4 = East, 2 = South, 1 = West
def getWalls(x):
	return (bool(x&8), bool(x&4), bool(x&2), bool(x&1))

def drawCell(x, y, s):
	turtle.up()
	turtle.setpos(BOX_SIZE*x, BOX_SIZE*(y+1))
	turtle.setheading(0)
	for i in range(4):
		if (s[i]):
			turtle.down()
		turtle.forward(BOX_SIZE)
		turtle.right(90)
		turtle.up()

def readMaze():
	f = open(sys.argv[1], "r")
	global maze, MAZE_WIDTH, MAZE_HEIGHT
	maze = []
	for l in f.readlines():
		maze.append([int(i) for i in l.split()])
	maze = maze[::-1]
	MAZE_WIDTH = len(maze[0])
	MAZE_HEIGHT = len(maze)
	maze = [[maze[y][x] for y in range(MAZE_HEIGHT)] for x in range(MAZE_WIDTH)] #swap indices so maze[x][y]
	f.close()

def checkMaze():
	flag = True
	for x in range(MAZE_WIDTH):
		for y in range(MAZE_HEIGHT):
			s = getWalls(maze[x][y])
			if (s[0] != getWalls(maze[x][(y+1)%MAZE_HEIGHT])[2]):
				flag = False
				print(x, y, "'s north IS WRONG")
			if (s[1] != getWalls(maze[(x+1)%MAZE_WIDTH][y])[3]):
				flag = False
				print(x, y, "'s east IS WRONG")
			if (s[2] != getWalls(maze[x][y-1])[0]):
				flag = False
				print(x, y, "'s south IS WRONG")
			if (s[3] != getWalls(maze[x-1][y])[1]):
				flag = False
				print(x, y, "'s west IS WRONG!")
	if flag:
		print("Maze file correct!")

def drawMaze():
	turtle.tracer(0, 0)
	for x in range(MAZE_WIDTH):
		for y in range(MAZE_HEIGHT):
			drawCell(x-0.5, y-0.5, getWalls(maze[x][y]))
	turtle.setpos(0, 0)
	turtle.setheading(90)
	turtle.update()
	turtle.tracer(1, 0)

def manhattanDist(src, tar):
	return abs(src[0] - tar[0]) + abs(src[1] - tar[1])

def dijkstras(maz, src, tar):
	paths = {}
	dists = {(src[0],src[1]):0}
	PQ = dists.copy()
	#perform dijkstras
	while len(PQ) != 0:
		# pop off PQ
		curr = min(PQ, key=lambda x: PQ[x])
		if curr == tar:
			break
		dist = PQ.pop(curr)
		# find neighbors
		walls = getWalls(maz[curr[0]][curr[1]])
		neighbors = []
		if not walls[0]:
			neighbors.append((curr[0], curr[1]+1))
		if not walls[1]:
			neighbors.append((curr[0]+1, curr[1]))
		if not walls[2]:
			neighbors.append((curr[0], curr[1]-1))
		if not walls[3]:
			neighbors.append((curr[0]-1, curr[1]))
		# relax all edges
		for n in neighbors:
			ndist = dists.setdefault(n, sys.maxsize)
			if dist + 1 < ndist:
				paths.setdefault(n, curr)
				dists[n] = dist + 1
				PQ.update({n:dist+1})
	# return paths
	p = []
	node = tar
	while node != src:
		p.append(node)
		node = paths[node]
	p.append(src)
	return p[::-1]

def drawPath(path, col):
	if len(path) == 0:
		return
	turtle.color(col)
	turtle.up()
	turtle.setpos(path[0][0]*BOX_SIZE, path[0][1]*BOX_SIZE)
	turtle.down()
	for pos in path:
		x, y = pos[0]*BOX_SIZE, pos[1]*BOX_SIZE
		turtle.setheading(turtle.towards(x, y))
		turtle.setpos(x, y)
	turtle.color("black")

# Class
class Karel:
	def __init__(self, x, y):
		turtle.up()
		turtle.setheading(90)
		turtle.setpos(x*BOX_SIZE, y*BOX_SIZE)
		turtle.color("black")
		self.x = x
		self.y = y
		self.dir = 0
		self.map = [[0 for i in range(MAZE_HEIGHT)] for j in range(MAZE_WIDTH)]
		self.mapToStart = [[0 for i in range(MAZE_HEIGHT)] for j in range(MAZE_WIDTH)]
		self.recon = [[0 for i in range(MAZE_HEIGHT)] for j in range(MAZE_WIDTH)]
		self.gather()

	# Sensors
	def openFront(self):
		return not getWalls(maze[self.x][self.y])[self.dir]

	def openLeft(self):
		return not getWalls(maze[self.x][self.y])[(self.dir-1)%4]

	def openRight(self):
		return not getWalls(maze[self.x][self.y])[(self.dir+1)%4]

	# Movement
	def turnLeft(self):
		turtle.left(90)
		self.dir = (1-(round(turtle.heading()) // 90))%4
		self.gather()

	def turnRight(self):
		turtle.right(90)
		self.dir = (1-(round(turtle.heading()) // 90))%4
		self.gather()

	def forward(self):
		turtle.forward(BOX_SIZE)
		self.x = round(turtle.xcor()) // BOX_SIZE
		self.y = round(turtle.ycor()) // BOX_SIZE
		self.gather()

	# updates reconstructed maze
	def gather(self):
		t = self.senseWalls()
		t = [t[(i-self.dir)%4] for i in range(4)]
		n = self.getNeighbors()
		n = [n[(i-self.dir)%4] for i in range(4)]
		a, b = (8,4,2,1), (2, 1, 8, 4)
		for i in range(4):
			if t[i]:
				self.recon[self.x][self.y] |= a[i]
				if n[i]:
					self.recon[n[i][0]][n[i][1]] |= b[i]

	def printRecon(self):
		for y in range(MAZE_HEIGHT-1, -1, -1):
			for x in range(MAZE_WIDTH):
				print(self.recon[x][y], end=" ")
			print()

	# Getting squares
	def isValid(self, src):
		return src[0] >= 0 and src[0] < MAZE_WIDTH and src[1] >= 0 and src[1] < MAZE_HEIGHT

	# 0 = front, 1 = right, 2 = back, 3 = left, None if doesn't exist
	def getNeighbors(self):
		n = [(self.x,self.y+1), (self.x+1,self.y), (self.x,self.y-1), (self.x-1,self.y)]
		n = [i if self.isValid(i) else None for i in n]
		n = n[self.dir:] + n[0:self.dir]
		return n

	# same format as getNeighbors()
	def getOpenNeighbors(self):
		n = self.getNeighbors()
		n[0] = n[0] if self.openFront() else None
		n[1] = n[1] if self.openRight() else None
		n[3] = n[3] if self.openLeft() else None
		return n

	# same format as getNeighbors() assume back is always open
	def senseWalls(self):
		return [not self.openFront(), not self.openRight(), False, not self.openLeft()]

	# Algorithms!
	def solveMazeFollowLeft(self, tars):
		turtle.color(0,0,255)
		turtle.down()
		while (self.x, self.y) not in tars:
			if self.openLeft():
				self.turnLeft()
				self.forward()
			elif self.openFront():
				self.forward()
			else:
				self.turnRight()

	def solveMazeFollowRight(self, tars):
		turtle.color(0,0,255)
		turtle.down()
		while (self.x, self.y) not in tars:
			if self.openRight():
				self.turnRight()
				self.forward()
			elif self.openFront():
				self.forward()
			else:
				self.turnLeft()

	# assume E1xE2 maze, where E is even
	def printMap(self):
		for y in range(MAZE_HEIGHT-1, -1, -1):
			for x in range(MAZE_WIDTH):
				print(self.map[x][y], end=" ")
			print()

	def printMapToStart(self):
		for y in range(MAZE_HEIGHT-1, -1, -1):
			for x in range(MAZE_WIDTH):
				print(self.mapToStart[x][y], end=" ")
			print()

	def getNeighborCells(self, src):
		x, y = src
		n = [(x,y+1), (x+1,y), (x,y-1), (x-1,y)]
		n = [i for i in n if self.isValid(i)]
		return n

	def getOpenNeighborCells(self, src):
		x, y = src
		n = [(x,y+1), (x+1,y), (x,y-1), (x-1,y)]
		o = getWalls(self.recon[x][y])
		return [n[i] for i in range(4) if not o[i] and self.isValid(n[i])]

	def moveMin(self):
		n = self.getOpenNeighbors()
		d = min([0,1,2,3], key=lambda x: self.map[n[x][0]][n[x][1]] if n[x] is not None else sys.maxsize)
		if d == 0:
			self.forward()
		elif d == 1:
			self.turnRight()
			self.forward()
		elif d == 2:
			self.turnRight()
			self.turnRight()
			self.forward()
		else: # d == 3
			self.turnLeft()
			self.forward()

	def moveMinToStart(self):
		n = self.getOpenNeighbors()
		d = min([0,1,2,3], key=lambda x: self.mapToStart[n[x][0]][n[x][1]] if n[x] is not None else sys.maxsize)
		if d == 0:
			self.forward()
		elif d == 1:
			self.turnRight()
			self.forward()
		elif d == 2:
			self.turnRight()
			self.turnRight()
			self.forward()
		else: # d == 3
			self.turnLeft()
			self.forward()

	def solveMazeModdedFloodFill(self):
		# fill squares with distance from center
		halfX, halfY = (MAZE_WIDTH // 2) - 1, (MAZE_HEIGHT // 2) - 1
		centers = [(halfX, halfY), (halfX+1, halfY), (halfX, halfY+1), (halfX+1,halfY+1)]
		for i in range(MAZE_WIDTH):
			for j in range(MAZE_HEIGHT):
				self.map[i][j] = min([manhattanDist((i, j), k) for k in centers])
		for i in range(MAZE_WIDTH):
			for j in range(MAZE_HEIGHT):
				self.mapToStart[i][j] = manhattanDist((0,0), (i,j))

		# 1st run to center
		turtle.color("red")
		turtle.down()
		self.moddedFloodFillToCenter()
		turtle.up()

		# 2nd run to center
		self.moddedFloodFillToStart()

		turtle.color("green")
		turtle.down()
		self.moddedFloodFillToCenter()
		turtle.up()

		# 3rd run to center
		self.moddedFloodFillToStart()

		turtle.color("blue")
		turtle.down()
		self.moddedFloodFillToCenter()
		turtle.up()

		# 4th run to center
		self.moddedFloodFillToStart()

		turtle.color("cyan")
		turtle.down()
		self.moddedFloodFillToCenter()
		turtle.up()

	def moddedFloodFillToCenter(self):
		stack = []
		while self.map[self.x][self.y] != 0: #while not at center
			overflow = 0

			stack.append((self.x, self.y))
			while len(stack) > 0:
				curr = stack.pop()

				# TODO: fix edge case of blocked off regions
				opens = [self.map[i[0]][i[1]] for i in self.getOpenNeighborCells(curr)] # little edge case of blocked off square
				md = self.map[curr[0]][curr[1]] - 1
				if len(opens) > 0:
					md = min(opens)
				overflow += 1
				if overflow > 10000: # more edge cases, too hacky tho
					print("well crap")
					break

				if (md != self.map[curr[0]][curr[1]] - 1):
					self.map[curr[0]][curr[1]] = md + 1
					stack.extend([i for i in self.getNeighborCells(curr) if self.map[i[0]][i[1]] > 0])
			self.moveMin()

	def moddedFloodFillToStart(self):
		stack = []
		while self.mapToStart[self.x][self.y] != 0: #while not at start
			overflow = 0

			stack.append((self.x, self.y))
			while len(stack) > 0:
				curr = stack.pop()

				opens = [self.mapToStart[i[0]][i[1]] for i in self.getOpenNeighborCells(curr)] # little edge case of blocked off square
				md = self.mapToStart[curr[0]][curr[1]] - 1
				if len(opens) > 0:
					md = min(opens)
				overflow += 1
				if overflow > 10000: # more edge cases
					print("well crap")
					break

				if (md != self.mapToStart[curr[0]][curr[1]] - 1):
					self.mapToStart[curr[0]][curr[1]] = md + 1
					stack.extend([i for i in self.getNeighborCells(curr) if self.mapToStart[i[0]][i[1]] > 0])
			self.moveMinToStart()

	# normal flood fill
	def solveMazeFloodFill(self):
		# fill squares with distance from center
		halfX, halfY = (MAZE_WIDTH // 2) - 1, (MAZE_HEIGHT // 2) - 1
		centers = [(halfX, halfY), (halfX+1, halfY), (halfX, halfY+1), (halfX+1,halfY+1)]
		for i in range(MAZE_WIDTH):
			for j in range(MAZE_HEIGHT):
				self.map[i][j] = min([manhattanDist((i, j), k) for k in centers])
		for i in range(MAZE_WIDTH):
			for j in range(MAZE_HEIGHT):
				self.mapToStart[i][j] = manhattanDist((0,0), (i,j))

		# 1st run
		turtle.color("red")
		turtle.down()
		x = self.floodFillHelper(centers, True)
		print("1st run - To: {}, From:".format(x), end=" ")
		turtle.up()
		y = self.floodFillHelper(centers, False)
		print(y)

		# 2nd run
		turtle.color("green")
		turtle.down()
		x = self.floodFillHelper(centers, True)
		print("2nd run - To: {}, From:".format(x), end=" ")
		turtle.up()
		y = self.floodFillHelper(centers, False)
		print(y)

		#3rd run
		turtle.color("blue")
		turtle.down()
		x = self.floodFillHelper(centers, True)
		print("3rd run - To: {}, From:".format(x), end=" ")
		turtle.up()
		y = self.floodFillHelper(centers, False)
		print(y)

		#4th run
		turtle.color("cyan")
		turtle.down()
		x = self.floodFillHelper(centers, True)
		print("4th run - To: {}".format(x))
		turtle.up()

	def floodFillHelper(self, cents, toCenter):
		l = 0
		def floodFillUpdate(cents, toCenter):
			currentLevel, nextLevel = [], [] # some stacks
			for i in range(MAZE_WIDTH):
				for j in range(MAZE_HEIGHT):
					self.map[i][j] = sys.maxsize
			if toCenter:
				currentLevel.extend(cents)
			else:
				currentLevel.append((0,0))
			level = 0
			while True:
				while currentLevel:
					curr = currentLevel.pop()
					cd = self.map[curr[0]][curr[1]]
					if cd == sys.maxsize:
						self.map[curr[0]][curr[1]] = level
						nextLevel.extend(self.getOpenNeighborCells(curr))
				if nextLevel:
					level += 1
					currentLevel = nextLevel
					nextLevel = []
				else:
					break

		floodFillUpdate(cents, toCenter)
		while self.map[self.x][self.y] != 0:
			floodFillUpdate(cents, toCenter)
			self.moveMin()
			l += 1
		return l

# Setup
readMaze()
checkMaze()
drawMaze()

# Maze Solving! start at (0,0), end at center
center = (MAZE_WIDTH//2, MAZE_HEIGHT//2)
p = dijkstras(maze, (0,0), center)
drawPath(p, (121, 252, 121))
print("Dijkstra's Length:", len(p) - 1) # bc includes start pos, too lazy to shortest path to all centers

k = Karel(0, 0)
k.solveMazeFloodFill()
