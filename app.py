import streamlit as st
import numpy as np
import time

# --- ページ設定とタイトル ---
st.set_page_config(page_title="心霊スポット配信", layout="centered")
st.title("📹 絶叫厳禁！心霊スポット生配信")

# --- セッション状態の初期化 ---
if 'game_step' not in st.session_state:
    st.session_state.game_step = "setup" # setup -> streaming -> result
if 'current_vol' not in st.session_state:
    st.session_state.current_vol = 0
if 'recording_duration' not in st.session_state:
    st.session_state.recording_duration = 0

# --- 難易度（スポット）設定 ---
# 画像はプレースホルダーです。ご自身の素材URLに差し替え可能です。
spot_settings = {
    "初級：旧・Ｋトンネル": {
        "threshold": 0.8, 
        "required_time": 5, 
        "enemy_img": "assets/p1back.png",
        "description": "比較的安全なスポット。小声でレポートを続けろ。",
        "outimg": "assets/p1front.png"
    },
    "中級：○○病院跡": {
        "threshold": 0.5, 
        "required_time": 10, 
        "enemy_img": "assets/p2back.png",
        "description": "何かの気配を感じる... 音を立てれば、即座に見つかるぞ。",
        "outimg": "assets/p2front.png"
    },
    "上級：呪われたＳ家": {
        "threshold": 0.3, 
        "required_time": 15, 
        "enemy_img": "assets/p3back.png",
        "description": "最恐のスポット。息を殺せ。物音一つ立てるな。",
        "outimg": "assets/p3front.png"
    }
}

# --- セットアップ画面 ---
if st.session_state.game_step == "setup":
    st.header("1. 配信スポット（難易度）を選択")
    spot_name = st.selectbox("スポットを選択...", list(spot_settings.keys()))
    conf = spot_settings[spot_name]

    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(conf['enemy_img'], caption=spot_name)
    with col2:
        st.subheader("ミッション")
        st.write(f"**目的:** {int(3*conf['required_time'])}秒間、声を出さずに探索をレポートせよ。")
        st.write(f"**ヒント:** {conf['description']}")
        st.warning("⚠️ 絶叫（一定以上の音量）は配信終了（ゲームオーバー）を意味する。")

    if st.button("配信開始！"):
        st.session_state.spot_name = spot_name
        st.session_state.game_step = "streaming"
        st.rerun()

# --- 配信（録音）画面 ---
elif st.session_state.game_step == "streaming":
    conf = spot_settings[st.session_state.spot_name]
    st.header(f"🛑 LIVE: {st.session_state.spot_name}")
    
    # 配信画面演出
    enemy_placeholder = st.empty()
    enemy_placeholder.image(conf['enemy_img'], caption="探索中...")

    st.markdown("---")
    st.subheader("📹 配信者への指示")
    st.error("「小声でレポートを続けてください...」")
    st.write(f"（目標探索時間: {int(3*conf['required_time'])}秒）")

    # 移動距離ゲージ
    progress_bar = st.progress(0, text="探索進捗: 0%")

    # マイク入力
    # note: st.audio_input は標準で「録音中」にゲージのような波形が表示されます。
    # ここでは、録音ボタンが押された後、解析に移る前の間に、
    # Streamlitの処理時間を使って擬似的にゲージを進める演出を行います。
    audio_file = st.audio_input("ここを長押ししてレポート（探索）開始")

    if audio_file:
        # 録音データを取得
        audio_bytes = audio_file.read()
        audio_data = np.frombuffer(audio_bytes, dtype=np.int16, offset=44)
        
        if len(audio_data) > 0:
            # 音声解析
            duration = len(audio_data) / 44100.0 # サンプリングレート44.1kHzと仮定
            max_vol = np.max(np.abs(audio_data)) / 32768.0

            # ゲージ演出（録音時間に合わせて進める）
            for p in range(101):
                time.sleep(duration / 100)
                # 実際の録音時間と、目標時間を比較してゲージを進める
                progress_score = min(100, int((duration / conf['required_time']) * p))
                progress_bar.progress(progress_score, text=f"探索進捗: {progress_score}%")
                if progress_score >= 100:
                    break

            st.session_state.current_vol = max_vol
            st.session_state.recording_duration = duration
            st.session_state.game_step = "result"
            time.sleep(0.5) # 演出のためのタメ
            st.rerun()

# --- 結果画面 ---
elif st.session_state.game_step == "result":
    conf = spot_settings[st.session_state.spot_name]
    max_vol = st.session_state.current_vol
    duration = st.session_state.recording_duration

    st.header("📹 配信終了")
    
    col1, col2 = st.columns([2, 1])

    with col1:
        if max_vol > conf['threshold']:
            # ゲームオーバー演出
            st.image(conf['outimg'], caption="!!! ??? !!!")
            st.error("（謎のノイズと共に配信が途切れた）")
            st.write(f"最大音量: **{max_vol:.3f}** (しきい値: {conf['threshold']})")
        
        elif duration < conf['required_time']:
            # 時間足りない
            st.image(conf['enemy_img'], caption="...")
            st.warning("配信者「...あれ？ 何も起きないですね？」")
            st.warning(f"（探索時間が足りなかったようだ。あと {conf['required_time'] - duration:.1f}秒必要）")
        
        else:
            # クリア演出
            st.image("assets/aclear.png", caption="生還")
            st.success("配信者「ふぅ、なんとか無事に脱出できました...」")
            st.success("（配信は伝説となった）")
            st.balloons()

    with col2:
        st.subheader("配信ログ")
        st.write(f"スポット: {st.session_state.spot_name}")
        st.write(f"探索時間: {duration:.1f}s")
        st.write(f"最大音量: {max_vol:.3f}")
        
        if st.button("別のスポットへ移動"):
            st.session_state.game_step = "setup"
            st.rerun()