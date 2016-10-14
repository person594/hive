from pyjamas.ui.Button import Button
from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.HTML import HTML
from pyjamas import Window
from pyjamas.Canvas.GWTCanvas import GWTCanvas

big_number = 1000000

class queen_bee:
	def __init__(self, color):
		self.color = color
		self.covered = None
	def __repr__(self):
		return ("White" if self.color == 0 else "Black") + " Queen Bee"
	def tile_char(self):
		return 'Q' if self.color == 0 else 'q'
	def moves(self, hive, loc):
		m = set()
		for loc2 in adj(loc):
			if loc2 not in hive.tiles and hive.slide_test(loc, loc2) and hive.adj_test(loc, loc2):
				m.add(move_tile(loc, loc2))
		return m
		
class soldier_ant:
	def __init__(self, color):
		self.color = color
		self.covered = None
	def __repr__(self):
		return ("White" if self.color == 0 else "Black") + " Soldier Ant"
	def tile_char(self):
		return 'A' if self.color == 0 else 'a'
	def moves(self, hive, loc):
		visited = {loc}
		#space...
		last_frontier = {loc}
		while len(last_frontier) > 0:
			frontier = set()
			for loc2 in last_frontier:
				for loc3 in adj(loc2):
					if loc3 not in frontier and loc3 not in visited and loc3 not in hive.tiles and hive.slide_test(loc2, loc3) and hive.adj_test(loc, loc3):
						frontier.add(loc3)
			visited.update(frontier)
			last_frontier = frontier
		visited -= {loc}
		return map(lambda l:move_tile(loc, l), visited)
	
		
class beetle:
	def __init__(self, color, covered=None):
		self.color = color
		self.covered = covered
	def __repr__(self):
		return ("White" if self.color == 0 else "Black") + " Beetle"
	def tile_char(self):
		return 'B' if self.color == 0 else 'b'
	def moves(self, hive, loc):
		m = set()
		for loc2 in adj(loc):
			if loc2 in hive.tiles:
				m.add(stack_tile(loc, loc2))
			elif self.covered is not None or (hive.adj_test(loc, loc2) and hive.slide_test(loc, loc2)):
				m.add(move_tile(loc, loc2))
		return m
	
class grasshopper:
	def __init__(self, color):
		self.color = color
		self.covered = None
	def __repr__(self):
		return ("White" if self.color == 0 else "Black") + " Grasshopper"
	def tile_char(self):
		return 'G' if self.color == 0 else 'g'
	def moves(self, hive, loc):
		m = set()
		for a in adj(loc):
			if a in hive.tiles:
				delta = (a[0] - loc[0], a[1] - loc[1])
				b = (a[0] + delta[0], a[1] + delta[1])
				while b in hive.tiles:
					b = (b[0] + delta[0], b[1] + delta[1])
				m.add(move_tile(loc, b))
		return m
	
class spider:
	def __init__(self, color):
		self.color = color
		self.covered = None
	def __repr__(self):
		return ("White" if self.color == 0 else "Black") + " Spider"
	def tile_char(self):
		return 'S' if self.color == 0 else 's'
	def moves(self, hive, loc):
		#this function is broken: if two possible paths intersect, they interfere with one another
		visited = {loc}
		#space...
		last_frontier = {loc}
		i = 0
		while len(last_frontier) > 0 and i < 3:
			frontier = set()
			for loc2 in last_frontier:
				for loc3 in adj(loc2):
					if loc3 not in frontier and loc3 not in visited and loc3 not in hive.tiles and hive.slide_test(loc2, loc3) and hive.adj_test(loc, loc3):
						for loc4 in adj(loc3).intersection(adj(loc2)):
							if loc4 in hive.tiles:
								frontier.add(loc3)
								break
			visited.update(frontier)
			last_frontier = frontier
			i+= 1
		return map(lambda l:move_tile(loc, l), last_frontier)

class place_tile:
	def __init__(self, tile, loc):
		self.tile = tile
		self.loc = loc
	def __repr__(self):
		return "Place " + str(self.tile) + " at " + str(self.loc)
	def moves(self, hive, loc):
		return set()

class move_tile:
	def __init__(self, loc1, loc2):
		self.loc1 = loc1
		self.loc2 = loc2
	def __repr__(self):
		return "Move the  tile at " + str(self.loc1) + " to " + str(self.loc2)

class stack_tile:
	def __init__(self, loc1, loc2):
		self.loc1 = loc1
		self.loc2 = loc2
	def __repr__(self):
		return "Move the tile at " + str(self.loc1) + " onto " + str(self.loc2)

class pass_turn:
	def init__(self):
		pass
	def __repr__(self):
		return "Pass turn"

