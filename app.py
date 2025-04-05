import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Mini Tetris - 12 Lines", layout="centered")
st.markdown(
    """
    <style>
      header {visibility: hidden;}
      .stApp { background-color: #111; }
      body { margin: 0; background: #111; }
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
      background: #111;
      margin: 0;
      overflow: hidden;
    }
    canvas {
      display: block;
      margin: auto;
      background: #000;
    }
  </style>
</head>
<body>
  <canvas id="tetris" width="240" height="400"></canvas>
  <script>
    // キャンバスとコンテキストの取得
    const canvas = document.getElementById('tetris');
    const context = canvas.getContext('2d');
    context.scale(20, 20);

    // アリーナ（フィールド）を作成
    function createMatrix(w, h) {
      const matrix = [];
      while (h--) {
        matrix.push(new Array(w).fill(0));
      }
      return matrix;
    }

    // ピースの定義
    function createPiece(type) {
      if (type === 'T') {
        return [
          [0,1,0],
          [1,1,1],
          [0,0,0]
        ];
      } else if (type === 'O') {
        return [
          [2,2],
          [2,2]
        ];
      } else if (type === 'L') {
        return [
          [0,3,0],
          [0,3,0],
          [0,3,3]
        ];
      } else if (type === 'J') {
        return [
          [0,4,0],
          [0,4,0],
          [4,4,0]
        ];
      } else if (type === 'I') {
        return [
          [0,5,0,0],
          [0,5,0,0],
          [0,5,0,0],
          [0,5,0,0]
        ];
      } else if (type === 'S') {
        return [
          [0,6,6],
          [6,6,0],
          [0,0,0]
        ];
      } else if (type === 'Z') {
        return [
          [7,7,0],
          [0,7,7],
          [0,0,0]
        ];
      }
    }

    // カラー設定（各数値に対して）
    const colors = [
      null,
      '#FF0D72',
      '#0D47A1',
      '#FF8E0D',
      '#FFD700',
      '#0D47A1',
      '#0D47A1',
      '#FF0D72'
    ];

    // 描画処理
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
      context.fillStyle = '#000';
      context.fillRect(0, 0, canvas.width, canvas.height);
      drawMatrix(arena, {x:0, y:0});
      drawMatrix(player.matrix, player.pos);
    }

    // 衝突判定
    function collide(arena, player) {
      const m = player.matrix;
      const o = player.pos;
      for (let y = 0; y < m.length; ++y) {
        for (let x = 0; x < m[y].length; ++x) {
          if (m[y][x] !== 0 &&
              (arena[y + o.y] &&
               arena[y + o.y][x + o.x]) !== 0) {
            return true;
          }
        }
      }
      return false;
    }

    // ピース固定とラインクリア処理
    function merge(arena, player) {
      player.matrix.forEach((row, y) => {
        row.forEach((value, x) => {
          if (value !== 0) {
            arena[y + player.pos.y][x + player.pos.x] = value;
          }
        });
      });
    }

    // ラインクリア処理：クリアした行数をカウントし、合計12行でゲーム終了
    function arenaSweep() {
      outer: for (let y = arena.length -1; y >= 0; y--) {
        for (let x = 0; x < arena[y].length; ++x) {
          if (arena[y][x] === 0) {
            continue outer;
          }
        }
        // 行全体が埋まっているなら削除
        arena.splice(y, 1)[0].fill(0);
        arena.unshift(new Array(arena[0].length).fill(0));
        player.linesCleared++;
        if (player.linesCleared >= 12) {
          alert("Game Over! 12 lines cleared.");
          cancelAnimationFrame(updateId);
          return;
        }
        y++;
      }
    }

    // ピースの落下処理
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
    const player = {
      pos: {x: 0, y: 0},
      matrix: null,
      linesCleared: 0,
    };

    function playerReset() {
      const pieces = 'TJLOSZI';
      player.matrix = createPiece(pieces[pieces.length * Math.random() | 0]);
      player.pos.y = 0;
      player.pos.x = (arena[0].length / 2 | 0) -
                     (player.matrix[0].length / 2 | 0);
      if (collide(arena, player)) {
        arena.forEach(row => row.fill(0));
        player.linesCleared = 0;
        alert("Game Over!");
        cancelAnimationFrame(updateId);
      }
    }

    document.addEventListener('keydown', event => {
      if (event.keyCode === 37) {
        playerMove(-1);
      } else if (event.keyCode === 39) {
        playerMove(1);
      } else if (event.keyCode === 40) {
        playerDrop();
      } else if (event.keyCode === 81) {
        playerRotate(-1);
      } else if (event.keyCode === 87) {
        playerRotate(1);
      }
    });

    function update(time = 0) {
      const deltaTime = time - lastTime;
      lastTime = time;
      dropCounter += deltaTime;
      if (dropCounter > dropInterval) {
        playerDrop();
      }
      draw();
      updateId = requestAnimationFrame(update);
    }

    playerReset();
    update();
  </script>
</body>
</html>
"""

components.html(html_code, height=500)
