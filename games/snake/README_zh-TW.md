# 貪食蛇

## 概觀

![Imgur](https://i.imgur.com/aVDPwWP.gif)

控制蛇的移動，讓牠吃到食物。每吃到一個食物，蛇身就會增長一段。盡可能地吃到最多食物。

## 執行

* 手動模式：`python MLGame.py snake -m`
    * 控制蛇的方向：方向鍵
    * 蛇一個影格移動一步，可以加入 `-f <FPS>` 來降低蛇的移動速度
* 機器學習模式：`python MLGame.py snake -i ml_play_template.py`

## 詳細遊戲資訊

### 座標系統

與打磚塊遊戲一樣

### 遊戲區域

300 \* 300 像素

### 遊戲物件

#### 蛇

* 蛇由一系列正方形構成。每一個正方形的大小是 10 \* 10 像素
* 蛇頭顏色是綠色的，而蛇身皆為白色
* 蛇頭初始位置在 (40, 40)，而蛇身依序在 (40, 30)、(40, 20)、(40, 10)
* 蛇初始移動方向是向下，每一個影格移動 10 個像素
* 當蛇吃到食物時，蛇身會增長一個

#### 食物

* 食物是 10 \* 10 像素大小的正方形，但是其樣貌為紅色圓形
* 食物的位置隨機決定，xy 座標範圍皆為 0 ~ 290，以 10 為一單位決定

## 撰寫玩遊戲的程式

範例程式在 [`ml/ml_play_template.py`](ml/ml_play_template.py)。

### 函式

以下函式定義在 [`games/snake/communication`](communication.py) 模組中

* `ml_ready()`：通知遊戲端已經準備好接收訊息了
* `get_scene_info()`：從遊戲端接接收遊戲場景資訊 `SceneInfo`
* `send_command(frame, command)`：傳送指令給遊戲端
    * `frame`：標記這個指令是給哪一個影格的。這個值必須跟收到的 `SceneInfo.frame` 一樣
    * `command`：控制蛇的指令，必須是 `SnakeAction` 之一

### 資料結構

以下資料結構已經先匯入到 [`games/snake/communication`](communication.py) 模組中，可以透過此模組匯入

#### `SceneInfo`

儲存遊戲場景的資訊。定義在 [`game/gamecore.py`](game/gamecore.py) 中

* `frame`：標記這個 `SceneInfo` 紀錄的是第幾影格的場景資訊
* `status`：目前的遊戲狀態，會是 `GameStatus` 其中之一
* `snake_head`：蛇頭的位置。為一個 `(x, y)` tuple
* `snake_body`：蛇身的位置。為一個 list，從蛇頭後一個蛇身依序紀錄到蛇尾，裡面每一個元素都是 `(x, y)` tuple
* `food`：食物的位置。為一個 `(x, y`) tuple
* `command`：依據這個影格的場景資訊而決定的指令，用於產生紀錄檔

#### `GameStatus`

遊戲狀態。定義在 [`game/gamecore.py`](game/gamecore.py)

* `GAME_ALIVE`：蛇還活著
* `GAME_OVER`：蛇撞到牆或是撞到自己

#### `SnakeAction`

控制蛇的移動方向。定義在 [`game/gameobject.py`](game/gameobject.py)

* `UP`：蛇頭向上
* `DOWN`：蛇頭向下
* `LEFT`：蛇頭向左
* `RIGHT`：蛇頭向右
* `NONE`：保持前進方向
