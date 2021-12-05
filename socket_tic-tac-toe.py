# MODULES
import numpy as np
import pygame
import pygame_menu
from pygame.locals import *
import random
import select
import socket
import sys
import time

# CONSTANTS
BG_COLOR = (81, 194, 255)
LINE_COLOR = (62, 149, 195)
CIRCLE_COLOR = (157, 97, 208)
CROSS_COLOR = (66, 66, 66)
PORT = 48763

# GLOBAL VARIABLES
screen_size = 800
grid_size = 3
space_size = screen_size // grid_size
line_width = space_size // 9
win_line_width = space_size // 10
win_line_padding = space_size // 12
circle_radius = space_size // 3
circle_width = space_size // 12
cross_width = space_size // 9
cross_padding = space_size // 4
grid = np.zeros((grid_size, grid_size))
s = socket.socket()
conn = socket.socket()
order = 0

# PYGAME STUFF
pygame.init()
pygame.display.set_caption('Tic-Tac-Toe')
screen = pygame.display.set_mode((screen_size, screen_size), pygame.RESIZABLE)
font = pygame.font.SysFont('Arial', 40)

# FUNCTIONS FOR MAIN MENU
def set_grid_size(value, size):
	global grid_size, grid
	grid_size = size
	grid = np.zeros((grid_size, grid_size))
	update_ui_vars()

def update_ui_vars():
	global grid_size, space_size, line_width, win_line_width, win_line_padding, circle_radius, circle_width, cross_width, cross_padding
	space_size = screen_size // grid_size
	line_width = space_size // 9
	win_line_width = space_size // 10
	win_line_padding = space_size // 12
	circle_radius = space_size // 3
	circle_width = space_size // 12
	cross_width = space_size // 9
	cross_padding = space_size // 4

# FUNCTIONS FOR GAME
def draw_lines():
	# horizontal
	for row in range(1, grid_size):
		pygame.draw.line(screen, LINE_COLOR, (0, row * space_size),
						 (screen_size, row * space_size), line_width)
	# vertical
	for col in range(1, grid_size):
		pygame.draw.line(screen, LINE_COLOR, (col * space_size, 0),
						 (col * space_size, screen_size), line_width)

