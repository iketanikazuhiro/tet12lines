import streamlit as st
import streamlit.components.v1 as components
import random

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
    /* キー操作説明（1行空けて上部に表示） */
    #instructions {
      text-align: center;
      font-size: 1.5em;
      color: #333;
      margin-top: 10px;
      margin-bottom: 10px;
    }
    /* ゲームコンテナ（相対配置で次ピースを絶対配置） */
    #game-container {
      position: relative;
      width: 240px;
      margin: auto;
    }
    canvas#tetris {
      display: block;
      background: #c0c0c0; /* ゲーム画面の枠はやや濃いグレー */
      border: 2px solid #888;
    }
    /* 次ピースプレビュー用キャンバス */
    canvas#next {
      position: absolute;
      top: 0;
      right: -90px; /* ゲーム画面の右肩に表示 */
      background: #c0c0c0;
      border: 2px solid #888;
    }
    /* 残り行数表示 */
    #line-count {
      text-align: center;
      font-size: 1.2em;
      color: #333;
      margin-top: 10px;
    }
  </style>
</head>
<body>
  <div id="instructions">Q　R　←　→　↓</div>
  <div id="game-container">
    <canvas id="tetris" width="240" height="400"></canvas>
    <canvas id="next" width="80" height="80"></canvas>
  </div>
  <div id="line-count">あと 12 行</div>
  <script>
    // ----- Tetris基本設定 -----
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
    // ブロックの色は全て淡い青 (#ADD8E6)
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
    
    // ----- ゲーム画面描画 -----
    const canvas = document.getElementById("tetris");
    const context = canvas.getContext("2d");
    
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
      context.fillStyle = "#f0f0f0";  // 背景：明るいグレー
      context.fillRect(0, 0, canvas.width, canvas.height);
      drawMatrix(arena, {x: 0, y: 0}, context);
      drawMatrix(player.matrix, player.pos, context);
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
    
    // ----- ピース固定、ラインクリア -----
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
          alert("Game Over! 12 lines cleared.");
          cancelAnimationFrame(updateId);
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
    
    function randomPiece() {
      const pieces = 'TJLOSZI';
      return pieces[pieces.length * Math.random() | 0];
    }
    
    function playerReset() {
      // 次ピースを現在のピースに
      player.matrix = nextPiece;
      // 新たな次ピースを生成
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
    
    let dropCounter = 0;
    let dropInterval = 1000;
    let lastTime = 0;
    let updateId;
    
    const arena = createMatrix(12, 20);
    
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
      } else if (event.keyCode === 82) {  // R（時計回り）※Rを利用
        playerRotate(1);
      }
    });
    
    // ----- 次ピースプレビュー描画 -----
    const nextCanvas = document.getElementById("next");
    const nextContext = nextCanvas.getContext("2d");
    function updateNext() {
      nextContext.fillStyle = "#f0f0f0";
      nextContext.fillRect(0, 0, nextCanvas.width, nextCanvas.height);
      if (nextPiece) {
        // nextPieceを描画する。小さいサイズ用にスケール調整。
        // ここでは、ブロックサイズ1として、中央に配置
        let matrix = nextPiece;
        // 一度、nextPieceとして作成したピースはmatrixとして保持されないため、
        // 同じ関数 createPiece() を用いて次ピースを作成し、描画する方法に変更します。
        // そのため、次ピースの描画は player.matrix の代わりに、
        // nextPiece = createPiece(ランダム文字) で既に生成済みのものを描画する。
        // ここでは簡単のため、次ピースの色は1固定とします。
        // 描画位置はキャンバス中央にする。
        // サイズによって位置調整が必要ですが、簡易的な実装です。
        // ここでは、ブロックサイズ 1 として、nextCanvas は8x8マス相当に設定しています。
        // なお、nextPiece は2次元配列として作成されています。
        for (let y = 0; y < nextPiece.length; ++y) {
          for (let x = 0; x < nextPiece[y].length; ++x) {
            if (nextPiece[y][x] !== 0) {
              nextContext.fillStyle = colors[nextPiece[y][x]];
              nextContext.fillRect(x + 1, y + 1, 1, 1);
            }
          }
        }
      }
    }
    
    // ----- 更新ループ -----
    function update(time = 0) {
      if (!time) time = performance.now();
      const deltaTime = time - lastTime;
      lastTime = time;
      dropCounter += deltaTime;
      if (dropCounter > dropInterval) {
        playerDrop();
      }
      draw();
      updateId = requestAnimationFrame(update);
    }
    
    function draw() {
      context.fillStyle = "#f0f0f0";
      context.fillRect(0, 0, canvas.width, canvas.height);
      drawMatrix(arena, {x: 0, y: 0}, context);
      drawMatrix(player.matrix, player.pos, context);
    }
    
    function updateLineCount() {
      const remaining = 12 - player.linesCleared;
      document.getElementById("line-count").textContent = "あと " + remaining + " 行";
    }
    
    // ----- ゲーム開始 -----
    function init() {
      player.linesCleared = 0;
      updateLineCount();
      playerReset();
      update();
    }
    
    // 初期化
    init();
  </script>
</body>
</html>
"""

components.html(html_code, height=500)
