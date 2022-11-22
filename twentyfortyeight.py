# --- imports ---
import random
import os
import copy

# --- variables ---

emptyChar = "⬜"
boardX = 4
boardY = 4


# --- functions ---
def DecryptBoard(boardList):
    finalString = ""
    for i in boardList:
        finalString += "\n"
        for e in i:
            try:
                if type(int(e)) is int:
                    eLen = len(str(e)) / 2
                    finalString += f"‖{e}‖"
            except ValueError:
                finalString += f"{e}"
    return finalString


def GetEmptyTiles(boardList):
    List = boardList
    returnList = []
    for y in range(boardY):
        for x in range(boardX):
            if boardList[y][x] == emptyChar:
                returnList.append([y, x])
    return returnList


class TwentyFortyEight:
    def __init__(self, consoleOn):  # consoleOn is a bool that allows printing or not printing
        # --- Starting variables ---
        self.score = 0
        self.dead = False
        # --- Print starting game ---
        random.seed(random.random())
        if consoleOn:
            print("This is 2048! Read rules online.")
            print("Initializing...")

        # --- Generate boardList ---
        rows = []
        for y in range(boardY):
            rows.append("⬜")
        columns = []
        for x in range(boardX):
            columns.append(rows.copy())
        self.boardList = columns
        for i in range(2):  # Create two twos in the board
            randomNumber = random.randint(1, 2)
            if randomNumber == 1:
                randomEmptyTile = GetEmptyTiles(self.boardList)[random.randrange(0, len(GetEmptyTiles(self.boardList)))]
                self.boardList[randomEmptyTile[0]][randomEmptyTile[1]] = "2"
            elif randomNumber == 2:
                randomEmptyTile = GetEmptyTiles(self.boardList)[random.randrange(0, len(GetEmptyTiles(self.boardList)))]
                self.boardList[randomEmptyTile[0]][randomEmptyTile[1]] = "4"
        # --- delete what generated the list ---
        del columns
        del rows
        del randomEmptyTile
        # --- decrypt boardList ---
        if consoleOn:
            print(DecryptBoard(self.boardList))

        # --- start the game ---
        if consoleOn:
            self.Start()

    def Start(self):  # This is the main game loop function
        invalidAnswer = False
        controlFunctions = {"down": self.Down, "up": self.Up, "left": self.Left, "right": self.Right}
        while not self.dead and not invalidAnswer:

            answer = input("Up, down, left or right?").lower()
            if answer != "up" and answer != "down" and answer != "left" and answer != "right":
                print("That is not a valid answer!")
                invalidAnswer = True
            else:
                answerFunction = controlFunctions.get(answer.lower())
                answerFunction()
            print(DecryptBoard(self.boardList))
            print(f"Score: {self.score}")
            self.CheckDead()
        if invalidAnswer:
            self.Start()
        if self.dead:
            print(f"Game over! Final score: {self.score}")

    def Down(self):
        self.MoveTile((1, 0),
                      self.boardList, True)
        # Moves tile down (note: tuple order is (y,x)) (Also note: down is 1 and up is -1)

    def Right(self):
        self.MoveTile((0, 1), self.boardList, True)
        # Note that right is 1 and left is -1

    def Left(self):
        self.MoveTile((0, -1), self.boardList, True)

    def Up(self):
        self.MoveTile((-1, 0), self.boardList, True)

    def MoveTile(self, direction, boardList,
                 mainBoard: bool):  # main board is to check if the board is the main board. This is to check the scoring
        movedItems = 0  # calculated to create new tiles
        if direction[0] > 0 or direction[1] > 0:
            for i in range(4):  # Push tiles down
                for y in range(boardY):
                    for x in range(boardX):
                        if boardList[y][x] != emptyChar:
                            try:
                                if boardList[y + direction[0]][x + direction[1]] == emptyChar:
                                    char = boardList[y][x]
                                    boardList[y][x] = emptyChar
                                    boardList[y + direction[0]][x + direction[1]] = char
                                    movedItems += 1
                            except IndexError:
                                pass
            for y in reversed(range(
                    boardY)):  # add tiles together (Note: The X and Y are reversed to calculate the merging properly based on the direction)
                for x in reversed(range(boardX)):
                    if boardList[y][x] != emptyChar:
                        try:
                            if boardList[y + direction[0]][x + direction[1]] == str(boardList[y][x]):
                                char = boardList[y][x]
                                boardList[y][x] = emptyChar
                                boardList[y + direction[0]][x + direction[1]] = str(
                                    int(char) * 2)  # multiplies the tile by 2 when merging
                                movedItems += 1
                                if mainBoard:
                                    self.score += int(char) * 2

                        except IndexError:
                            pass
            for i in range(4):  # Push tiles down again
                for y in range(boardY):
                    for x in range(boardX):
                        if boardList[y][x] != emptyChar:
                            try:  # try catch function to check if the index goes out of the board
                                if boardList[y + direction[0]][x + direction[1]] == emptyChar:
                                    char = boardList[y][x]
                                    boardList[y][x] = emptyChar
                                    boardList[y + direction[0]][x + direction[1]] = char
                                    movedItems += 1
                            except IndexError:
                                pass

        # left and up directions
        elif direction[0] < 0 or direction[1] < 0:
            for i in range(boardX + boardY):  # calculates pushing the tiles multiple times
                for y in range(boardY):
                    for x in range(boardX):
                        if boardList[y][x] != emptyChar:  # checks if the current tile is empty
                            if (y != 0 and direction[0] != 0) or (x != 0 and direction[1] != 0):
                                # special case where tiles could move off of the board because we are using negative list indexes
                                if boardList[y + direction[0]][x + direction[1]] == emptyChar:
                                    char = boardList[y][x]
                                    boardList[y][x] = emptyChar
                                    boardList[y + direction[0]][x + direction[1]] = char
                                    movedItems += 1
            for y in range(boardY):  # adds the tiles together
                for x in range(boardX):
                    if boardList[y][x] != emptyChar:
                        if boardList[y + direction[0]][x + direction[1]] == boardList[y][x]:
                            if (y != 0 and direction[0] != 0) or (x != 0 and direction[1] != 0):
                                char = boardList[y][x]
                                boardList[y][x] = emptyChar
                                boardList[y + direction[0]][x + direction[1]] = str(int(char) * 2)
                                movedItems += 1
                                if mainBoard:
                                    self.score += int(char) * 2
            for i in range(boardX + boardY):  # calculates pushing the tiles again
                for y in range(boardY):
                    for x in range(boardX):
                        if boardList[y][x] != emptyChar:  # checks if the current tile is empty
                            if (y != 0 and direction[0] != 0) or (x != 0 and direction[1] != 0):
                                # special case where tiles could move off of the board because we are using negative list indexes
                                if boardList[y + direction[0]][x + direction[1]] == emptyChar:
                                    char = boardList[y][x]
                                    boardList[y][x] = emptyChar
                                    boardList[y + direction[0]][x + direction[1]] = char
                                    movedItems += 1

        # create a new tile
        if movedItems != 0:
            randomEmptyTile = GetEmptyTiles(boardList)[random.randrange(0, len(GetEmptyTiles(boardList)))]
            boardList[randomEmptyTile[0]][randomEmptyTile[1]] = "2"

    def CheckDead(self):
        newBoard = copy.deepcopy(self.boardList)  # copy of board to check if game is dead
        check = 0
        self.MoveTile((1, 0), newBoard, False)  # check down
        if newBoard == self.boardList:
            check += 1
        newBoard = copy.deepcopy(self.boardList)  # copy of board to check if game is dead
        self.MoveTile((0, 1), newBoard, False)  # check right
        if newBoard == self.boardList:
            check += 1
        newBoard = copy.deepcopy(self.boardList)  # copy of board to check if game is dead
        self.MoveTile((-1, 0), newBoard, False)  # check up
        if newBoard == self.boardList:
            check += 1
        newBoard = copy.deepcopy(self.boardList)  # copy of board to check if game is dead
        self.MoveTile((0, -1), newBoard, False)  # check left
        if newBoard == self.boardList:
            check += 1
        if check == 4:
            self.dead = True

        return check
