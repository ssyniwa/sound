import streamlit as st
import numpy as np
import time
import io
from pydub import AudioSegment

st.set_page_config(page_title="Silent Stealth", layout="centered")
st.title("🤫 息を殺せ！ステルスサバイバル")

# 説明
st.info("下の「Record」ボタンを押しながら、静かにしてください。音を立てると敵が振り向きます！")

# 敵の画像エリア
enemy_placeholder = st.empty()
enemy_placeholder.image("assets/enemy_back.png", caption="敵は油断している...")

# 難易度設定
threshold = st.sidebar.slider("敵の耳の良さ（しきい値）", 0, 100, 30)

# マイク入力 (標準機能)
audio_file = st.audio_input("マイクを長押しして潜入開始")

if audio_file:
    # 音声データを読み込んで解析
    audio_bytes = audio_file.read()
    audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
    
    # デシベル（音量）を取得
    # dBFSは最大が0なので、扱いやすいようにプラスの数値に変換
    current_vol = abs(audio_segment.dBFS) if audio_segment.dBFS != float('-inf') else 0
    
    # 判定ロジック (dBFSは数値が小さいほど音が大きい)
    # 簡易的に：100 - abs(dBFS) で「音の大きさ」を0-100で表現
    volume_score = max(0, 100 - current_vol)
    
    st.write(f"あなたの音量スコア: {volume_score:.1f}")
    
    if volume_score > threshold:
        enemy_placeholder.image("assets/enemy_front.png", caption="!!! 見つかった !!!")
        st.error("敵がこちらを振り向いた！ゲームオーバー！")
    else:
        enemy_placeholder.image("assets/enemy_clear.png", caption="敵はいなくなった")
        st.success("ふぅ... バレずに済んだようだ。")
        st.balloons()