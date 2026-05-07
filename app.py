import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import numpy as np
import time

# --- 設定 ---
GAME_TIME = 60  # 制限時間（秒）

st.set_page_config(page_title="Stealth Voice Game", layout="centered")
st.title("👁️ 敵の視線を逃れろ")

# セッション状態の初期化
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'game_over' not in st.session_state:
    st.session_state.game_over = False

# 音声処理クラス
class StealthAudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.max_amplitude = 0

    def recv_audio(self, frame):
        audio_data = frame.to_ndarray()
        self.max_amplitude = np.max(np.abs(audio_data)) / 32768.0
        return frame

# --- UIレイアウト ---
col1, col2 = st.columns([2, 1])

with col2:
    threshold = st.slider("敵の聴覚感度", 0.0, 1.0, 0.2)
    start_btn = st.button("ゲーム開始！")
    if start_btn:
        st.session_state.start_time = time.time()
        st.session_state.game_over = False

with col1:
    # 敵の画像表示用プレースホルダー
    enemy_placeholder = st.empty()
    timer_placeholder = st.empty()
    
    # 初期の敵（背中を向けている状態）
    enemy_placeholder.image("assets/enemy_back.png", caption="敵は背を向けている...")

# WebRTC接続
ctx = webrtc_streamer(
    key="stealth-game-v2",
    mode=WebRtcMode.SENDONLY,
    media_stream_constraints={"video": False, "audio": True},
    worker_class=StealthAudioProcessor,
)

# --- ゲームループ ---
if ctx.audio_processor and st.session_state.start_time and not st.session_state.game_over:
    while True:
        elapsed_time = time.time() - st.session_state.start_time
        remaining_time = max(0, GAME_TIME - int(elapsed_time))
        
        # 音量取得
        current_vol = ctx.audio_processor.max_amplitude
        
        # タイマー更新
        timer_placeholder.metric("残り時間", f"{remaining_time}秒")
        
        # 判定：見つかった場合
        if current_vol > threshold:
            st.session_state.game_over = True
            enemy_placeholder.image("assets/enemy_front.png", caption="見つかった！")
            st.error("敵がこちらを振り向いた！ゲームオーバー！")
            break
            
        # 判定：クリア
        if remaining_time <= 0:
            st.session_state.game_over = True
            st.balloons()
            st.success("1分間耐え抜いた！ミッション成功！")
            break
            
        time.sleep(0.1)  # 負荷軽減