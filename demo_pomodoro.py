"""
Demo script showcasing all customization features
カスタマイズ機能のデモンストレーション
"""

from pomodoro_timer import PomodoroTimer, TimerSettings, Theme, SoundSettings
import time


def demo_customization_features():
    """全カスタマイズ機能のデモンストレーション"""
    print("=" * 70)
    print("🍅 ポモドーロタイマー カスタマイズ機能デモ（パターンB）")
    print("=" * 70)
    print("個人の好みに合わせた設定でユーザー継続率を測定します")
    print()
    
    # デフォルト設定でタイマー作成
    timer = PomodoroTimer()
    
    def print_status(title):
        """現在の状態を表示"""
        print(f"\n📋 {title}")
        print("-" * 50)
        session_info = timer.get_session_info()
        theme_config = timer.get_current_theme_config()
        
        print(f"🎨 テーマ: {timer.settings.theme.value}")
        print(f"   背景: {theme_config['background']}, 文字: {theme_config['text']}")
        print(f"⏰ 時間設定: 作業{timer.settings.work_duration}分 / 休憩{timer.settings.break_duration}分")
        print(f"🔊 サウンド: 開始音{'ON' if timer.settings.sound_settings.start_sound else 'OFF'} "
              f"終了音{'ON' if timer.settings.sound_settings.end_sound else 'OFF'} "
              f"tick音{'ON' if timer.settings.sound_settings.tick_sound else 'OFF'}")
        print(f"📊 状態: {session_info['session_type']} ({session_info['remaining_time']})")
    
    # 1. 初期状態
    print_status("初期設定 (標準)")
    
    # 2. カスタマイズ例1: 短時間集中モード
    print("\n" + "="*70)
    print("🚀 カスタマイズ例1: 短時間集中モード")
    print("="*70)
    
    timer.set_work_duration(15)  # 15分作業
    timer.set_break_duration(5)  # 5分休憩
    timer.set_theme(Theme.FOCUS)  # フォーカステーマ
    timer.toggle_tick_sound()  # tick音ON
    
    print_status("短時間集中モード適用後")
    
    # 3. カスタマイズ例2: 長時間作業モード
    print("\n" + "="*70)
    print("🌙 カスタマイズ例2: 長時間作業モード")
    print("="*70)
    
    timer.set_work_duration(45)  # 45分作業
    timer.set_break_duration(15)  # 15分休憩
    timer.set_theme(Theme.DARK)  # ダークテーマ
    timer.toggle_tick_sound()  # tick音OFF
    
    print_status("長時間作業モード適用後")
    
    # 4. カスタマイズ例3: サイレントモード
    print("\n" + "="*70)
    print("🔇 カスタマイズ例3: サイレントモード")
    print("="*70)
    
    timer.set_work_duration(25)  # 標準25分作業
    timer.set_break_duration(10)  # 10分休憩
    timer.set_theme(Theme.LIGHT)  # ライトテーマ
    timer.toggle_start_sound()  # 開始音OFF
    timer.toggle_end_sound()  # 終了音OFF
    
    print_status("サイレントモード適用後")
    
    # 5. 全時間オプションの表示
    print("\n" + "="*70)
    print("⏰ 利用可能な時間設定オプション")
    print("="*70)
    
    print("📅 作業時間オプション:")
    for i, work_time in enumerate(PomodoroTimer.WORK_TIME_OPTIONS, 1):
        print(f"   {i}. {work_time}分 {'👈' if work_time == timer.settings.work_duration else ''}")
    
    print("\n☕ 休憩時間オプション:")
    for i, break_time in enumerate(PomodoroTimer.BREAK_TIME_OPTIONS, 1):
        print(f"   {i}. {break_time}分 {'👈' if break_time == timer.settings.break_duration else ''}")
    
    # 6. 全テーマオプションの表示
    print("\n🎨 利用可能なテーマオプション:")
    for theme in Theme:
        config = PomodoroTimer.THEME_CONFIGS[theme]
        current = "👈" if theme == timer.settings.theme else ""
        print(f"   {theme.value}: 背景{config['background']} 文字{config['text']} {current}")
    
    # 7. ユーザー継続率測定のメトリクス
    print("\n" + "="*70)
    print("📈 ユーザー継続率測定メトリクス")
    print("="*70)
    
    print("測定可能な指標:")
    print("   • 完了したポモドーロ数")
    print("   • セッション継続時間")
    print("   • 設定変更頻度")
    print("   • 好みのテーマ使用率")
    print("   • カスタム時間設定の効果")
    print("   • サウンド設定の継続性への影響")
    
    # 8. 短いタイマーデモ
    print("\n" + "="*70)
    print("⏱️  実際のタイマー動作デモ（3秒）")
    print("="*70)
    
    # デモ用設定
    demo_timer = PomodoroTimer(TimerSettings(work_duration=25, break_duration=5))
    demo_timer.remaining_time = 3  # 3秒でデモ
    
    # イベントハンドラー
    def on_start(timer):
        print("🚀 タイマー開始！")
    
    def on_tick(timer):
        print(f"⏰ 残り時間: {timer.get_remaining_time_formatted()}")
    
    def on_end(timer):
        session_type = "作業" if timer.is_work_session else "休憩"
        print(f"✅ {session_type}セッション完了！")
    
    demo_timer.on_timer_start = on_start
    demo_timer.on_timer_tick = on_tick
    demo_timer.on_timer_end = on_end
    
    demo_timer.start_timer()
    time.sleep(4)  # デモ実行
    
    print("\n" + "="*70)
    print("🎉 カスタマイズ機能デモ完了")
    print("="*70)
    print("✨ 個人の好みに合わせた設定により、ユーザーの継続率向上が期待されます")
    print("🔄 継続的な使用データ収集により、さらなる改善が可能です")


if __name__ == "__main__":
    demo_customization_features()