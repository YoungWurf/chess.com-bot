from urllib.parse import urlparse
import os
import time
from numpy import array
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from stockfishpy import *
import getpass
import chess
import chess.pgn
from selenium.webdriver.common.by import By

def get_moves_to_pgn(driver,move_number,color):
    new_moves=''
    while (True):
            try:
                elements = driver.find_elements_by_class_name('move')
                last_moves=''
                if(len(elements)-1 <= move_number):
                    temp_last_moves=[]
                    for move in elements:
                        last_moves+=move.text.strip()
                        temp_last_moves.append(last_moves)
                        last_moves=temp_last_moves[len(temp_last_moves)-1]
                    break
            except:
                pass
    new_moves +=last_moves+'\n'
    with open("moves.txt", "w") as text_file:
        text_file.write("%s" % new_moves)

def get_best_move():
    chessEngine = Engine('./stockfish_13_linux_x64', param={'Threads': 1, 'Ponder': None})
    file = 'moves.txt'
    with open(file) as f:
        board_pgn = chess.pgn.read_game(f)
    board_pgn=board_pgn.end()
    board=board_pgn.board()
    try:
        print(board)
        chessEngine.setposition(board.fen())
        chessEngine.uci()
        chessEngine.isready()
        chessEngine.ucinewgame()
        move = chessEngine.bestmove()
        print(move["bestmove"])
        return move["bestmove"]
    except:
        return "none"

def find_board_size(driver):
    board = driver.find_element_by_class_name("board-layout-chessboard.board-board")
    style=board.get_attribute("style")
    size=style.split(";")
    size=size[0].split(":")
    size_number=str(size[1])
    size_number=size_number.replace("px","")
    size_number=size_number.replace(" ","")
    size_number=int(size_number)
    return size_number

def draw_board_coordinates(size):
    cell_size=size/8
    board=[[[0 for _ in range(2)] for _ in range(8)] for _ in range(8)]
    for i in range(8):
        for j in range(8):
            for k in range(2):
                if k ==0:
                    if j ==0:
                        board[i][j][k]=cell_size
                    elif j==8:
                        board[i][j][k]=cell_size-20
                    else:
                        board[i][j][k]=(j+1)*cell_size
                else:
                    if i==0:
                        board[i][j][k]=cell_size
                    #if i==8:
                    #   board[i][j][k]=cell_size-20
                    else:
                        board[i][j][k]=cell_size*(i+1)
    return board

def automove(driver,x,y,new_x,new_y):
    board = driver.find_element_by_class_name("board-layout-chessboard.board-board")
    action_chains = ActionChains(driver)
    action_chains.move_to_element_with_offset(board, x, y).click().perform()
    time.sleep(2)
    action_chains.move_to_element_with_offset(board, new_x, new_y).click().perform()
    time.sleep(2)
    action_chains.move_to_element_with_offset(board, new_x, new_y).click().perform() 

def letter_to_int(letter,color):
    if color=="white":
        array_letter=["a","b","c","d","e","f","g","h"]
        return array_letter.index(letter)
    elif color=='black':
        array_letter=['h','g','f','e','d','c','b','a']
        return abs(array_letter.index(letter)-8)

def get_color(driver,username):
    names=[]
    components=driver.find_elements_by_class_name("user-username.username")
    for component in components:
        names.append(component.text)
    if names[0]==username:
        return "white"
    else:
        return "black"
        
def get_guest_name(driver):
    return driver.find_element_by_xpath("//*[@id='board-layout-player-bottom']/div/div[2]/div/a[1]").text

def apply_settings(driver):
    driver.find_element_by_class_name("board-layout-icon.icon-font-chess.circle-gearwheel").click()
    time.sleep(15)
    print("Apply settings('white always on bottom' and piece notation to 'text') manually and wait...\n")

