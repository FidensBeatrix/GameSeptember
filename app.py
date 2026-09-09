import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Kinetic Sand PAC-MAN",
    page_icon="🐶",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------
# LOGIN
# ------------------------------------------------------------

def check_credentials(username: str, password: str) -> bool:
    """
    Credentials are stored in Streamlit Secrets, NOT in GitHub.

    Expected .streamlit/secrets.toml format:

    [auth.users]
    Venitas = "change-me"
    Gondor = "change-me-too"
    """
    try:
        users = st.secrets["auth"]["users"]
        return username in users and password == users[username]
    except Exception:
        return False


def show_login():
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {display: none;}
            .block-container {
                padding-top: 2.2rem;
                max-width: 920px;
            }
            .login-title {
                font-size: 2rem;
                font-weight: 800;
                margin-bottom: .15rem;
            }
            .login-sub {
                opacity: .72;
                margin-bottom: 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.35, 1], vertical_alignment="center")

    with left:
        st.markdown('<div class="login-title">🐾 Kinetic Sand PAC-MAN</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="login-sub">Sign in before the T-Rex starts looking for snacks.</div>',
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Username")
            password = st.text_input("Password", type="password", placeholder="Password")
            submitted = st.form_submit_button("LOGIN", use_container_width=True)

        if submitted:
            if check_credentials(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("🦖 RAWR... wrong username or password. No castle hunting for impostors.")

    with right:
        try:
            st.image("RATeamLogo.png", use_container_width=True)
        except Exception:
            st.info("Add **RATeamLogo.png** to the same GitHub folder as `app.py`.")

    st.stop()


if not st.session_state.get("authenticated", False):
    show_login()


# ------------------------------------------------------------
# AUTHENTICATED APP HEADER
# ------------------------------------------------------------

head_left, head_right = st.columns([5, 1], vertical_alignment="center")
with head_left:
    st.caption(f"Logged in as **{st.session_state.get('username', '')}**")
with head_right:
    if st.button("Log out", use_container_width=True):
        st.session_state.clear()
        st.rerun()


# ------------------------------------------------------------
# GAME
# ------------------------------------------------------------

GAME_HTML = r"""
<div id="ks-root" tabindex="0">
  <style>
    #ks-root {
      width: 100%;
      outline: none;
      color: #f8fafc;
      font-family: Arial, Helvetica, sans-serif;
    }

    #ks-wrap {
      max-width: 1320px;
      margin: 0 auto;
    }

    #ks-header {
      text-align: center;
      margin: 2px 0 10px 0;
    }

    #ks-title {
      font-size: 30px;
      font-weight: 900;
      color: #ffd166;
      letter-spacing: .5px;
    }

    #ks-status {
      font-size: 16px;
      font-weight: 700;
      margin-top: 5px;
    }

    #ks-letters {
      font-size: 22px;
      font-weight: 900;
      color: #7dd3fc;
      margin-top: 6px;
      letter-spacing: 8px;
    }

    #game-shell {
      position: relative;
      width: 100%;
      overflow: auto;
      border-radius: 8px;
    }

    #game {
      display: block;
      margin: 0 auto;
      background: #050816;
      border: 3px solid #6d28d9;
      max-width: 100%;
      height: auto;
    }

    #controls {
      margin: 12px auto 0;
      max-width: 860px;
      display: flex;
      justify-content: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    #controls button {
      min-width: 160px;
      border: 0;
      border-radius: 8px;
      padding: 10px 14px;
      font-size: 15px;
      font-weight: 800;
      color: white;
      background: #7c3aed;
      cursor: pointer;
    }

    #controls button:hover {
      background: #5b21b6;
    }

    #help {
      text-align: center;
      opacity: .78;
      margin-top: 8px;
      font-size: 13px;
    }

    #guess-panel {
      display: none;
      max-width: 620px;
      margin: 14px auto 0;
      border: 2px solid #ffd166;
      background: #111827;
      border-radius: 10px;
      padding: 16px;
      text-align: center;
    }

    #guess-panel h3 {
      margin: 0 0 8px;
      color: #ffd166;
    }

    #guess-panel input {
      width: min(360px, 88%);
      padding: 10px 12px;
      border-radius: 7px;
      border: 1px solid #475569;
      background: #020617;
      color: white;
      font-size: 17px;
      text-align: center;
    }

    #guess-panel button {
      margin-left: 8px;
      padding: 10px 15px;
      border: 0;
      border-radius: 7px;
      color: white;
      background: #2563eb;
      font-weight: 800;
      cursor: pointer;
    }

    #guess-feedback {
      min-height: 24px;
      margin-top: 10px;
      font-weight: 800;
    }

    @media (max-width: 700px) {
      #ks-title { font-size: 22px; }
      #ks-status { font-size: 13px; }
      #ks-letters { font-size: 17px; letter-spacing: 4px; }
      #guess-panel button { margin: 8px 0 0; width: 88%; }
    }
  </style>

  <div id="ks-wrap">
    <div id="ks-header">
      <div id="ks-title">🏖️ KINETIC SAND PAC-MAN 🏰</div>
      <div id="ks-status"></div>
      <div id="ks-letters"></div>
    </div>

    <div id="game-shell">
      <canvas id="game"></canvas>
    </div>

    <div id="controls">
      <button id="restart">Restart Game</button>
      <button id="pause">Pause / Resume (SPACE)</button>
    </div>

    <div id="help">Move with Arrow Keys or WASD • SPACE pauses • Purple portal = IN • Blue portal = OUT</div>

    <div id="guess-panel">
      <h3>🦖😢 NOOO! YOU GOT ALL THE CASTLES!</h3>
      <div id="guess-text">My snack escaped... Fine. Guess the word!</div>
      <div style="margin:10px 0;font-weight:800" id="found-letters"></div>
      <input id="guess-input" maxlength="12" placeholder="Type the hidden word..." />
      <button id="guess-button">GUESS</button>
      <div id="guess-feedback"></div>
    </div>
  </div>

  <script>
  (() => {
    const ROOT = document.getElementById("ks-root");
    if (ROOT.dataset.ready === "1") return;
    ROOT.dataset.ready = "1";

    const WORD = "TESTING";
    const CELL = 30;
    const SPEED = 135;

    const MAZE_STR = [
      "11111111111111111111111111111111111111111",
      "10000000000000000000100000000000000000001",
      "10111101111101111110101111101111101111101",
      "10000101000001000000100000101000001000001",
      "11110101011111011111111110101011111011111",
      "10000100010000000000100000100010000000001",
      "10111111010111111110101111111010111111001",
      "10000000010000000000100000000010000000001",
      "10111101111101111110111110111111101111101",
      "10000100000001000000000000100000001000001",
      "11110111111001011111111110101111111011111",
      "10000100001000010000000000100010000000001",
      "10111101001111110111111110111010111111001",
      "10000001000000000100000000100010000000001",
      "10111111111101111110111111101111111111101",
      "10000000000100000000100000001000000000001",
      "11111101110111111110101111111011101111111",
      "10000001000100000000100000000000100000001",
      "10111111011101111111111110111110111111001",
      "10000000010000000000100000100000100000001",
      "10111101111111101110101111101111101111101",
      "10000100000000001000100000000000001000001",
      "11110111111111111011111111111111111011111",
      "10000000000000000000000000000000000000001",
      "11111111111111111111111111111111111111111"
    ];

    const MAZE = MAZE_STR.map(r => [...r].map(Number));
    const ROWS = MAZE.length;
    const COLS = MAZE[0].length;

    const PLAYER_START = [23, 2];
    const DINO_START = [1, 39];

    const PORTALS = {
      A: [[1, 3], [23, 37]],
      B: [[5, 38], [19, 2]],
      C: [[17, 38], [3, 2]],
      D: [[23, 20], [1, 20]]
    };

    const CASTLE_POSITIONS = [
      [1, 8], [3, 25], [7, 6], [11, 20],
      [15, 34], [19, 16], [23, 31]
    ];

    const canvas = document.getElementById("game");
    const ctx = canvas.getContext("2d");
    canvas.width = COLS * CELL;
    canvas.height = ROWS * CELL;

    const statusEl = document.getElementById("ks-status");
    const lettersEl = document.getElementById("ks-letters");
    const guessPanel = document.getElementById("guess-panel");
    const guessInput = document.getElementById("guess-input");
    const guessButton = document.getElementById("guess-button");
    const guessFeedback = document.getElementById("guess-feedback");
    const foundLetters = document.getElementById("found-letters");

    let timer = null;
    let guessTimer = null;
    let state = {};
    let fireworks = [];
    let fireworkFrame = 0;
    let fireworkTimer = null;

    function keyOf(pos) {
      return `${pos[0]},${pos[1]}`;
    }

    function shuffle(arr) {
      const a = [...arr];
      for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
      }
      return a;
    }

    function resetGame() {
      if (timer) clearInterval(timer);
      if (guessTimer) clearTimeout(guessTimer);
      stopFireworks();

      const shuffled = shuffle([...WORD]);
      const letterMap = {};
      CASTLE_POSITIONS.forEach((p, i) => letterMap[keyOf(p)] = shuffled[i]);

      state = {
        gameOver: false,
        awaitingGuess: false,
        won: false,
        score: 0,

        paused: false,
        countdownActive: false,
        countdownValue: null,

        player: [...PLAYER_START],
        playerDir: [0, 0],
        nextDir: [0, 0],

        dino: [...DINO_START],
        dinoTick: 0,

        castles: new Set(CASTLE_POSITIONS.map(keyOf)),
        castleLetters: letterMap,
        collected: [],

        portalCooldown: 0,
        lastEvent: "Collect all Kinetic Sand castles!"
      };

      guessPanel.style.display = "none";
      guessFeedback.textContent = "";
      guessInput.value = "";

      render();
      timer = setInterval(gameLoop, SPEED);
      ROOT.focus();
    }

    function isWall(r, c) {
      return r < 0 || r >= ROWS || c < 0 || c >= COLS || MAZE[r][c] === 1;
    }

    function samePos(a, b) {
      return a[0] === b[0] && a[1] === b[1];
    }

    function movePlayer() {
      let nr = state.player[0] + state.nextDir[0];
      let nc = state.player[1] + state.nextDir[1];

      if (!isWall(nr, nc)) state.playerDir = [...state.nextDir];

      nr = state.player[0] + state.playerDir[0];
      nc = state.player[1] + state.playerDir[1];

      if (!isWall(nr, nc)) state.player = [nr, nc];

      checkPortal();
      checkCastle();
      checkCollision();
    }

    function checkPortal() {
      if (state.portalCooldown > 0) return;

      for (const [label, pair] of Object.entries(PORTALS)) {
        const entry = pair[0];
        const exit = pair[1];
        if (samePos(state.player, entry)) {
          state.player = [...exit];
          state.portalCooldown = 4;
          state.lastEvent = `🌀 Portal ${label}: purple IN → blue OUT`;
          return;
        }
      }
    }

    function checkCastle() {
      const k = keyOf(state.player);
      if (!state.castles.has(k)) return;

      const letter = state.castleLetters[k];
      state.castles.delete(k);
      state.collected.push(letter);
      state.score += 250;
      state.lastEvent = `🏰 Castle opened — letter: ${letter}`;

      if (state.castles.size === 0) {
        state.playerDir = [0, 0];
        state.nextDir = [0, 0];
        state.awaitingGuess = true;
        state.lastEvent = "🦖😢 NOOO! You got all the castles...";

        // 5 seconds so the player can actually read the sad dino message.
        guessTimer = setTimeout(() => {
          if (!state.gameOver && state.awaitingGuess) showGuessPanel();
        }, 5000);
      }
    }

    function getNeighbors(pos, includePortals = true) {
      const [r, c] = pos;
      const out = [];

      for (const [dr, dc] of [[-1,0],[1,0],[0,-1],[0,1]]) {
        const nr = r + dr, nc = c + dc;
        if (!isWall(nr, nc)) out.push([nr, nc]);
      }

      if (includePortals) {
        for (const pair of Object.values(PORTALS)) {
          if (samePos(pos, pair[0])) out.push([...pair[1]]);
        }
      }

      return out;
    }

    function bfsNextStep(start, target) {
      if (samePos(start, target)) return [...start];

      const q = [[...start]];
      const prev = new Map();
      prev.set(keyOf(start), null);

      let found = false;

      while (q.length) {
        const cur = q.shift();
        if (samePos(cur, target)) {
          found = true;
          break;
        }

        for (const nxt of getNeighbors(cur, true)) {
          const k = keyOf(nxt);
          if (!prev.has(k)) {
            prev.set(k, cur);
            q.push(nxt);
          }
        }
      }

      if (!found && !prev.has(keyOf(target))) return [...start];

      let step = [...target];
      let parent = prev.get(keyOf(step));

      if (parent === undefined) return [...start];

      while (parent && !samePos(parent, start)) {
        step = [...parent];
        parent = prev.get(keyOf(step));
      }

      return step;
    }

    function predictPlayerTarget() {
      let target = [...state.player];
      const [dr, dc] = state.playerDir;

      for (let i = 0; i < 3; i++) {
        const nr = target[0] + dr;
        const nc = target[1] + dc;
        if (isWall(nr, nc)) break;
        target = [nr, nc];
      }
      return target;
    }

    function moveDino() {
      state.dinoTick += 1;
      if (state.dinoTick % 4 === 0) return;

      const start = [...state.dino];
      const player = [...state.player];
      const predicted = predictPlayerTarget();

      const manhattan = Math.abs(start[0] - player[0]) + Math.abs(start[1] - player[1]);
      const target = manhattan <= 7 ? player : predicted;

      let next = bfsNextStep(start, target);
      if (samePos(next, start) && !samePos(start, player)) {
        next = bfsNextStep(start, player);
      }

      state.dino = [...next];

      for (const pair of Object.values(PORTALS)) {
        if (samePos(state.dino, pair[0])) {
          state.dino = [...pair[1]];
          break;
        }
      }

      checkCollision();
    }

    function checkCollision() {
      if (state.awaitingGuess || state.gameOver) return;

      if (samePos(state.player, state.dino)) {
        state.gameOver = true;
        state.won = false;
        state.playerDir = [0, 0];
        state.nextDir = [0, 0];
        state.lastEvent = "🦖 NOM NOM... you were delicious!";
      }
    }

    function pauseGame() {
      if (state.gameOver || state.awaitingGuess || state.countdownActive) return;

      if (!state.paused) {
        state.paused = true;
        state.playerDir = [0, 0];
        state.nextDir = [0, 0];
        state.lastEvent = "🐾 Pawsing the Claws...";
        render();
      } else {
        startCountdown();
      }
    }

    function startCountdown() {
      if (!state.paused || state.countdownActive) return;

      state.countdownActive = true;
      state.countdownValue = 3;
      state.lastEvent = "Get ready...";
      render();

      const countdown = setInterval(() => {
        state.countdownValue -= 1;

        if (state.countdownValue <= 0) {
          clearInterval(countdown);
          state.countdownActive = false;
          state.countdownValue = null;
          state.paused = false;
          state.lastEvent = "GO! 🐶💨";
          render();
          ROOT.focus();
          return;
        }

        render();
      }, 1000);
    }

    function counts(s) {
      const m = {};
      for (const ch of s) m[ch] = (m[ch] || 0) + 1;
      return m;
    }

    function sameCounts(a, b) {
      const ca = counts(a);
      const cb = counts(b);
      const keys = new Set([...Object.keys(ca), ...Object.keys(cb)]);
      for (const k of keys) {
        if ((ca[k] || 0) !== (cb[k] || 0)) return false;
      }
      return true;
    }

    function showGuessPanel() {
      foundLetters.textContent = "Letters you found: " + state.collected.join("   ");
      guessPanel.style.display = "block";
      guessFeedback.textContent = "";
      guessInput.value = "";
      guessInput.focus();
    }

    function submitGuess() {
      const guess = guessInput.value.trim().toUpperCase();

      if (guess === WORD) {
        state.awaitingGuess = false;
        state.gameOver = true;
        state.won = true;
        state.score += 1000;
        state.lastEvent = "🎉 CORRECT! TESTING!";
        guessPanel.style.display = "none";
        render();
        startFireworks();
        return;
      }

      const collected = state.collected.join("");

      if (!sameCounts(guess, collected)) {
        guessFeedback.textContent =
          "🦖 RAWR! Sneaky letters? NOM NOM! Use only the 7 letters you actually found: " +
          state.collected.join(" ");
        guessFeedback.style.color = "#fbbf24";
      } else {
        guessFeedback.textContent =
          "🦖 Whomp, whomp... NOM NOM! Right letters, wrong word. Better luck next time! 😋";
        guessFeedback.style.color = "#ff6b6b";
      }

      guessInput.value = "";
      guessInput.focus();
    }

    function gameLoop() {
      if (!state.gameOver && !state.awaitingGuess && !state.paused && !state.countdownActive) {
        if (state.portalCooldown > 0) state.portalCooldown -= 1;

        movePlayer();
        if (!state.gameOver && !state.awaitingGuess) moveDino();
      }

      render();
    }

    function updateLabels() {
      const found = WORD.length - state.castles.size;
      statusEl.textContent =
        `Castles ${found}/${WORD.length}   •   Score ${state.score}   •   ${state.lastEvent}`;

      const slots = [...state.collected];
      while (slots.length < WORD.length) slots.push("_");
      lettersEl.textContent = "Letters:   " + slots.join("   ");
    }

    function drawRect(x, y, w, h, fill, stroke = null, sw = 1) {
      ctx.fillStyle = fill;
      ctx.fillRect(x, y, w, h);
      if (stroke) {
        ctx.strokeStyle = stroke;
        ctx.lineWidth = sw;
        ctx.strokeRect(x, y, w, h);
      }
    }

    function drawPortal(pos, label, entry) {
      const [r, c] = pos;
      const cx = c * CELL + CELL / 2;
      const cy = r * CELL + CELL / 2;

      ctx.beginPath();
      ctx.arc(cx, cy, 14, 0, Math.PI * 2);
      ctx.fillStyle = entry ? "#7c3aed" : "#0284c7";
      ctx.fill();
      ctx.strokeStyle = entry ? "#e9d5ff" : "#bae6fd";
      ctx.lineWidth = 3;
      ctx.stroke();

      ctx.beginPath();
      ctx.arc(cx, cy, 9, 0, Math.PI * 2);
      ctx.strokeStyle = "white";
      ctx.lineWidth = 1;
      ctx.stroke();

      ctx.textAlign = "center";
      ctx.fillStyle = "white";
      ctx.font = "bold 12px Arial";
      ctx.fillText(label, cx, cy + 2);

      ctx.font = "bold 6px Arial";
      ctx.fillText(entry ? "IN" : "OUT", cx, cy + 11);
    }

    function drawCastle(pos) {
      const [r, c] = pos;
      const cx = c * CELL + CELL / 2;
      const cy = r * CELL + CELL / 2;

      ctx.beginPath();
      ctx.arc(cx, cy, 14, 0, Math.PI * 2);
      ctx.fillStyle = "#fde68a";
      ctx.fill();
      ctx.strokeStyle = "#f59e0b";
      ctx.lineWidth = 2;
      ctx.stroke();

      drawRect(cx - 10, cy - 3, 20, 12, "#d6a24b", "#7c4a16");
      drawRect(cx - 11, cy - 10, 7, 8, "#d6a24b", "#7c4a16");
      drawRect(cx + 4, cy - 10, 7, 8, "#d6a24b", "#7c4a16");
      drawRect(cx - 3, cy + 3, 6, 6, "#7c4a16");
    }

    function drawPlayer() {
      const [r, c] = state.player;
      const cx = c * CELL + CELL / 2;
      const cy = r * CELL + CELL / 2;

      // red dog hero
      ctx.beginPath();
      ctx.ellipse(cx - 11, cy - 2, 6, 10, -.25, 0, Math.PI * 2);
      ctx.fillStyle = "#b91c1c";
      ctx.fill();

      ctx.beginPath();
      ctx.ellipse(cx + 11, cy - 2, 6, 10, .25, 0, Math.PI * 2);
      ctx.fill();

      ctx.beginPath();
      ctx.arc(cx, cy, 13, 0, Math.PI * 2);
      ctx.fillStyle = "#ef4444";
      ctx.fill();
      ctx.strokeStyle = "#fca5a5";
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.beginPath();
      ctx.ellipse(cx, cy + 5, 8, 6, 0, 0, Math.PI * 2);
      ctx.fillStyle = "#fecaca";
      ctx.fill();

      ctx.beginPath();
      ctx.arc(cx - 5, cy - 4, 2, 0, Math.PI * 2);
      ctx.arc(cx + 5, cy - 4, 2, 0, Math.PI * 2);
      ctx.fillStyle = "#111827";
      ctx.fill();

      ctx.beginPath();
      ctx.ellipse(cx, cy + 2, 3, 2.5, 0, 0, Math.PI * 2);
      ctx.fill();
    }

    function drawDino() {
      const [r, c] = state.dino;
      const cx = c * CELL + CELL / 2;
      const cy = r * CELL + CELL / 2;

      ctx.fillStyle = "#22c55e";
      ctx.strokeStyle = "#86efac";
      ctx.lineWidth = 2;

      ctx.beginPath();
      ctx.arc(cx, cy - 1, 14, Math.PI, 0);
      ctx.lineTo(cx + 14, cy + 10);
      ctx.lineTo(cx - 14, cy + 10);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();

      ctx.textAlign = "center";
      ctx.font = "15px Arial";
      ctx.fillText("🦖", cx, cy + 5);
    }

    function overlayBox(w, h, border) {
      const cx = canvas.width / 2;
      const cy = canvas.height / 2;
      drawRect(cx - w/2, cy - h/2, w, h, "#111827", border, 4);
      return [cx, cy];
    }

    function drawPauseOverlay() {
      if (state.countdownActive && state.countdownValue != null) {
        const [cx, cy] = overlayBox(230, 170, "#f87171");
        ctx.textAlign = "center";
        ctx.fillStyle = "white";
        ctx.font = "bold 17px Arial";
        ctx.fillText("READY?", cx, cy - 38);
        ctx.fillStyle = "#fde047";
        ctx.font = "bold 56px Arial";
        ctx.fillText(String(state.countdownValue), cx, cy + 28);
        return;
      }

      const [cx, cy] = overlayBox(600, 164, "#f87171");
      ctx.textAlign = "center";
      ctx.fillStyle = "#fca5a5";
      ctx.font = "bold 20px Arial";
      ctx.fillText("🐾 PAWSING THE CLAWS 🐾", cx, cy - 42);

      ctx.fillStyle = "white";
      ctx.font = "bold 13px Arial";
      ctx.fillText("Hunting for letters, dodging T-Rexes...", cx, cy - 5);
      ctx.fillText("even legendary castle explorers need a breather.", cx, cy + 14);

      ctx.fillStyle = "#93c5fd";
      ctx.fillText("Press SPACE when you're ready to run again!", cx, cy + 52);
    }

    function drawGuessOverlay() {
      const [cx, cy] = overlayBox(520, 100, "#ffd166");
      ctx.textAlign = "center";
      ctx.fillStyle = "#ffd166";
      ctx.font = "bold 19px Arial";
      ctx.fillText("🦖😢 NOOO! YOU GOT ALL THE CASTLES!", cx, cy - 20);
      ctx.fillStyle = "#86efac";
      ctx.font = "bold 14px Arial";
      ctx.fillText("My snack escaped... Fine. Guess the word!", cx, cy + 10);
      ctx.fillStyle = "white";
      ctx.font = "bold 12px Arial";
      ctx.fillText("Use all 7 letters to finish the game.", cx, cy + 33);
    }

    function drawEndOverlay() {
      const [cx, cy] = overlayBox(600, 160, state.won ? "#22c55e" : "#ef4444");
      ctx.textAlign = "center";

      if (state.won) {
        ctx.fillStyle = "#fde047";
        ctx.font = "bold 25px Arial";
        ctx.fillText("🎉 CONGRATULATIONS! 🎉", cx, cy - 20);
        ctx.fillStyle = "#7dd3fc";
        ctx.font = "bold 26px Arial";
        ctx.fillText("TESTING", cx, cy + 24);
      } else {
        ctx.fillStyle = "#86efac";
        ctx.font = "bold 25px Arial";
        ctx.fillText("🦖 NOM NOM NOM!", cx, cy - 20);
        ctx.fillStyle = "white";
        ctx.font = "bold 17px Arial";
        ctx.fillText("You were delicious! 😋", cx, cy + 14);
      }
    }

    function render() {
      updateLabels();

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      drawRect(0, 0, canvas.width, canvas.height, "#050816");

      for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
          const x = c * CELL, y = r * CELL;

          if (MAZE[r][c] === 1) {
            drawRect(x + 1, y + 1, CELL - 2, CELL - 2, "#111827", "#2563eb", 2);
          } else if ((r + c) % 3 === 0) {
            ctx.beginPath();
            ctx.arc(x + CELL/2, y + CELL/2, 1, 0, Math.PI * 2);
            ctx.fillStyle = "#a78bfa";
            ctx.fill();
          }
        }
      }

      for (const [label, pair] of Object.entries(PORTALS)) {
        drawPortal(pair[0], label, true);
        drawPortal(pair[1], label, false);
      }

      for (const k of state.castles) {
        drawCastle(k.split(",").map(Number));
      }

      drawDino();
      drawPlayer();

      if (state.awaitingGuess) drawGuessOverlay();
      else if (state.gameOver) drawEndOverlay();
      else if (state.paused) drawPauseOverlay();

      drawFireworks();
    }

    function startFireworks() {
      stopFireworks();
      fireworks = [];
      fireworkFrame = 0;
      for (let i = 0; i < 7; i++) spawnFirework();

      fireworkTimer = setInterval(() => {
        fireworkFrame++;

        if (fireworkFrame > 55) {
          stopFireworks();
          render();
          return;
        }

        for (const fw of fireworks) {
          for (const p of fw.particles) {
            const rad = p.angle * Math.PI / 180;
            p.x += Math.cos(rad) * p.speed;
            p.y += Math.sin(rad) * p.speed + p.gravity * 0.13;
            p.gravity += 0.12;
            p.speed *= 0.985;
          }
        }

        if ([10,20,30].includes(fireworkFrame)) {
          for (let i = 0; i < 3; i++) spawnFirework();
        }

        render();
      }, 45);
    }

    function spawnFirework() {
      const palette = ["#fde047","#fb7185","#22d3ee","#a78bfa","#34d399","#f97316"];
      const color = palette[Math.floor(Math.random() * palette.length)];
      const cx = 80 + Math.random() * (canvas.width - 160);
      const cy = 70 + Math.random() * (canvas.height / 2);

      const particles = [];
      for (let i = 0; i < 18; i++) {
        particles.push({
          x: cx,
          y: cy,
          angle: i * 20,
          speed: 2.4 + Math.random() * 2.8,
          gravity: 0
        });
      }

      fireworks.push({color, particles});
    }

    function drawFireworks() {
      for (const fw of fireworks) {
        for (const p of fw.particles) {
          const size = Math.max(1.5, Math.min(4, p.speed));
          ctx.beginPath();
          ctx.arc(p.x, p.y, size, 0, Math.PI * 2);
          ctx.fillStyle = fw.color;
          ctx.fill();
        }
      }
    }

    function stopFireworks() {
      if (fireworkTimer) clearInterval(fireworkTimer);
      fireworkTimer = null;
      fireworks = [];
    }

    function keyHandler(e) {
      const tag = (e.target && e.target.tagName || "").toLowerCase();
      const editing = tag === "input" || tag === "textarea";

      if (editing) {
        if (e.key === "Enter" && e.target === guessInput) {
          e.preventDefault();
          submitGuess();
        }
        return;
      }

      const key = e.key.toLowerCase();

      if (key === " ") {
        e.preventDefault();
        pauseGame();
        return;
      }

      if (state.gameOver || state.awaitingGuess || state.paused || state.countdownActive) return;

      const dirs = {
        arrowup: [-1,0], w: [-1,0],
        arrowdown: [1,0], s: [1,0],
        arrowleft: [0,-1], a: [0,-1],
        arrowright: [0,1], d: [0,1]
      };

      if (dirs[key]) {
        e.preventDefault();
        state.nextDir = dirs[key];
      }
    }

    ROOT.addEventListener("keydown", keyHandler);
    document.getElementById("restart").addEventListener("click", resetGame);
    document.getElementById("pause").addEventListener("click", pauseGame);
    guessButton.addEventListener("click", submitGuess);

    // Clicking the game gives keyboard focus back to it.
    canvas.addEventListener("click", () => ROOT.focus());
    ROOT.addEventListener("click", (e) => {
      if (e.target !== guessInput) ROOT.focus();
    });

    resetGame();
  })();
  </script>
</div>
"""

components.html(GAME_HTML, height=1020, scrolling=True)
