import streamlit as st
import streamlit.components.v1 as components
import random

st.set_page_config(page_title="Mini Tetris - 12 Lines", layout="centered")
st.markdown(
    """
    <style>
      header {visibility: hidden;}
      .stApp { background-color: #f0f0f0; }
      body { margin: 0; background: #f0f0f0; }
    </style>
    """,
    unsafe_allow_html=True,
)

html_code = """
<html>
<head>
  <meta charset="UTF-8">
  <title>Mini Tetris - 12 Lines</title>
  <style>
    body {
      background: #f0f0f0;
      margin: 0;
      overflow: hidden;
      font-family: sans-serif;
    }
    /* キー操作説明を画面上部に表示 */
    #instructions {
      text-align: center;
      font-size: 1.5em;
      color: #333;
      margin-top: 10px;
      margin-bottom: 10px;
    }
    /* ゲームコンテナ（キャンバス部分） */
    #game-container {
      position: relative;
      width: 240px;
      margin: auto;
    }
    /* メインキャンバス：背景は薄いグレー、枠はやや濃いグレー */
    canvas#tetris {
      display: block;
      background: #f0f0f0;
      border: 2px solid #888;
    }
    /* 次ピースプレビュー：枠なし、背景は薄いグレー */
    canvas#next {
      position: absolute;
      top: 0;
      right: -90px;
      background: #f0f0f0;
      border: none;
    }
    /* 残りライン数表示（コントロールの上に1行空けて中央揃え） */
    #line-count {
      text-align: center;
      font-size: 1.2em;
      color: #333;
      margin-top: 10px;
    }
    /* コントロールボタン（START, RESET）：文字表示のみ（枠なし） */
    #controls {
      text-align: center;
      margin-top: 10px;
    }
    #controls button {
      padding: 8px 16px;
      font-size: 1em;
      cursor: pointer;
      background: none;
      border: none;
      color: #333;
      margin: 0 5px;
    }
  </style>
</head>
<body>
  <div id="instructions">←　→　Ｑ　Ｒ　↓</div>
  <div id="game-container">
    <canvas id="tetris" width="240" height="400"></canvas>
    <canvas id="next" width="80" height="80"></canvas>
  </div>
  <div id="line-count">Lines to Clear: 12</div>
  <div id="controls">
    <button id="start-btn" onclick="startGame()">START</button>
    <button id="reset-btn" onclick="resetGame()">RESET</button>
  </div>
  <script>
    // ----- 基本関数 -----
    function createMatrix(w, h) {
      const matrix = [];
      while (h--) {
        matrix.push(new Array(w).fill(0));
      }
      return matrix;
    }
    function createPiece(type) {
      if (type === 'T') {
        return [
          [0,1,0],
          [1,1,1],
          [0,0,0]
        ];
      } else if (type === 'O') {
        return [
          [1,1],
          [1,1]
        ];
      } else if (type === 'L') {
        return [
          [0,1,0],
          [0,1,0],
          [0,1,1]
        ];
      } else if (type === 'J') {
        return [
          [0,1,0],
          [0,1,0],
          [1,1,0]
        ];
      } else if (type === 'I') {
        return [
          [0,1,0,0],
          [0,1,0,0],
          [0,1,0,0],
          [0,1,0,0]
        ];
      } else if (type === 'S') {
        return [
          [0,1,1],
          [1,1,0],
          [0,0,0]
        ];
      } else if (type === 'Z') {
        return [
          [1,1,0],
          [0,1,1],
          [0,0,0]
        ];
      }
    }
    function randomPiece() {
      const pieces = 'TJLOSZI';
      return pieces[pieces.length * Math.random() | 0];
    }

    // ----- カラー設定 -----
    // ブロックの色はすべて淡い青 (#ADD8E6)
    const colors = [
      null,
      '#ADD8E6',
      '#ADD8E6',
      '#ADD8E6',
      '#ADD8E6',
      '#ADD8E6',
      '#ADD8E6',
      '#ADD8E6'
    ];

    // ----- ゲーム画面描画 -----
    const canvas = document.getElementById("tetris");
    const context = canvas.getContext("2d");
    context.scale(20, 20);
    function drawMatrix(matrix, offset, ctx) {
      matrix.forEach((row, y) => {
        row.forEach((value, x) => {
          if (value !== 0) {
            ctx.fillStyle = colors[value];
            ctx.fillRect(x + offset.x, y + offset.y, 1, 1);
          }
        });
      });
    }
    function draw() {
      context.fillStyle = "#f0f0f0";
      context.fillRect(0, 0, canvas.width, canvas.height);
      drawMatrix(arena, {x:0, y:0}, context);
      drawMatrix(player.matrix, player.pos, context);
    }

    // ----- 次ピースプレビュー -----
    const nextCanvas = document.getElementById("next");
    const nextContext = nextCanvas.getContext("2d");
    nextContext.scale(20, 20);
    function updateNext() {
      nextContext.fillStyle = "#f0f0f0";
      nextContext.fillRect(0, 0, nextCanvas.width, nextCanvas.height);
      if (nextPiece) {
        const matrix = nextPiece;
        const offset = {
          x: Math.floor((nextCanvas.width/20 - matrix[0].length)/2),
          y: Math.floor((nextCanvas.height/20 - matrix.length)/2)
        };
        drawMatrix(matrix, offset, nextContext);
      }
    }

    // ----- 衝突判定 -----
    function collide(arena, player) {
      const m = player.matrix;
      const o = player.pos;
      for (let y = 0; y < m.length; ++y) {
        for (let x = 0; x < m[y].length; ++x) {
          if (m[y][x] !== 0 &&
              (arena[y + o.y] && arena[y + o.y][x + o.x]) !== 0) {
            return true;
          }
        }
      }
      return false;
    }

    // ----- ピース固定・ラインクリア -----
    function merge(arena, player) {
      player.matrix.forEach((row, y) => {
        row.forEach((value, x) => {
          if (value !== 0) {
            arena[y + player.pos.y][x + player.pos.x] = value;
          }
        });
      });
    }
    function arenaSweep() {
      let rowCount = 0;
      outer: for (let y = arena.length - 1; y >= 0; y--) {
        for (let x = 0; x < arena[y].length; x++) {
          if (arena[y][x] === 0) {
            continue outer;
          }
        }
        arena.splice(y, 1)[0].fill(0);
        arena.unshift(new Array(arena[0].length).fill(0));
        rowCount++;
        y++;
      }
      if (rowCount > 0) {
        player.linesCleared += rowCount;
        updateLineCount();
        if (player.linesCleared >= 12) {
          // 12ラインクリアで全表示を消去
          document.body.innerHTML = "";
          document.body.style.background = "#f0f0f0";
          return;
        }
      }
    }

    // ----- プレイヤー操作 -----
    const player = {
      pos: {x: 0, y: 0},
      matrix: null,
      linesCleared: 0
    };
    let nextPiece = createPiece(randomPiece());
    function playerReset() {
      player.matrix = nextPiece;
      nextPiece = createPiece(randomPiece());
      updateNext();
      player.pos.y = 0;
      player.pos.x = ((arena[0].length / 2) | 0) - ((player.matrix[0].length / 2) | 0);
      if (collide(arena, player)) {
        arena.forEach(row => row.fill(0));
        player.linesCleared = 0;
        updateLineCount();
        alert("Game Over!");
        cancelAnimationFrame(updateId);
      }
    }
    function playerDrop() {
      player.pos.y++;
      if (collide(arena, player)) {
        player.pos.y--;
        merge(arena, player);
        playerReset();
        arenaSweep();
      }
      dropCounter = 0;
    }
    function playerMove(dir) {
      player.pos.x += dir;
      if (collide(arena, player)) {
        player.pos.x -= dir;
      }
    }
    function playerRotate(dir) {
      const pos = player.pos.x;
      let offset = 1;
      rotate(player.matrix, dir);
      while (collide(arena, player)) {
        player.pos.x += offset;
        offset = -(offset + (offset > 0 ? 1 : -1));
        if (offset > player.matrix[0].length) {
          rotate(player.matrix, -dir);
          player.pos.x = pos;
          return;
        }
      }
    }
    function rotate(matrix, dir) {
      for (let y = 0; y < matrix.length; ++y) {
        for (let x = 0; x < y; ++x) {
          [matrix[x][y], matrix[y][x]] = [matrix[y][x], matrix[x][y]];
        }
      }
      if (dir > 0) {
        matrix.forEach(row => row.reverse());
      } else {
        matrix.reverse();
      }
    }

    // ----- 更新ループ -----
    let dropCounter = 0;
    let dropInterval = 1000;
    let lastTime = performance.now();
    let updateId;
    const arena = createMatrix(12, 20);
    function update(time) {
      const deltaTime = time - lastTime;
      lastTime = time;
      dropCounter += deltaTime;
      if (dropCounter > dropInterval) {
        playerDrop();
      }
      draw();
      updateId = requestAnimationFrame(update);
    }

    // ----- ラインカウント表示 -----
    function updateLineCount() {
      const remaining = 12 - player.linesCleared;
      document.getElementById("line-count").textContent = "Lines to Clear: " + remaining;
    }

    // ----- キー操作 -----
    document.addEventListener('keydown', event => {
      if (event.keyCode === 37) {         // 左矢印
        playerMove(-1);
      } else if (event.keyCode === 39) {  // 右矢印
        playerMove(1);
      } else if (event.keyCode === 40) {  // 下矢印
        playerDrop();
      } else if (event.keyCode === 81) {  // Q（反時計回り）
        playerRotate(-1);
      } else if (event.keyCode === 82) {  // R（時計回り）
        playerRotate(1);
      }
    });

    // ----- ゲーム開始とリセット -----
    function startGame() {
      player.linesCleared = 0;
      updateLineCount();
      playerReset();
      updateId = requestAnimationFrame(update);
    }
    function resetGame() {
      cancelAnimationFrame(updateId);
      arena.forEach(row => row.fill(0));
      player.linesCleared = 0;
      updateLineCount();
      playerReset();
      updateId = requestAnimationFrame(update);
    }

    // ----- 初期化 -----
    function init() {
      arena.forEach(row => row.fill(0));
      player.linesCleared = 0;
      updateLineCount();
      playerReset();
    }
    init();
  </script>
</body>
</html>
"""

components.html(html_code, height=500)
