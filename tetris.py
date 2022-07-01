import pygame
import random
from shapes import shape_colors, shapes

pygame.font.init()

leaderboard = []
scores = []

try:
    with open('data.txt', 'r') as file:
        for j, i in enumerate(file.readlines()):
            if j == 0:
                highscore = int(i.split()[-1])
            elif 3 <= j <= 7:
                i = i.split()
                leaderboard.append((i[0], int(i[2])))
            elif j == 10:
                scores = i.split()
except FileNotFoundError:
    highscore = 0

leaderboard.sort(key=lambda x: x[1], reverse=True)
if len(scores) < 2000:
    scores += [0]*(2000-len(scores))
scores.sort(reverse=True)

s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 20 height per blo ck
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height


class Piece(object):
    rows = 20
    columns = 10

    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for x in range(10)] for x in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)]
                grid[i][j] = c
    return grid


def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(shape, grid):
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_positions = [j for sub in accepted_positions for j in sub]
    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False

    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def get_shape():
    global shapes, shape_colors
    return Piece(5, 0, random.choice(shapes))


def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width/2 - (label.get_width() / 2), top_left_y + play_height/2 - label.get_height()/2))


def draw_grid(surface, row, col):
    sx = top_left_x
    sy = top_left_y
    for i in range(row):
        pygame.draw.line(surface, (128, 128, 128), (sx, sy+i*30), (sx + play_width, sy + i * 30))
        for j in range(col):
            pygame.draw.line(surface, (128, 128, 128), (sx + j * 30, sy), (sx + j * 30, sy + play_height))


def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except Exception:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc


def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    pygame.draw.rect(surface, (70, 70, 70), (sx - 10, sy - 50, 180, 200), 0)

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*30, sy + i*30, 30, 30), 0)

    surface.blit(label, (sx + 10, sy - 30))


def user_inp(win):
    input_rect = pygame.Rect(s_width//2-70, s_height//2, 140, 40)
    base_font = pygame.font.Font(None, 32)
    user_text = ''
    color_active = pygame.Color('lightskyblue3')

    color_passive = pygame.Color('chartreuse4')
    color = color_passive

    active = False

    running = True

    font = pygame.font.SysFont('comicsans', 30)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = True
                else:
                    active = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                elif event.key == pygame.K_RETURN:
                    if len(user_text) >= 1:
                        running = False
                        break
                    else:
                        text = font.render('Input Your name', 1, (255, 0, 0))
                        win.blit(text, (s_width//2-70, s_height//2 + 40))
                        pygame.display.flip()
                else:
                    user_text += event.unicode

        win.fill((0, 0, 0))

        if active:
            color = color_active
        else:
            color = color_passive
        label = font.render('Congratulations on Entering the Leaderboard', 1,
                            (100, 100, 100))
        win.blit(label, (s_width//2-170, s_height//3))

        label = font.render('Please Enter your Name', 1,
                            (100, 100, 100))
        win.blit(label, (s_width//2-170, 2*s_height//5))
        pygame.draw.rect(win, color, input_rect)

        text_surface = base_font.render(user_text, True, (255, 255, 255))

        win.blit(text_surface, (input_rect.x+5, input_rect.y+5))
        input_rect.w = max(100, text_surface.get_width()+10)
        pygame.display.flip()
    return user_text


def draw_window(surface, highscore, leaderboard, score=0):
    surface.fill((0, 0, 0))

    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('TETRIS', 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    font2 = pygame.font.SysFont('comicsans', 30)
    text = font2.render(f'Score: {score}', 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100

    surface.blit(text, (sx+20, sy+160))

    text = font2.render(f'Highscore: {highscore}', 1, (255, 255, 255))
    surface.blit(text, (sx+20, sy+190))

    pygame.draw.rect(surface, (70, 70, 70), (sx - 550, sy - 50, 180, 200), 0)

    text = font2.render('Leaderboard', 1, (255, 255, 255))
    surface.blit(text, (sx-530, sy-30))

    for j, i in enumerate(leaderboard):
        if i[0] in [str(i) for i in range(5)]:
            text = font2.render('', 1, (255, 255, 255))
            surface.blit(text, (sx-530, sy+10+j*20))
        else:
            text = font2.render(f'{i[0][:4]} {i[1]}', 1, (255, 255, 255))
            surface.blit(text, (sx-530, sy+10+j*20))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j * 30, top_left_y + i * 30, 30, 30), 0)

    draw_grid(surface, 20, 10)
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)


def bins(arr, t):
    le, ri = 0, len(arr) - 1
    if t < arr[ri]:
        return -1
    while le <= ri:
        mid = (le + ri)//2
        if arr[mid] >= t and arr[mid+1] < t:
            return mid+1
        elif arr[mid] < t:
            ri = mid-1
        else:
            le = mid+1


def main(highscore, scores, leaderboard):
    global grid

    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    score = 0
    play_time = 0

    while run:
        play_time = clock.get_rawtime()
        fall_speed = 0.27 - round(play_time/20000, 2)

        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time/1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1

                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)

                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            k = clear_rows(grid, locked_positions)
            if k > 0:
                score += k*150 - 50
                highscore = max(score, highscore)

        draw_window(win, highscore, leaderboard, score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        if check_lost(locked_positions):
            run = False

    pygame.display.update()
    if len(leaderboard) < 5:
        leaderboard.append((user_inp(win)[:4].upper(), score))
        leaderboard += [('0', 0)]*(5-len(leaderboard))
        leaderboard.sort(key=lambda x: x[1], reverse=True)
    elif score > leaderboard[-1][1]:
        k = user_inp(win)[:4].upper()
        leaderboard.append((k, score))
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        leaderboard.pop()
    else:
        rank = bins(scores, score)
        rank = rank if rank != -1 else 'Unranked'
        win.fill((0, 0, 0))
        draw_text_middle(f"You rank: {rank}, Try Again", 40, (255, 255, 255), win)
        pygame.display.update()
        pygame.time.delay(3500)
    scores.append(score)
    scores.sort(reverse=True)
    scores = scores[:2000]
    scores = [str(i) for i in scores]
    return leaderboard[0][1], scores


def main_menu(highscore, scores):
    run = True
    while run:
        win.fill((0, 0, 0))
        draw_text_middle('Press any key to begin.', 60, (255, 255, 255), win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                highscore, scores = main(highscore, scores, leaderboard)
                with open('data.txt', 'w') as file:
                    file.write(f'highscore = {highscore}\n\n')
                    file.write('Leaderboard:\n')
                    for i in leaderboard:
                        file.write(f'{i[0][:4]} : {i[1]}\n')
                    file.write('\nAll Scores:\n')
                    file.write(' '.join(scores))
    pygame.quit()


win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')

main_menu(highscore, scores)
