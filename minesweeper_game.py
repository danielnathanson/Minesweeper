import PySimpleGUI as sg
import random
import sys

class GameState:
    def __init__(self, width, height, mines, is_ai, ai_analysis):
        self.running = True
        self.has_won = None
        self.flag_count = 0
        self.width = width
        self.height = height
        self.mines = mines
        self.uncleared_count = width * height
        self.is_ai = is_ai
        self.ai_analysis = ai_analysis
        self.make_square_grid()

        self.multi_purpose_button = sg.Button(f'Mines Left: {self.mines}', pad = (0,0), key = "title", disabled = True, button_color= ('white', '#6F4E37'))
        self.play_again_button = sg.Button(f'Play again', pad = (0,0), key = "play_again", disabled = True, visible = False)
        self.window = sg.Window('Minesweeper', [[self.multi_purpose_button, self.play_again_button]] + self.square_grid, finalize = True)
    
    def make_square_grid(self):
        self.square_list = []
        self.square_grid = []
        
        #creates grid of squares
        for i in range(self.height):
            row = []
            for j in range(self.width):
                curr = sg.Button(self, pad = (0,0), right_click_menu = ['&Right', ['Flag']], image_filename = '~/desktop/myprojects/minesweeper/facingDown.png', key = f"b{i}{j}")
                self.make_square(curr, i, j)
                row.append(curr)
            self.square_list.extend(row)
            self.square_grid.append(row[:])

        for square in random.sample(self.square_list, k=self.mines):
            square.mined = True
        
        add1 = lambda x: x+1
        sub1 = lambda x: x-1
        no_change = lambda x: x
        func_list = [add1, sub1, no_change]
        for i in range(self.height):
            for j in range(self.width):
                self.square_grid[i][j].neighbors = []
                for f in func_list:
                    for g in func_list:
                        if not (f is no_change and g is no_change):
                            new_i = f(i)
                            new_j = g(j)
                            if (0 <= new_i < self.height) and (0 <= new_j < self.width):
                                self.square_grid[i][j].neighbors.append(self.square_grid[new_i][new_j])

    def make_square(self, square, i , j):
        square.flagged = False
        square.mined = False
        square.cleared = False
        square.id = f"{i}{j}"
        square.gamestate = self
    
    def play_game(self):
        if self.is_ai:
            self.play_ai_game()
        else:
            self.play_normal_game()
    
    def play_normal_game(self):
        while self.running:
            self.move_reader()
    
    def play_ai_game(self):
        flipper = True
        counter = 0
        while self.running:
            self.any_click = False
            if flipper:
                func = sg.Button.click_ai
            else:
                func = sg.Button.flag_ai

            for square in self.square_list:
                if square.cleared and (square.mines_near != 0):
                    func(square)
            
            if flipper and not self.any_click:
                untouched_square_list = [square for square in self.square_list if square.is_untouched()]
                random.choice(untouched_square_list).click()
                self.move_reader()
            
            flipper = not flipper
            counter += 1


    
    def move_reader(self):
        event, values = self.window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            self.running = False
            return
        
        square = self.window[event]

        if square.mined:
            self.has_won = False
            square.update(image_filename = '~/desktop/myprojects/minesweeper/mine.png')
            self.replay()
        else:
            mines_near = square.calc_mines_near()
            square.update(image_filename = f"~/desktop/myprojects/minesweeper/{mines_near}.png")
            square.clear()

            if self.uncleared_count == self.mines:
                self.has_won = True
                self.replay()

    def disable_all(self):
        for square in self.square_list:
            if square.is_untouched():
                square.disable()

    def replay(self):
        global ai_win_count, NUM_GAMES
        self.disable_all()
        self.running = False
    
        if self.has_won:
            ai_win_count += 1
            self.multi_purpose_button.update('You won!', button_color='Green')
        else:
            self.multi_purpose_button.update(f'You lost!', button_color='Red')
        self.play_again_button.update(disabled=False, visible=True)
        if NUM_GAMES > 0:
            NUM_GAMES -=1
        self.play_again_reader()

    def play_again_reader(self):
        if self.ai_analysis:
            self.window.close()
            return
        while True:
            event, values = self.window.read()

            if event == sg.WIN_CLOSED or event == 'Exit':
                self.window.close()
                return
            if event == 'play_again':
                self.window.close()
                break
        play_new_game()

