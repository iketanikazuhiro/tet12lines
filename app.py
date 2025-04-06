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
    /* キー操作説明（ゲーム画面の上部、中央揃え） */
    #instructions {
      text-align: center;
      font-size: 1.5em;
      color: #333;
      margin-top: 10px;
      margin-bottom: 10px;
    }
    /* ゲームコンテナ：相対配置で次ピースプレビューを絶対配置 */
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
    /* 次ピースプレビューキャンバス：ゲーム画面の右上に配置 */
    canvas#next {
      position: absolute;
      top: 0;
      right: -90px;
      background: #f0f0f0;
      border: 2px solid #888;
    }
    /* ラインカウント表示：下部中央 */
    #line-count {
      text-align: center;
      font-size: 1.2em;
      color: #333;
      margin-top: 10px;
    }
  </style>
</head>
<body>
  <div id="instructions">←　→　Ｑ　Ｒ　↓</div>
  <div id="game-container">
    <canvas id="tetris" width="240" height="400"></canvas>
    <canvas id="next" width="80" height="80"></canvas>
  </div>
  <div id="line-count">あと 12 行</div>
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

    // ----- 描画処理 -----
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
      context.fillStyle = "#f0f0f0";  // 背景：薄いグレー
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
          alert("Game Over! 12 lines cleared.");
          cancelAnimationFrame(updateId);
          return;
        }
      }
    }

    // ----- 次ピースプレビュー -----
    const nextCanvas = document.getElementById("next");
    const nextContext = nextCanvas.getContext("2d");
    nextContext.scale(20, 20);
    function updateNext() {
      nextContext.fillStyle = "#f0f0f0";
      nextContext.fillRect(0, 0, nextCanvas.width, nextCanvas.height);
      if (nextPiece) {
        // 中央揃えのためのオフセット（nextCanvasは80x80なので、4マス×4マス分の描画想定）
        const matrix = nextPiece;
        const offset = {
          x: Math.floor((nextCanvas.width / 20 - matrix[0].length) / 2),
          y: Math.floor((nextCanvas.height / 20 - matrix.length) / 2)
        };
        drawMatrix(matrix, offset, nextContext);
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
      document.getElementById("line-count").textContent = "あと " + remaining + " 行";
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

    // ----- 初期化と更新ループ開始 -----
    function init() {
      player.linesCleared = 0;
      updateLineCount();
      playerReset();
      updateId = requestAnimationFrame(update);
    }

    init();
  </script>
</body>
</html>
"""

components.html(html_code, height=500)
