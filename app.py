import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import numpy as np
import time

# --- 音声処理クラス ---
class StealthAudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.max_amplitude = 0

    def recv_audio(self, frame):
        # 1. 音声データを1次元の数値配列(int16)として取得
        raw_data = frame.to_ndarray().flatten()
        
        # 2. データが空でないか確認
        if raw_data.dtype == np.int16:
            # 整数（16bit）で届いた場合
            self.max_amplitude = np.max(np.abs(raw_data)) / 32768.0
        else:
            # すでに小数（float）で届いている場合
            self.max_amplitude = np.max(np.abs(raw_data))

        return frame
# 標準機能のマイクレコーダーを試す
audio_value = st.audio_input("マイクのテスト（ここで波形が動くか確認してください）")

if audio_value:
    st.write("マイクは生きています！")
    st.audio(audio_value)
# --- アプリ設定 ---
st.set_page_config(page_title="Silent Stealth", layout="centered")
st.title("🤫 息を殺せ！ステルスサバイバル")

# セッション状態（ゲーム管理）
if 'game_active' not in st.session_state:
    st.session_state.game_active = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0

# --- UI要素 ---
threshold = st.sidebar.slider("敵の感度 (しきい値)", 0.01, 1.00, 0.15)
limit_time = 60 # 60秒耐える設定

# 画像表示用
enemy_image = st.empty()
status_text = st.empty()
progress_bar = st.progress(0)

# 初期画像（背中）
enemy_image.image("assets/enemy_back.png", caption="敵は油断している...")

# WebRTCストリーマー
ctx = webrtc_streamer(
    key="stealth-v4",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=StealthAudioProcessor,
    media_stream_constraints={"video": False, "audio": True},
)

# --- ゲーム実行ロジック ---
# ctx.state.playing が True（マイク起動中）の時だけ動かす
if ctx.state.playing:
    if not st.session_state.game_active:
        st.session_state.start_time = time.time()
        st.session_state.game_active = True

    # ゲームループ（Streamlitの再レンダリングを利用）
    while st.session_state.game_active:
        # ctx.audio_processor が生成されるまで待機が必要な場合があるためチェック
        if ctx.audio_processor:
            current_vol = ctx.audio_processor.max_amplitude
            elapsed = time.time() - st.session_state.start_time
            remaining = max(0, limit_time - int(elapsed))
            st.write(f"Raw Volume: {ctx.audio_processor.max_amplitude}")
            # UI更新
            status_text.subheader(f"残り時間: {remaining}s | 現在の音量: {current_vol:.3f}")
            progress_bar.progress(min(1.0, current_vol / threshold))

            # 判定1: 見つかった
            if current_vol > threshold:
                enemy_image.image("assets/enemy_front.png", caption="!!! 見つかった !!!")
                st.error("敵がこちらを振り向いた！")
                st.session_state.game_active = False
                break

            # 判定2: クリア
            if elapsed >= limit_time:
                enemy_image.image("assets/enemy_clear.png", caption="生き延びた！")
                st.balloons()
                st.success("ミッションコンプリート！")
                st.session_state.game_active = False
                break

            time.sleep(1.0) # ブラウザの負荷軽減
            st.rerun() # 画面を強制更新してリアルタイム性を出す
        else:
            time.sleep(0.5)
            status_text.write("マイク準備中...")
            break
else:
    st.info("上の 'Start' ボタンを押して、マイクの使用を許可してください。")
    st.session_state.game_active = False