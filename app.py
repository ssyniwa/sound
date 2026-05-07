import streamlit as st
import numpy as np
import io

st.set_page_config(page_title="Silent Stealth", layout="centered")
st.title("🤫 息を殺せ！ステルスサバイバル")

st.info("下のマイクボタンを押して、静かに録音してください。")

# 敵の画像
enemy_placeholder = st.empty()
enemy_placeholder.image("assets/enemy_back.png", caption="敵は油断している...")

# 難易度設定（しきい値）
threshold = st.sidebar.slider("敵の耳の良さ（しきい値）", 0.0, 1.0, 0.1)

# マイク入力
audio_file = st.audio_input("マイクを長押しして潜入（録音）開始")

if audio_file:
    # 音声バイナリをnumpy配列に変換
    # st.audio_inputは通常WAV形式でデータを渡します
    audio_bytes = audio_file.read()
    
    # 最初の44バイト（WAVヘッダー）を飛ばして数値化
    audio_data = np.frombuffer(audio_bytes, dtype=np.int16, offset=44)
    
    if len(audio_data) > 0:
        # 音量の正規化 (0.0 〜 1.0)
        vol = np.max(np.abs(audio_data)) / 32768.0
        
        st.write(f"今回の最大音量: **{vol:.3f}**")

        if vol > threshold:
            enemy_placeholder.image("assets/enemy_front.png", caption="!!! 見つかった !!!")
            st.error("敵がこちらを振り向いた！ゲームオーバー！")
        else:
            enemy_placeholder.image("assets/enemy_clear.png", caption="ふぅ... バレなかった。")
            st.success("潜入成功！")
            st.balloons()