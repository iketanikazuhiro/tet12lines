import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Mini Tetris - 12 Lines", layout="centered")
st.markdown(
    """
    <style>
      header {visibility: hidden;}
      .stApp { background-color: #f0f0f0; }
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
    #game-container {
      text-align: center;
    }
    #instructions {
      color: #333;
      font-size: 1.2em;
      margin-top: 10px;
    }
    #line-count {
      color: #333;
      font-size: 1.2em;
      margin-top: 10px;
    }
    canvas {
      display: block;
      margin: auto;
      background: #c0c0c0; /* やや濃いグレー */
      border: 2px solid #888;
    }
  </style>
</head>
<body>
  <div id="game-container">
    <div id="instructions">
      キー操作: ←: 左移動, →: 右移動, ↓: 落下, Q: 反時計回り, W: 時計回り
    </div>
    <canvas id="tetris" width="240" height="400"></canvas>
    <div id="line-count">あと 12 行</div>
  </div>
  <script>
    // アリーナ（フィールド）の生成
    function createMatrix(w, h) {
      const matrix = [];
      while (h--) {
        matrix.push(new Array(w).fill(0));
      }
      return matrix;
    }
    
    // テトリミノの生成。ここでは全てのピースを淡い青 (#ADD8E6) で表示
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
    
    // ブロックの色はすべて淡い青 (#ADD8E6)
    const colors = [
      null,
      "#ADD8E6",
      "#ADD8E6",
      "#ADD8E6",
      "#ADD8E6",
      "#ADD8E6",
      "#ADD8E6",
      "#ADD8E6"
    ];
    
    // 描画処理
    const canvas = document.getElementById("tetris");
    const context = canvas.getContext("2d");
    
    function drawMatrix(matrix, offset) {
      matrix.forEach((row, y) => {
        row.forEach((value, x) => {
          if (value !== 0) {
            context.fillStyle = colors[value];
            context.fillRect(x + offset.x, y + offset.y, 1, 1);
          }
        });
      });
    }
    
    function draw() {
      context.fillStyle = '#c0c0c0';
      context.fillRect(0, 0, canvas.width, canvas.height);
      drawMatrix(arena, {x: 0, y: 0});
      drawMatrix(player.matrix, player.pos);
    }
    
    // 衝突判定
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
    
    // ピースをフィールドに固定
    function merge(arena, player) {
      player.matrix.forEach((row, y) => {
        row.forEach((value, x) => {
          if (value !== 0) {
            arena[y + player.pos.y][x + player.pos.x] = value;
          }
        });
      });
    }
    
    // プレイヤーの状態
    const player = {
      pos: {x: 0, y: 0},
      matrix: null,
      linesCleared: 0
    };
    
    // プレイヤーリセット：新たなピースを生成
    function playerReset() {
      const pieces = 'TJLOSZI';
      player.matrix = createPiece(pieces[pieces.length * Math.random() | 0]);
      player.pos.y = 0;
      player.pos.x = (arena[0].length / 2 | 0) - (player.matrix[0].length / 2 | 0);
      if (collide(arena, player)) {
        arena.forEach(row => row.fill(0));
        player.linesCleared = 0;
        updateLineCount();
        alert("Game Over!");
      }
    }
    
    // ピース回転
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
    
    let dropCounter = 0;
    let dropInterval = 1000;
    let lastTime = 0;
    let updateId;
    
    // ラインクリア処理。クリアした行数をカウントし、残り行数を更新
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
