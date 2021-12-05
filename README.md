# python-socket-TicTacToe
A simple game using socket programming.

## 開發環境
OS: Windows 10 Pro

Build: [19042.1348](https://support.microsoft.com/en-us/topic/november-9-2021-kb5007186-os-builds-19041-1348-19042-1348-and-19043-1348-033ee59c-e9b7-4eaf-8ee7-b3512bb1a0aa)

Programming Language: Python

Version: [Python 3.9.9](https://www.python.org/downloads/release/python-399/)

Modules:

[NumPy 1.21.4](https://numpy.org/)

[Pygame 2.1.0](https://pygame.org/)

[Pygame menu 4.2.0](https://pygame.org/project/3165/)

## 參考資料
[Socket Programming in Python (Guide)](https://realpython.com/python-sockets/)

[Python的非阻塞式（non-blocking）socket通訊程式（二）：使用select程式庫](https://swf.com.tw/?p=1201)

[Tic-tac-toe using Python and Pygame](https://github.com/AlejoG10/python-tictactoe-yt)

[Menus - Pygame Tutorial](https://youtu.be/0RryiSjpJn0)

## 程式簡介
* 有GUI的圈叉遊戲，可以用來打發時間。
* 至少且最多只能有2名玩家，其中一邊當server，另一邊當client。
* 程式主畫面

![](https://i.imgur.com/N3ti5Af.png)
* 規則說明

![](https://i.imgur.com/TF7Kr5j.png)
* 遊戲畫面

![](https://i.imgur.com/7IdeZpN.png)

## 技術細節
* 採用非常簡單的TCP連線，所以除非server端有公共IP，否則只能在區域網玩。
* 程式流程圖
![](https://i.imgur.com/51t3dBq.jpg)
* 當server `accept()`成功時，就關閉welcoming socket，防止他人進入。
* 每個回到主畫面的動作都會關閉socket。
* 使用`select()` system call，使socket函式不會讓程式卡住。
    1. `select()`每過一段時間就會檢查是否有資料送進socket，如果有再使用`recv()`來接收。
    2. 如果不使用non-blocking的話，server在等待`accept()`時程式會卡住，不可能取消。此外，在遊戲中等待對手決定下一步時程式會被`recv()`卡住，不能拖動視窗、調整視窗大小以及中斷連線，server也不能發送重玩指令給client。
    3. client的`connect()`我沒有設計成non-blocking，反正超時之後就會回到主畫面。
* client在收到server的格子數量與先後順序訊息後，會先停1秒才進入遊戲畫面，好讓玩家知道自己是圈還是叉。