def play_new_game(def_w=10, def_h=10, def_mine=10, ai_analysis = False):
    sg.theme('Default1')
    title =  [sg.Text('Generate your Minesweeper game!')]
    width_set = [sg.Text('board width '), sg.Input(str(def_w), key ='width_input')]
    height_set = [sg.Text('board height'), sg.Input(str(def_h), key ='height_input')]
    mine_set = [sg.Text('mines       '), sg.Input(str(def_mine), key = 'mine_input')]
    error_text = sg.Text('Height, Width, and Mines must all be integer values. Enter new values', visible = False)
    ai_checkbox = sg.Checkbox('AI mode', key = 'ai')
    submit = [sg.Button('Submit'), ai_checkbox, error_text]
    layout = [title, width_set, height_set, mine_set, submit]
    first_window = sg.Window('Minesweeper', layout)
    input_list = ['width_input', 'height_input', 'mine_input']

    if ai_analysis and NUM_GAMES > 0:
        new_game = GameState(def_w, def_h, def_mine, True, True)
        first_window.close()
        new_game.play_game()
        return
    event, values = first_window.read()  
    
    while not verify(values):
        error_text.update(visible=True)
        event, values = first_window.read()
    
    int_list = {input: int(values[input]) for input in input_list}
    
    if ai_checkbox.get():
        new_game = GameState(int_list['width_input'], int_list['height_input'], int_list['mine_input'], True, False)
    else:
        new_game = GameState(int_list['width_input'], int_list['height_input'], int_list['mine_input'], False, False)
    
    first_window.close()
    new_game.play_game()

def verify(values):
    input_list = ['width_input', 'height_input', 'mine_input']
    for input in input_list:
        try:
            int(values.get(input))
        except (ValueError, TypeError):
            return False
    return True

#Couldn't extend Button class so overrode methods
def disable(self):
    self.update(disabled = True)

def enable(self):
    self.update(disabled = False)

def handle_flag(self, event = None):
    if not self.cleared:
        if self.flagged:
            self.flagged = False
            self.gamestate.flag_count -= 1
            self.enable()
            self.update(image_filename = '~/desktop/myprojects/minesweeper/facingDown.png')
        else:
            self.flagged = True
            self.gamestate.flag_count += 1
            self.disable()
            self.update(image_filename = '~/desktop/myprojects/minesweeper/flagged.png')

        self.gamestate.multi_purpose_button.update(f'Mines left: {max(self.gamestate.mines - self.gamestate.flag_count, 0)}')

def clear(self):
    
    if self.is_untouched() and not self.mined:
        self.disable()
        self.cleared = True
        self.gamestate.uncleared_count -= 1
        #print(f"DEBUG: button id: {self.id} uncleared count: {self.gamestate.uncleared_count}")
        self.mines_near = self.calc_mines_near()
        self.update(image_filename = f"~/desktop/myprojects/minesweeper/{self.mines_near}.png")
        if self.mines_near == 0:
            for neighbor in self.neighbors:
                clear(neighbor)

def flag_ai(self):
    flagged_near = self.calc_flagged_near()
    untouched_near = self.calc_untouched_near()

    if untouched_near > 0 and ((self.mines_near - flagged_near) == untouched_near):
        for neighbor in self.neighbors:
            if neighbor.is_untouched():
                neighbor._RightClickMenuCallback()
                
def click_ai(self):
    flagged_near = self.calc_flagged_near()
    untouched_near = self.calc_untouched_near()

    if untouched_near > 0 and self.mines_near == flagged_near:
        for neighbor in self.neighbors:
            if neighbor.is_untouched():
                neighbor.click()
                self.gamestate.move_reader()
                self.gamestate.any_click = True

def calc_mines_near(self):
    return sum([neighbor.mined for neighbor in self.neighbors])

def calc_uncleared_near(self):
    return sum([(not neighbor.cleared and not neighbor.flagged) for neighbor in self.neighbors])

def calc_flagged_near(self):
    return sum([neighbor.flagged for neighbor in self.neighbors])

def calc_untouched_near(self):
    return sum([neighbor.is_untouched() for neighbor in self.neighbors])

def is_untouched(self):
    return not self.flagged and not self.cleared


sg.Button.disable = disable
sg.Button.enable = enable
sg.Button._RightClickMenuCallback = handle_flag
sg.Button.clear = clear
sg.Button.calc_mines_near = calc_mines_near
sg.Button.calc_uncleared_near = calc_uncleared_near
sg.Button.calc_flagged_near = calc_flagged_near
sg.Button.is_untouched = is_untouched
sg.Button.calc_untouched_near = calc_untouched_near
sg.Button.flag_ai = flag_ai
sg.Button.click_ai = click_ai


ai_win_count = 0
NUM_GAMES = 10


#returns the percent of games that the ai wins at that difficulty
def ai_analy_runner(width, height, mines):
    total = NUM_GAMES
    for i in range(NUM_GAMES):
        play_new_game(width, height, mines, True)
    return ai_win_count / total * 100

if __name__ == "__main__":
    try:
        arg1 = sys.argv[1]
        if sys.argv[1] == 'normal':
            play_new_game(10, 10, 10)
        elif sys.argv[1] == 'analysis':
            win_percent = ai_analy_runner(16, 16, 10)
            print(f"The AI won {win_percent}% of games at the specified difficulty")
        else:
            raise Exception()
    except:
        print("Error: provide 'normal' or 'analysis' as a command line argument")
