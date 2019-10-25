import socket
import threading
import json
import chess
import stockfish
import platform
import os

stockfish_path = r""


def main():
    p = platform.system()
    if p == "Windows":
        stockfish_path = r"./stockfish_10_x64.exe"
    elif p == "Linux":
        os.system("chmod +x stockfish_10_x64")
        stockfish_path = r"./stockfish_10_x64"
    else:
        print("Your os is not supported yet! :/")
        input()
        exit(1)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 8000))
    s.listen(4)
    print("[*] AI has started")
    print("[*] AI waiting for connection...")
    while True:
        con, addr = s.accept()
        print("[*] {} has connected".format(addr[0]))
        threading.Thread(target=chessThread, args=(con, addr)).start()

def chessThread(con, addr):
    data = con.recv(1024).decode("utf-8")
    try:
        jsondata = json.loads(data)
    except json.JSONDecodeError as e:
        return
    try:
        print("[*] {} - starts a new game".format(addr[0]))
    except KeyError:
        return
    board = chess.Board()
    board.set_castling_fen("")
    moves = []
    while True:
        data = con.recv(1024).decode("utf-8")
        try:
            jsondata = json.loads(data)
        except json.JSONDecodeError:
            return
        if jsondata["type"] == "move":
            temp = str(jsondata["value"])
            arr = list(temp)
            jsondata["value"] = (arr[0]) + flipx(arr[1]) + (arr[2]) + flipx(arr[3])
            print("[*] {} - moved   {}".format(addr[0], jsondata["value"]))
            Nf3 = chess.Move.from_uci(jsondata["value"])
            board.push(Nf3)
        elif jsondata["type"] == "getmove":
            engine = stockfish.Stockfish(stockfish_path)
            engine.set_fen_position(board.fen())
            bestmove = engine.get_best_move()
            print("[*] {} - getmove {}".format(addr[0], bestmove))
            con.sendall(bestmove.encode("utf-8"))

def flipx(n):
    if(n == "1"):
        return "8"
    elif(n=="2"):
        return "7"
    elif(n == "3"):
        return "6"
    elif(n == "4"):
        return "5"
    elif(n == "5"):
        return "4"
    elif(n == "6"):
        return "3"
    elif(n == "7"):
        return "2"
    elif(n == "8"):
        return "1"
    else:
        return "0"

if __name__ == '__main__':
    main()