def adj(loc):
	x, y = loc
	return {(x+1, y), (x-1, y), (x, y+1), (x, y-1), (x+1, y-1), (x-1, y+1)}

def prompt_list(l, prompt=':'):
	for i, item in enumerate(l):
		print ("%d: %s" % (i, str(item)))
	n = None
	while type(n) is not int or n >= len(l) or n < 0:
		try:
			n = input(prompt)
		except:
			pass
	return l[n]
	
class hive:
	def __init__(self):
		self.tiles = {}
		self.ply = 0
		self.queen_locs = [None, None]

		self.hands = {
			queen_bee(0): 1, spider(0): 2, beetle(0): 2, grasshopper(0): 3, soldier_ant(0): 3,
			queen_bee(1): 1, spider(1): 2, beetle(1): 2, grasshopper(1): 3, soldier_ant(1): 3
		}

	def hive_string(self):
		#   \     /
		#    :---:       :
		#   /  Q  \     /
		#  :  0,0  :---:
		#   \     /     \
		#    '---'
		white_hand = []
		black_hand = []
		for tile in self.hands:
			if tile.color == 0:
				white_hand += [tile] * self.hands[tile]
			else:
				black_hand += [tile] * self.hands[tile]
		white_hand_chars = []
		black_hand_chars = []
		for i in range(5):
			white_hand_chars.append([' '] * (8*len(white_hand) + 1))
			black_hand_chars.append([' '] * (8*len(black_hand) + 1))
		
		for i, tile in enumerate(white_hand):
			col = 8*i
			white_hand_chars[2][col] = ':'
			white_hand_chars[2][col+4] = tile.tile_char()
			white_hand_chars[2][col+8] = ':'
			
			white_hand_chars[1][col+1] = '/'
			white_hand_chars[3][col+1] = '\\'
			white_hand_chars[1][col+7] = '\\'
			white_hand_chars[3][col+7] = '/'
			
			white_hand_chars[0][col+2:col+7] = '.---.'
			white_hand_chars[4][col+2:col+7] = "'---'"
		
		white_hand_str = ""
		for line in white_hand_chars:
			white_hand_str += "".join(line) + '\n'
			
		for i, tile in enumerate(black_hand):
			col = 8*i
			black_hand_chars[2][col] = ':'
			black_hand_chars[2][col+4] = tile.tile_char()
			black_hand_chars[2][col+8] = ':'
			
			black_hand_chars[1][col+1] = '/'
			black_hand_chars[3][col+1] = '\\'
			black_hand_chars[1][col+7] = '\\'
			black_hand_chars[3][col+7] = '/'
			
			black_hand_chars[0][col+2:col+7] = '.---.'
			black_hand_chars[4][col+2:col+7] = "'---'"
			
		black_hand_str = ""
		for line in black_hand_chars:
			black_hand_str += "".join(line) + '\n'
		
		main_str = ""
		if len(self.tiles) > 0:
			minC = minR = big_number
			maxC = maxR = -big_number
			for loc,tile in self.tiles.items():
				r = -loc[0] - 2*loc[1]
				c = loc[0]
				minC = min(minC, c-1)
				maxC = max(maxC, c+1)
				minR = min(minR, r-2)
				maxR = max(maxR, r+2)
			nLines = 5 + 2*(maxR - minR)
			nCols = 9 + 6*(maxC - minC)
			chars = []
			for i in range(nLines):
				chars.append([' '] * nCols)
			for r in range(minR, maxR+1):
				for c in range(minC, maxC+1):
					if r%2 != c%2:
						continue
					line = 2 + 2*(r -minR)
					col = 6*(c - minC)
					x = c
					y = -(r+c)/2
					x_str = str(x)
					#left pad
					while len(x_str) < 3:
						x_str = ' ' + x_str
					y_str = str(y)
					while len(y_str) < 3:
						y_str = y_str + ' '
					chars[line][col+1] = x_str[0]
					chars[line][col+2] = x_str[1]
					chars[line][col+3] = x_str[2]
					chars[line][col+4] = ','
					chars[line][col+5] = y_str[0]
					chars[line][col+6] = y_str[1]
					chars[line][col+7] = y_str[2]
			for loc, tile in self.tiles.items():
				r = -loc[0] - 2*loc[1]
				c = loc[0]
				line = 2 + 2*(r -minR)
				col = 6*(c - minC)
				
				if chars[line-2][col+2] == ' ':
					chars[line-2][col+2] = '.'
				else:
					chars[line-2][col+2] = ':'
				chars[line-2][col+3] = '-'
				chars[line-2][col+4] = '-'
				chars[line-2][col+5] = '-'
				if chars[line-2][col+6] == ' ':
					chars[line-2][col+6] = '.'
				else:
					chars[line-2][col+6] = ':'
				
				chars[line-1][col+1] = '/'
				chars[line-1][col+4] = tile.tile_char()
				chars[line-1][col+7] = '\\'
				
				chars[line][col] = ':'
				chars[line][col+8] = ':'
				
				chars[line+1][col+1] = '\\'
				stack_str = ""
				cur = tile.covered
				while len(stack_str) < 5:
					if cur:
						stack_str += cur.tile_char()
						cur = cur.covered
					else:
						stack_str += ' '
				chars[line+1][col+2] = stack_str[0]
				chars[line+1][col+3] = stack_str[1]
				chars[line+1][col+4] = stack_str[2]
				chars[line+1][col+5] = stack_str[3]
				chars[line+1][col+6] = stack_str[4]
				chars[line+1][col+7] = '/'
				
				if chars[line+2][col+2] == ' ':
					chars[line+2][col+2] = "'"
				else:
					chars[line+2][col+2] = ':'
				chars[line+2][col+3] = '-'
				chars[line+2][col+4] = '-'
				chars[line+2][col+5] = '-'
				if chars[line+2][col+6] == ' ':
					chars[line+2][col+6] = "'"
				else:
					chars[line+2][col+6] = ':'
			
			for line in chars:
				main_str += ''.join(line) + '\n'
		return '\n'.join([black_hand_str, main_str, white_hand_str])
				
	def make_move(self, move):
		if isinstance(move, place_tile):
			self.tiles[move.loc] = move.tile
			self.hands[move.tile] -= 1
			if isinstance(move.tile, queen_bee):
				self.queen_locs[move.tile.color] = move.loc
		elif isinstance(move, move_tile):
			tile = self.tiles[move.loc1]
			if tile.covered is not None:
				self.tiles[move.loc1] = tile.covered
				tile.covered = None
			else:
				self.tiles.pop(move.loc1)
			self.tiles[move.loc2] = tile
			if isinstance(tile, queen_bee):
				self.queen_locs[tile.color] = move.loc2
		elif isinstance(move, stack_tile):
			tile = self.tiles[move.loc1]
			if tile.covered is not None:
				self.tiles[move.loc1] = tile.covered
				tile.covered = None
			else:
				self.tiles.pop(move.loc1)
			tile = beetle(tile.color, self.tiles[move.loc2])
			self.tiles[move.loc2] = tile
		self.ply += 1

	def unmake_move(self, move):
		self.ply -= 1
		if isinstance(move, place_tile):
			self.tiles.pop(move.loc)
			self.hands[move.tile] += 1
			if isinstance(move.tile, queen_bee):
				self.queen_locs[move.tile.color] = None
		elif isinstance(move, move_tile):
			tile = self.tiles[move.loc2]
			self.tiles.pop(move.loc2)
			if move.loc1 in self.tiles:
				tile = beetle(tile.color, self.tiles[move.loc1])
			self.tiles[move.loc1] = tile
			if isinstance(tile, queen_bee):
				self.queen_locs[tile.color] = move.loc1
		elif isinstance(move, stack_tile):
			tile = self.tiles[move.loc2]
			self.tiles[move.loc2] = tile.covered
			if move.loc1 in self.tiles:
				tile.covered = self.tiles[move.loc1]
			else:
				tile.covered = None
			self.tiles[move.loc1] = tile
		
	#can the tile at loc be removed while maintining the one hive
	def one_hive_test(self, loc):
		def neighbors(lc):
			return {l for l in adj(lc) if l != loc and l in self.tiles}
		explored = set()
		frontier = None
		for lc in self.tiles:
			if lc != loc:
				frontier = {lc}
				break
		if not frontier:
			return True
		while len(frontier) > 0:
			explored.update(frontier)
			new_frontier = set()
			for lc in frontier:
				new_frontier.update(neighbors(lc))
			frontier = new_frontier - explored
		return len(explored) == len(self.tiles) - 1
	
	def slide_test(self, loc1, loc2):
		for l in adj(loc1).intersection(adj(loc2)):
			if l not in self.tiles:
				return True
		return False

	def adj_test(self, loc1, loc2):
		for loc3 in adj(loc2):
			if loc3 in self.tiles and loc3 != loc1:
				return True
		return False
	
	def get_moves(self):
		moves = []
		if self.ply < 2:
			for tile in self.hands:
				if tile.color == self.ply:
					moves.append(place_tile(tile, (0, self.ply)))
			return moves
		
		color = self.ply % 2
		if self.queen_locs[color] is None:
			moves =  self.get_place_moves(self.ply >= 6)
		else:
			moves = self.get_place_moves() + self.get_movement_moves()
		if len(moves) == 0:
			moves = [pass_turn()]
		return moves
		
	def get_place_moves(self, queen_only=False):
		color = self.ply % 2
		placeable_tiles = []
		for tile in self.hands:
			if tile.color == color and self.hands[tile] > 0:
				if (not queen_only) or isinstance(tile, queen_bee):
					placeable_tiles.append(tile)
		if len(placeable_tiles) == 0: return []
		placeable_locations = []
		#loc: location of an existing tile of our color
		for loc, tile in self.tiles.items():
			if tile.color == color:
				#l2: location of an empty hex adjacent to loc; possible placement location
				for l2 in adj(loc):
					if l2 not in self.tiles and l2 not in placeable_locations:
						#l3: a non-empty hex adjacent to our empty hex
						for l3 in adj(l2):
							if l3 in self.tiles and self.tiles[l3].color != color:
								break
						else:
							placeable_locations.append(l2)
		moves = []
		for loc in placeable_locations:
			for tile in placeable_tiles:
				moves.append(place_tile(tile, loc))
		return moves
	
	def get_movement_moves(self):
		color = self.ply % 2
		moves = []
		for loc, tile in self.tiles.items():
			if tile.color == color:
				if tile.covered is not None or self.one_hive_test(loc):
					moves += list(tile.moves(self, loc))
		return moves
	
	def is_game_over(self):
		for loc in self.queen_locs:
			if loc is not None:
				for loc2 in adj(loc):
					if loc2 not in self.tiles:
						break
				else:
					return True
		return False
	
	def game_status(self):
		white_surrounded = False
		black_surrounded = False
		if self.queen_locs[0] is not None:
			for loc in adj(self.queen_locs[0]):
				if loc not in self.tiles:
					break
			else:
				white_surrounded = True
		
		if self.queen_locs[1] is not None:
			for loc in adj(self.queen_locs[1]):
				if loc not in self.tiles:
					break
			else:
				black_surrounded = True
		if white_surrounded and black_surrounded:
			return "Draw"
		elif white_surrounded and not black_surrounded:
			return "Black wins"
		elif not white_surrounded and black_surrounded:
			return "White wins"
		else:
			return "Game in progress"
	
	def evaluate(self):
		#kind of a hack to make early wins more applealing than later wins
		turn_multiplier = ((self.ply + 2.0) / (self.ply + 1.0))
		sign = 1 if self.ply%2 == 0 else -1
		white_adj = 0
		if self.queen_locs[0] is None:
			white_adj = 6
		else:
			for loc in adj(self.queen_locs[0]):
				if loc in self.tiles:
					white_adj += 1
		if white_adj == 6:
			white_adj = big_number
		black_adj = 0
		if self.queen_locs[1] is None:
			black_adj = 6
		else:
			for loc in adj(self.queen_locs[1]):
				if loc in self.tiles:
					black_adj += 1
		if black_adj == 6:
			black_adj = big_number
		
		return sign * turn_multiplier * (black_adj - white_adj)
	
	def alpha_beta(self, depth, alpha, beta):
		if depth == 0 or self.is_game_over():
			return self.evaluate()
		for move in self.get_moves():
			self.make_move(move)
			score = -self.alpha_beta(depth - 1, -beta, -alpha)
			self.unmake_move(move)
			if score >= beta:
				return beta
			if score > alpha:
				alpha = score
		return alpha
	
	def move_search(self, depth):
		beta = 2*big_number
		alpha = -beta
		best_move = None
		for move in self.get_moves():
			self.make_move(move)
			score = -self.alpha_beta(depth, -beta, -alpha)
			self.unmake_move(move)
			if score > alpha:
				alpha = score
				best_move = move
		return best_move
	
	def prompt_move(self):
		print self.hive_string()
		moves = self.get_moves()
		self.make_move(prompt_list(moves))
	
	def comp_move(self, depth=3):
		print self.hive_string()
		move = self.move_search(depth)
		print "Computer move:"
		print move
		self.make_move(move)
	
	def count_tiles(self):
		count = 0
		for tile in self.hands:
			count += self.hands[tile]
		for loc in self.tiles:
			tile = self.tiles[loc]
			while tile is not None:
				count += 1
				tile = tile.covered
		return count


def greet(sender):
	Window.alert("Hello, AJAX!")

if __name__ == '__main__':
		b = Button("Click me", greet)
		RootPanel().add(b)
		hw = HTML("Hello <b>World</b>")
		RootPanel().add(hw)
		canvas = GWTCanvas()
		RootPanel().add(canvas)
		self.canvas.beginPath()
		canvas.rect(0, 0, 300, 300)
		self.canvas.stroke()
		
