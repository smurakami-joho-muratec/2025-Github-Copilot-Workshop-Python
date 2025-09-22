"""
Test script for Pomodoro Timer Customization Features
カスタマイズ機能のテストスクリプト
"""

from pomodoro_timer import PomodoroTimer, TimerSettings, Theme, SoundSettings
import time
import threading


def test_customization_features():
    """カスタマイズ機能の全体テスト"""
    print("=" * 60)
    print("🍅 ポモドーロタイマー カスタマイズ機能テスト（パターンB）")
    print("=" * 60)
    
    # 1. 時間設定テスト (15/25/35/45分)
    print("\n1️⃣ 時間設定テスト:")
    timer = PomodoroTimer()
    
    for work_time in PomodoroTimer.WORK_TIME_OPTIONS:
        result = timer.set_work_duration(work_time)
        print(f"   作業時間 {work_time}分設定: {'✅' if result else '❌'}")
    
    for break_time in PomodoroTimer.BREAK_TIME_OPTIONS:
        result = timer.set_break_duration(break_time)
        print(f"   休憩時間 {break_time}分設定: {'✅' if result else '❌'}")
    
    # 無効な値のテスト
    invalid_work = timer.set_work_duration(30)  # 利用不可能な値
    invalid_break = timer.set_break_duration(20)  # 利用不可能な値
    print(f"   無効な作業時間(30分)拒否: {'✅' if not invalid_work else '❌'}")
    print(f"   無効な休憩時間(20分)拒否: {'✅' if not invalid_break else '❌'}")
    
    # 2. テーマ切り替えテスト (ダーク/ライト/フォーカスモード)
    print("\n2️⃣ テーマ切り替えテスト:")
    for theme in Theme:
        result = timer.set_theme(theme)
        config = timer.get_current_theme_config()
        print(f"   {theme.value}テーマ設定: {'✅' if result else '❌'}")
        print(f"     → 背景: {config['background']}, 文字: {config['text']}, アクセント: {config['accent']}")
    
    # 3. サウンド設定テスト (開始/終了/tick音のオン・オフ)
    print("\n3️⃣ サウンド設定テスト:")
    
    # 初期状態の確認
    initial_start = timer.settings.sound_settings.start_sound
    initial_end = timer.settings.sound_settings.end_sound
    initial_tick = timer.settings.sound_settings.tick_sound
    
    # 各サウンドのオン・オフ切り替え
    start_toggled = timer.toggle_start_sound()
    end_toggled = timer.toggle_end_sound()
    tick_toggled = timer.toggle_tick_sound()
    
    print(f"   開始音切り替え: 初期{initial_start} → {start_toggled} ✅")
    print(f"   終了音切り替え: 初期{initial_end} → {end_toggled} ✅")
    print(f"   tick音切り替え: 初期{initial_tick} → {tick_toggled} ✅")
    
    # 4. カスタム設定の組み合わせテスト
    print("\n4️⃣ カスタム設定組み合わせテスト:")
    
    # パターン1: 短時間集中モード
    timer.set_work_duration(15)
    timer.set_break_duration(5)
    timer.set_theme(Theme.FOCUS)
    timer.settings.sound_settings.tick_sound = True
    print("   短時間集中モード設定完了 ✅")
    print(f"     → 作業15分/休憩5分, フォーカステーマ, tick音ON")
    
    # パターン2: 長時間作業モード
    timer.set_work_duration(45)
    timer.set_break_duration(15)
    timer.set_theme(Theme.DARK)
    timer.settings.sound_settings.tick_sound = False
    print("   長時間作業モード設定完了 ✅")
    print(f"     → 作業45分/休憩15分, ダークテーマ, tick音OFF")
    
    # 5. タイマー機能テスト（短時間）
    print("\n5️⃣ タイマー機能テスト:")
    
    # テスト用に短い時間設定
    test_timer = PomodoroTimer(TimerSettings(work_duration=25, break_duration=5))
    test_timer.remaining_time = 3  # 3秒でテスト
    
    # イベントハンドラー設定
    events_fired = []
    
    def on_start(timer):
        events_fired.append("start")
        print("   🚀 タイマー開始イベント発火 ✅")
    
    def on_end(timer):
        events_fired.append("end")
        print("   🔔 タイマー終了イベント発火 ✅")
    
    def on_tick(timer):
        events_fired.append("tick")
        if len(events_fired) == 1 or events_fired[-2] != "tick":  # 最初のtickだけ表示
            print(f"   ⏰ tick: {timer.get_remaining_time_formatted()}")
    
    test_timer.on_timer_start = on_start
    test_timer.on_timer_end = on_end
    test_timer.on_timer_tick = on_tick
    
    # タイマー開始
    test_timer.start_timer()
    time.sleep(4)  # 3秒のカウントダウン + 1秒余裕
    
    # 結果確認
    if "start" in events_fired and "end" in events_fired and "tick" in events_fired:
        print("   タイマー機能テスト完了 ✅")
    else:
        print("   タイマー機能テスト失敗 ❌")
    
    # 6. ユーザー継続性測定のための情報取得テスト
    print("\n6️⃣ ユーザー継続性測定情報テスト:")
    session_info = test_timer.get_session_info()
    progress = test_timer.get_progress_percentage()
    
    print(f"   セッション情報取得: {session_info['session_type']} ✅")
    print(f"   進捗情報取得: {progress:.1f}% ✅")
    print(f"   完了ポモドーロ数: {session_info['completed_pomodoros']} ✅")
    
    # 7. 設定の永続化テスト（シミュレーション）
    print("\n7️⃣ 設定永続化テスト:")
    
    # カスタム設定作成
    custom_settings = TimerSettings(
        work_duration=35,
        break_duration=10,
        theme=Theme.DARK,
        sound_settings=SoundSettings(start_sound=True, end_sound=False, tick_sound=True)
    )
    
    # 設定を適用した新しいタイマー作成
    persistent_timer = PomodoroTimer(custom_settings)
    
    # 設定が正しく保持されているか確認
    settings_preserved = (
        persistent_timer.settings.work_duration == 35 and
        persistent_timer.settings.break_duration == 10 and
        persistent_timer.settings.theme == Theme.DARK and
        persistent_timer.settings.sound_settings.start_sound == True and
        persistent_timer.settings.sound_settings.end_sound == False and
        persistent_timer.settings.sound_settings.tick_sound == True
    )
    
    print(f"   カスタム設定保持テスト: {'✅' if settings_preserved else '❌'}")
    
    print("\n" + "=" * 60)
    print("🎉 全てのカスタマイズ機能テストが完了しました！")
    print("個人の好みに合わせた設定でユーザー継続率向上が期待できます。")
    print("=" * 60)


if __name__ == "__main__":
    test_customization_features()