from model.board import Board

board = Board(20, 20)
board.generate_maze()

for i in range(0, 20):
    for j in range (0, 20):
        if board.check_goal(j, i):
            print('G ', end='')
        elif board.can_be_traversed(j, i): 
            print('  ', end='')
        else:
            print('# ', end='')
    print('\n')