def draw_figures():
	for row in range(grid_size):
		for col in range(grid_size):
			if grid[row][col] == 1:  # draw X for player 1
				pygame.draw.line(screen, CROSS_COLOR, (col * space_size + cross_padding, row * space_size + cross_padding),
								 ((col + 1) * space_size - cross_padding, (row + 1) * space_size - cross_padding), cross_width)
				pygame.draw.line(screen, CROSS_COLOR, (col * space_size + cross_padding, (row + 1) * space_size -
													   cross_padding), ((col + 1) * space_size - cross_padding, row * space_size + cross_padding), cross_width)
			elif grid[row][col] == 2:  # draw O for player 2
				pygame.draw.circle(screen, CIRCLE_COLOR, (col * space_size + space_size //
														  2, row * space_size + space_size // 2), circle_radius, circle_width)

def mark_space(row, col, player):
	grid[row][col] = player

def is_space_available(row, col):
	return grid[row][col] == 0

def is_grid_empty():
	return np.all(grid == 0)

def is_winner(player):
	# vertical win check
	for col in range(grid_size):
		if np.all(grid.T[col] == player):
			draw_vertical_winning_line(col, player)
			return True

	# horizontal win check
	for row in range(grid_size):
		if np.all(grid[row] == player):
			draw_horizontal_winning_line(row, player)
			return True

	# diagonal win check
	if np.all(grid.diagonal() == player):
		draw_diagonal_winning_line(player)
		return True

	# antidiagonal win chek
	if np.all(np.fliplr(grid).diagonal() == player):
		draw_antidiagonal_winning_line(player)
		return True

	return False

def draw_vertical_winning_line(col, player):
	if player == 1:
		color = CROSS_COLOR
	elif player == 2:
		color = CIRCLE_COLOR

	posX = col * space_size + space_size // 2
	pygame.draw.line(screen, color, (posX, win_line_padding),
					 (posX, screen_size - win_line_padding), win_line_width)

def draw_horizontal_winning_line(row, player):
	if player == 1:
		color = CROSS_COLOR
	elif player == 2:
		color = CIRCLE_COLOR

	posY = row * space_size + space_size // 2
	pygame.draw.line(screen, color, (win_line_padding, posY),
					 (screen_size - win_line_padding, posY), win_line_width)

def draw_diagonal_winning_line(player):
	if player == 1:
		color = CROSS_COLOR
	elif player == 2:
		color = CIRCLE_COLOR

	pygame.draw.line(screen, color, (win_line_padding, win_line_padding),
					 (screen_size - win_line_padding, screen_size - win_line_padding), win_line_width)

def draw_antidiagonal_winning_line(player):
	if player == 1:
		color = CROSS_COLOR
	elif player == 2:
		color = CIRCLE_COLOR

	pygame.draw.line(screen, color, (win_line_padding, screen_size - win_line_padding),
					 (screen_size - win_line_padding, win_line_padding), win_line_width)

def game_restart():
	screen.fill(BG_COLOR)
	draw_lines()
	grid.fill(0)

# WAIT SERVER LOOP
def wait_server():
	global screen_size, screen, s, conn, order
	order = random.randint(1, 2)  # random select order
	text1 = font.render(
		'Waiting for connection, press Esc to cancel.', True, (255, 255, 255))
	text2 = font.render('You will be the X!', True, (255, 255, 255))
	text3 = font.render('You will be the O!', True, (255, 255, 255))
	text1_rect = text1.get_rect(center=(screen_size // 2, screen_size // 2 - 100))
	text2_rect = text2.get_rect(center=(screen_size // 2, screen_size // 2 + 100))
	screen.fill(BG_COLOR)
	screen.blit(text1, text1_rect)
	if order == 1:
		screen.blit(text2, text2_rect)
	else:
		screen.blit(text3, text2_rect)

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind(('', PORT))
	s.listen()

	print('[server] welcoming socket start at: %s:%s' % ('*', PORT))

	s.setblocking(False)
	inputs = [s]
	is_connected = False
	while not is_connected:
		readable, _, _ = select.select(inputs, [], [], 0.1)

		for sck in readable:
			if sck is s:
				conn, addr = sck.accept()
				conn.setblocking(True)
				is_connected = True

		for event in pygame.event.get():
			# when player closed the screen
			if event.type == pygame.QUIT:
				s.close()
				sys.exit()
			# when player changed screen size
			if event.type == pygame.VIDEORESIZE:
				screen_size = min(event.w, event.h)
				screen = pygame.display.set_mode(
					(screen_size, screen_size), pygame.RESIZABLE)
				update_ui_vars()
				main_menu.resize(screen_size, screen_size)
				help_menu.resize(screen_size, screen_size)
				text1_rect = text1.get_rect(center=(screen_size // 2, screen_size // 2 - 100))
				text2_rect = text2.get_rect(center=(screen_size // 2, screen_size // 2 + 100))
				screen.fill(BG_COLOR)
				screen.blit(text1, text1_rect)
				if order == 1:
					screen.blit(text2, text2_rect)
				else:
					screen.blit(text3, text2_rect)
			# when player press Esc key
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					print('[server] connection canceled.')
					s.close()
					return

		pygame.display.update()

	s.close()  # close welcoming socket to prevent other connection
	print('[server] connected by ' + str(addr))
	outdata = str(grid_size) + ' ' + str(order % 2 + 1)
	conn.sendall(outdata.encode())
	game_server()

	conn.close()

# WAIT CLIENT LOOP
def wait_client(value):
	global s, order
	text1 = font.render('Waiting for connection...', True, (255, 255, 255))
	text2 = font.render('You will be the X!', True, (255, 255, 255))
	text3 = font.render('You will be the O!', True, (255, 255, 255))
	text4 = font.render(
		'Can\'t find the game or it\'s already full.', True, (255, 255, 255))
	text1_rect = text1.get_rect(
		center=(screen_size // 2, screen_size // 2 - 100))
	text2_rect = text2.get_rect(
		center=(screen_size // 2, screen_size // 2 + 100))
	text4_rect = text4.get_rect(
		center=(screen_size // 2, screen_size // 2 + 100))
	screen.fill(BG_COLOR)
	screen.blit(text1, text1_rect)
	pygame.display.update()

	s.settimeout(10)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.connect((value, PORT))
	except:
		print('[client] connection falied.')
		screen.blit(text4, text4_rect)
		pygame.display.update()
		time.sleep(2)
		s.close()
		return

	print('[client] connected to (\'%s\', %s)' % (value, PORT))

	indata = s.recv(1024)
	if not indata:
		print('[client] server closed connection.')
	else:
		info = indata.decode().split()
		set_grid_size('', int(info[0]))
		order = int(info[1])
		if order == 1:
			screen.blit(text2, text2_rect)
		else:
			screen.blit(text3, text2_rect)
		pygame.display.update()
		time.sleep(1)
		game_client()

	s.close()

# GAME SERVER LOOP
def game_server():
	global screen_size, screen, conn
	is_game_running = True
	is_my_turn = True
	is_game_over = False
	game_restart()
	if order == 2:
		is_my_turn = False

	conn.setblocking(False)
	inputs = [conn]
	while is_game_running:
		readable, _, _ = select.select(inputs, [], [], 0.1)

		for sck in readable:
			if sck is conn:
				indata = sck.recv(1024)
				if not indata:
					print('[server] client closed connection.')
					return
				else:
					clicked = indata.decode().split()
					mark_space(int(clicked[0]), int(clicked[1]), order % 2 + 1)
					if is_winner(order % 2 + 1):
						is_game_over = True
					draw_figures()
					is_my_turn = True

		for event in pygame.event.get():
			# when player closed the screen
			if event.type == pygame.QUIT:
				conn.close()
				sys.exit()
			# when player changed screen size
			if event.type == pygame.VIDEORESIZE:
				screen_size = min(event.w, event.h)
				screen = pygame.display.set_mode(
					(screen_size, screen_size), pygame.RESIZABLE)
				update_ui_vars()
				main_menu.resize(screen_size, screen_size)
				help_menu.resize(screen_size, screen_size)
				screen.fill(BG_COLOR)
				draw_lines()
				draw_figures()
				if is_game_over:
					is_winner(1)
					is_winner(2)
			# when player clicked the screen
			if event.type == pygame.MOUSEBUTTONDOWN and is_my_turn and not is_game_over:
				# get mouse coordinates
				mouseX, mouseY = event.pos
				# transform screen coordinates to grid coordinates
				clicked_col = min(mouseX // space_size, grid_size - 1)
				clicked_row = min(mouseY // space_size, grid_size - 1)

				if is_space_available(clicked_row, clicked_col):
					mark_space(clicked_row, clicked_col, order)
					if is_winner(order):
						is_game_over = True
					draw_figures()
					outdata = str(clicked_row) + ' ' + str(clicked_col)
					conn.sendall(outdata.encode())
					is_my_turn = False
			# when player press R key
			if event.type == pygame.KEYDOWN and not is_grid_empty():
				if event.key == pygame.K_r:
					outdata = 'Restart'
					conn.sendall(outdata.encode())
					is_game_over = False
					game_restart()
					if order == 1:
						is_my_turn = True
					else:
						is_my_turn = False
			# when player press Esc key
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					print('[server] connection closed.')
					is_game_running = False

		pygame.display.update()

# GAME CLIENT LOOP
def game_client():
	global screen_size, screen, s
	is_game_running = True
	is_my_turn = True
	is_game_over = False
	game_restart()
	if order == 2:
		is_my_turn = False

	s.setblocking(False)
	inputs = [s]
	while is_game_running:
		readable, _, _ = select.select(inputs, [], [], 0.1)

		for sck in readable:
			if sck is s:
				indata = sck.recv(1024)
				if not indata:
					print('[client] server closed connection.')
					return
				elif indata.decode() == 'Restart':
					is_game_over = False
					game_restart()
					if order == 1:
						is_my_turn = True
					else:
						is_my_turn = False
				else:
					clicked = indata.decode().split()
					mark_space(int(clicked[0]), int(clicked[1]), order % 2 + 1)
					if is_winner(order % 2 + 1):
						is_game_over = True
					draw_figures()
					is_my_turn = True

		for event in pygame.event.get():
			# when player closed the screen
			if event.type == pygame.QUIT:
				s.close()
				sys.exit()
			# when player changed screen size
			if event.type == pygame.VIDEORESIZE:
				screen_size = min(event.w, event.h)
				screen = pygame.display.set_mode(
					(screen_size, screen_size), pygame.RESIZABLE)
				update_ui_vars()
				main_menu.resize(screen_size, screen_size)
				help_menu.resize(screen_size, screen_size)
				screen.fill(BG_COLOR)
				draw_lines()
				draw_figures()
				if is_game_over:
					is_winner(1)
					is_winner(2)
			# when player clicked the screen
			if event.type == pygame.MOUSEBUTTONDOWN and is_my_turn and not is_game_over:
				# get mouse coordinates
				mouseX, mouseY = event.pos
				# transform screen coordinates to grid coordinates
				clicked_col = min(mouseX // space_size, grid_size - 1)
				clicked_row = min(mouseY // space_size, grid_size - 1)

				if is_space_available(clicked_row, clicked_col):
					mark_space(clicked_row, clicked_col, order)
					if is_winner(order):
						is_game_over = True
					draw_figures()
					outdata = str(clicked_row) + ' ' + str(clicked_col)
					s.sendall(outdata.encode())
					is_my_turn = False
			# when player press Esc key
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					print('[client] connection closed.')
					is_game_running = False

		pygame.display.update()

# PYGAME_MENU STUFF
main_menu = pygame_menu.Menu('Main Menu', screen_size, screen_size, theme=pygame_menu.themes.THEME_BLUE)
help_menu = pygame_menu.Menu('Help', screen_size, screen_size, theme=pygame_menu.themes.THEME_BLUE)

main_menu.add.selector(
	'Grid Size: ',
	[('2x2', 2), ('3x3', 3), ('4x4', 4), ('5x5', 5), ('6x6', 6), ('7x7', 7), ('8x8', 8), ('9x9', 9)],
	onchange=set_grid_size
)
main_menu.add.button('Start a New Game', wait_server)
main_menu.add.text_input('Join a Game: ', default='IP Address', maxchar=16, input_underline='_', onreturn=wait_client)
main_menu.add.button(help_menu.get_title(), help_menu)
main_menu.add.button('Quit', pygame_menu.events.EXIT)
main_menu.enable()

help_menu.add.label('1. Player orders are randomly decided (X first).', max_char=-1, font_size=30)
help_menu.add.label('2. Only server can set the grid size.', max_char=-1, font_size=30)
help_menu.add.label('3. Only server can restart the game with R key.', max_char=-1, font_size=30)
help_menu.add.label('4. Both players can leave the game with Esc key.', max_char=-1, font_size=30)
help_menu.add.label('5. The window is resizable but only in square.', max_char=-1, font_size=30)
help_menu.add.button('Return to Menu', pygame_menu.events.BACK)

# PYGAME MAINLOOP
if __name__ == '__main__':
	while True:
		events = pygame.event.get()
		for event in events:
			# when player closed the screen
			if event.type == pygame.QUIT:
				pygame.quit()
				break
			# when player changed screen size
			if event.type == pygame.VIDEORESIZE:
				screen_size = min(event.w, event.h)
				screen = pygame.display.set_mode(
					(screen_size, screen_size), pygame.RESIZABLE)
				update_ui_vars()
				main_menu.resize(screen_size, screen_size)
				help_menu.resize(screen_size, screen_size)

		main_menu.update(events)
		main_menu.draw(screen)

		pygame.display.update()