def start_guest_game():
    chrome_options = Options()
    chrome_options.add_argument("/home/"+str(os.getlogin())+"/.config/google-chrome/Default")
    driver=webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    driver.get("https://www.chess.com/play/online")
    time.sleep(5)
    driver.find_element_by_xpath("//*[@id='board-layout-sidebar']/div/div[2]/div/div[1]/div[1]/div/button").click()
    time.sleep(5)
    driver.find_element_by_xpath("//*[@id='guest-button']").click()
    time.sleep(5)
    apply_settings(driver)
    time.sleep(5)
    driver.find_element_by_xpath("//*[@id='board-layout-sidebar']/div/div[2]/div/div[1]/div[1]/div/button").click()
    return driver

def play_as_guest():
    driver=start_guest_game()
    time.sleep(5)
    guest_name=get_guest_name(driver)
    guest_color=get_color(driver,guest_name)
    size=find_board_size(driver)
    board=draw_board_coordinates(size)
    print(guest_name)
    print(guest_color)
    move=0
    time.sleep(5)
    while(True):
            move+=1
            if guest_color=='white' and move==1:
                bst='d2d4'
            else:
                get_moves_to_pgn(driver,move,guest_color)
                bst=get_best_move()
                if bst=="none":
                    break
            list1=[]
            list1[:0]=bst
            x=int(board[abs(int(list1[1])-8)][int(letter_to_int(list1[0],guest_color))][0])
            y=int(board[abs(int(list1[1])-8)][int(letter_to_int(list1[0],guest_color))][1])
            new_x=int(board[abs(int(list1[3])-8)][int(letter_to_int(list1[2],guest_color))][0])
            new_y=int(board[abs(int(list1[3])-8)][int(letter_to_int(list1[2],guest_color))][1])
            automove(driver,x,y,new_x,new_y)
            time.sleep(5)

def login(my_username,my_password):
    chrome_options = Options()
    chrome_options.add_argument("/home/"+str(os.getlogin())+"/.config/google-chrome/Default")
    driver=webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://www.chess.com/login")
    driver.maximize_window()
    time.sleep(5)
    driver.find_element_by_name("_username").send_keys(my_username)
    time.sleep(1)
    driver.find_element_by_name("_password").send_keys(my_password)
    time.sleep(1)
    driver.find_element_by_name("_password").send_keys("\ue007")
    time.sleep(5)
    return driver

def start_game(driver):
    driver.get("https://www.chess.com/play/online")
    time.sleep(5)
    driver.find_element_by_xpath("//*[@id='board-layout-sidebar']/div/div[2]/div/div[1]/div[1]/div/button").click()

def play_with_account(username,password):
    driver=login(username,password)
    start_game(driver)
    time.sleep(5)
    name=get_guest_name(driver)
    color=get_color(driver,name)
    size=find_board_size(driver)
    board=draw_board_coordinates(size)
    move=0
    time.sleep(5)
    while(True):
            move+=1
            if color=='white' and move==1:
                bst='d2d4'
            else:
                get_moves_to_pgn(driver,move,color)
                bst=get_best_move()
                if bst=="none":
                    break
            list1=[]
            list1[:0]=bst
            x=int(board[abs(int(list1[1])-8)][int(letter_to_int(list1[0],color))][0])
            y=int(board[abs(int(list1[1])-8)][int(letter_to_int(list1[0],color))][1])
            new_x=int(board[abs(int(list1[3])-8)][int(letter_to_int(list1[2],color))][0])
            new_y=int(board[abs(int(list1[3])-8)][int(letter_to_int(list1[2],color))][1])
            automove(driver,x,y,new_x,new_y)
            time.sleep(5)

def start():
    print("You will need to enable from settings 1)White always on bottom and 2)Piece Notation to Text\n")
    print("If you want to use this script as a guest type 'g' ,for cheating with your account type 'i am dum dum' \n")
    user_input=input()
    if user_input =='g':
        play_as_guest()
    elif user_input=='i am dum dum':
        print("\n Remember you are using this on your own risk,you may lose your account you dum dum!\n")
        print("\nType the username or email of your account:")
        username=input()
        print("\nType your password:")
        password=input()
        play_with_account(username,password)
    else:
        print("Huh you did not cheat,you think you are a better person now?\n")

def main():
    start()

main()
