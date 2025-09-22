"""
Pomodoro Timer Application - Main Interface
カスタマイズ性の向上（パターンB）メインアプリケーション
"""

import os
import time
from pomodoro_timer import PomodoroTimer, TimerSettings, Theme, SoundSettings


class PomodoroApp:
    """ポモドーロタイマーアプリケーションのメインクラス"""
    
    def __init__(self):
        # デフォルト設定でタイマーを初期化
        default_settings = TimerSettings(
            work_duration=25,
            break_duration=5,
            theme=Theme.LIGHT,
            sound_settings=SoundSettings(start_sound=True, end_sound=True, tick_sound=False)
        )
        
        self.timer = PomodoroTimer(default_settings)
        self.running = True
        
        # イベントハンドラーを設定
        self.timer.on_timer_start = self._on_timer_start
        self.timer.on_timer_end = self._on_timer_end
        self.timer.on_timer_tick = self._on_timer_tick
        self.timer.on_break_start = self._on_break_start
        self.timer.on_settings_changed = self._on_settings_changed
    
    def run(self):
        """メインアプリケーションループ"""
        self._clear_screen()
        self._print_welcome()
        
        while self.running:
            try:
                self._display_status()
                self._display_menu()
                choice = input("\n選択してください: ").strip()
                self._handle_menu_choice(choice)
                
                if choice != 'q':
                    input("\nEnterキーを押して続行...")
                    
            except KeyboardInterrupt:
                print("\n\nアプリケーションを終了しています...")
                self.running = False
            except Exception as e:
                print(f"\nエラーが発生しました: {e}")
                input("Enterキーを押して続行...")
    
    def _clear_screen(self):
        """画面をクリア"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _print_welcome(self):
        """ウェルカムメッセージを表示"""
        print("=" * 60)
        print("🍅 ポモドーロタイマー - カスタマイズ版（パターンB）")
        print("=" * 60)
        print("個人の好みに合わせた設定でユーザー継続率を向上！")
        print()
    
    def _display_status(self):
        """現在の状態を表示"""
        self._clear_screen()
        self._print_welcome()
        
        # テーマに応じた色表示（シミュレーション）
        theme_config = self.timer.get_current_theme_config()
        print(f"🎨 現在のテーマ: {self.timer.settings.theme.value} テーマ")
        print(f"   背景色: {theme_config['background']}")
        print(f"   文字色: {theme_config['text']}")
        print(f"   アクセント色: {theme_config['accent']}")
        print()
        
        # セッション情報
        session_info = self.timer.get_session_info()
        print(f"📊 セッション状況:")
        print(f"   状態: {session_info['state']}")
        print(f"   種類: {session_info['session_type']}")
        print(f"   残り時間: {session_info['remaining_time']}")
        print(f"   進捗: {session_info['progress_percentage']:.1f}%")
        print(f"   完了したポモドーロ: {session_info['completed_pomodoros']}")
        print()
        
        # 現在の設定
        print(f"⚙️  現在の設定:")
        print(f"   作業時間: {self.timer.settings.work_duration}分")
        print(f"   休憩時間: {self.timer.settings.break_duration}分")
        print(f"   開始音: {'ON' if self.timer.settings.sound_settings.start_sound else 'OFF'}")
        print(f"   終了音: {'ON' if self.timer.settings.sound_settings.end_sound else 'OFF'}")
        print(f"   tick音: {'ON' if self.timer.settings.sound_settings.tick_sound else 'OFF'}")
        print()
    
    def _display_menu(self):
        """メニューを表示"""
        print("📋 メニュー:")
        print("   1. タイマー開始/再開")
        print("   2. タイマー一時停止")
        print("   3. タイマー停止")
        print("   4. タイマーリセット")
        print("   5. 作業時間設定 (15/25/35/45分)")
        print("   6. 休憩時間設定 (5/10/15分)")
        print("   7. テーマ変更 (ライト/ダーク/フォーカス)")
        print("   8. サウンド設定")
        print("   9. 設定プリセット")
        print("   s. 現在の状態表示")
        print("   q. 終了")
    
    def _handle_menu_choice(self, choice: str):
        """メニュー選択を処理"""
        if choice == '1':
            self._start_timer()
        elif choice == '2':
            self._pause_timer()
        elif choice == '3':
            self._stop_timer()
        elif choice == '4':
            self._reset_timer()
        elif choice == '5':
            self._configure_work_time()
        elif choice == '6':
            self._configure_break_time()
        elif choice == '7':
            self._configure_theme()
        elif choice == '8':
            self._configure_sound()
        elif choice == '9':
            self._configure_presets()
        elif choice == 's':
            pass  # 状態は自動で表示される
        elif choice == 'q':
            self._quit_application()
        else:
            print("無効な選択です。")
    
    def _start_timer(self):
        """タイマーを開始"""
        if self.timer.start_timer():
            print("✅ タイマーを開始しました！")
        else:
            print("❌ タイマーを開始できませんでした。")
    
    def _pause_timer(self):
        """タイマーを一時停止"""
        if self.timer.pause_timer():
            print("⏸️ タイマーを一時停止しました。")
        else:
            print("❌ タイマーを一時停止できませんでした。")
    
    def _stop_timer(self):
        """タイマーを停止"""
        if self.timer.stop_timer():
            print("⏹️ タイマーを停止しました。")
        else:
            print("❌ タイマーを停止できませんでした。")
    
    def _reset_timer(self):
        """タイマーをリセット"""
        if self.timer.reset_timer():
            print("🔄 タイマーをリセットしました。")
        else:
            print("❌ タイマーをリセットできませんでした。")
    
    def _configure_work_time(self):
        """作業時間を設定"""
        print("\n⏰ 作業時間設定:")
        for i, duration in enumerate(PomodoroTimer.WORK_TIME_OPTIONS, 1):
            marker = "👈" if duration == self.timer.settings.work_duration else "  "
            print(f"   {i}. {duration}分 {marker}")
        
        try:
            choice = int(input("選択してください (1-4): ")) - 1
            if 0 <= choice < len(PomodoroTimer.WORK_TIME_OPTIONS):
                duration = PomodoroTimer.WORK_TIME_OPTIONS[choice]
                if self.timer.set_work_duration(duration):
                    print(f"✅ 作業時間を{duration}分に設定しました。")
                else:
                    print("❌ 設定に失敗しました。")
            else:
                print("❌ 無効な選択です。")
        except ValueError:
            print("❌ 数字を入力してください。")
    
    def _configure_break_time(self):
        """休憩時間を設定"""
        print("\n☕ 休憩時間設定:")
        for i, duration in enumerate(PomodoroTimer.BREAK_TIME_OPTIONS, 1):
            marker = "👈" if duration == self.timer.settings.break_duration else "  "
            print(f"   {i}. {duration}分 {marker}")
        
        try:
            choice = int(input("選択してください (1-3): ")) - 1
            if 0 <= choice < len(PomodoroTimer.BREAK_TIME_OPTIONS):
                duration = PomodoroTimer.BREAK_TIME_OPTIONS[choice]
                if self.timer.set_break_duration(duration):
                    print(f"✅ 休憩時間を{duration}分に設定しました。")
                else:
                    print("❌ 設定に失敗しました。")
            else:
                print("❌ 無効な選択です。")
        except ValueError:
            print("❌ 数字を入力してください。")
    
    def _configure_theme(self):
        """テーマを設定"""
        print("\n🎨 テーマ設定:")
        themes = list(Theme)
        for i, theme in enumerate(themes, 1):
            marker = "👈" if theme == self.timer.settings.theme else "  "
            config = PomodoroTimer.THEME_CONFIGS[theme]
            print(f"   {i}. {theme.value} (背景: {config['background']}, 文字: {config['text']}) {marker}")
        
        try:
            choice = int(input("選択してください (1-3): ")) - 1
            if 0 <= choice < len(themes):
                theme = themes[choice]
                if self.timer.set_theme(theme):
                    print(f"✅ テーマを{theme.value}に設定しました。")
                else:
                    print("❌ 設定に失敗しました。")
            else:
                print("❌ 無効な選択です。")
        except ValueError:
            print("❌ 数字を入力してください。")
    
    def _configure_sound(self):
        """サウンド設定"""
        print("\n🔊 サウンド設定:")
        print(f"   1. 開始音: {'ON' if self.timer.settings.sound_settings.start_sound else 'OFF'}")
        print(f"   2. 終了音: {'ON' if self.timer.settings.sound_settings.end_sound else 'OFF'}")
        print(f"   3. tick音: {'ON' if self.timer.settings.sound_settings.tick_sound else 'OFF'}")
        print("   4. 戻る")
        
        try:
            choice = int(input("切り替えたい項目を選択してください (1-4): "))
            if choice == 1:
                status = self.timer.toggle_start_sound()
                print(f"✅ 開始音を{'ON' if status else 'OFF'}にしました。")
            elif choice == 2:
                status = self.timer.toggle_end_sound()
                print(f"✅ 終了音を{'ON' if status else 'OFF'}にしました。")
            elif choice == 3:
                status = self.timer.toggle_tick_sound()
                print(f"✅ tick音を{'ON' if status else 'OFF'}にしました。")
            elif choice == 4:
                return
            else:
                print("❌ 無効な選択です。")
        except ValueError:
            print("❌ 数字を入力してください。")
    
    def _configure_presets(self):
        """設定プリセット"""
        print("\n⚡ 設定プリセット:")
        print("   1. 標準設定 (25分作業/5分休憩, ライトテーマ)")
        print("   2. 短時間集中 (15分作業/5分休憩, フォーカステーマ)")
        print("   3. 長時間作業 (45分作業/15分休憩, ダークテーマ)")
        print("   4. 戻る")
        
        try:
            choice = int(input("選択してください (1-4): "))
            if choice == 1:
                self._apply_standard_preset()
            elif choice == 2:
                self._apply_focus_preset()
            elif choice == 3:
                self._apply_long_work_preset()
            elif choice == 4:
                return
            else:
                print("❌ 無効な選択です。")
        except ValueError:
            print("❌ 数字を入力してください。")
    
    def _apply_standard_preset(self):
        """標準設定プリセットを適用"""
        self.timer.set_work_duration(25)
        self.timer.set_break_duration(5)
        self.timer.set_theme(Theme.LIGHT)
        self.timer.settings.sound_settings.start_sound = True
        self.timer.settings.sound_settings.end_sound = True
        self.timer.settings.sound_settings.tick_sound = False
        print("✅ 標準設定プリセットを適用しました。")
    
    def _apply_focus_preset(self):
        """短時間集中プリセットを適用"""
        self.timer.set_work_duration(15)
        self.timer.set_break_duration(5)
        self.timer.set_theme(Theme.FOCUS)
        self.timer.settings.sound_settings.start_sound = True
        self.timer.settings.sound_settings.end_sound = True
        self.timer.settings.sound_settings.tick_sound = True
        print("✅ 短時間集中プリセットを適用しました。")
    
    def _apply_long_work_preset(self):
        """長時間作業プリセットを適用"""
        self.timer.set_work_duration(45)
        self.timer.set_break_duration(15)
        self.timer.set_theme(Theme.DARK)
        self.timer.settings.sound_settings.start_sound = True
        self.timer.settings.sound_settings.end_sound = True
        self.timer.settings.sound_settings.tick_sound = False
        print("✅ 長時間作業プリセットを適用しました。")
    
    def _quit_application(self):
        """アプリケーションを終了"""
        print("👋 ポモドーロタイマーを終了します。お疲れ様でした！")
        self.timer.stop_timer()
        self.running = False
    
    # イベントハンドラー
    def _on_timer_start(self, timer):
        """タイマー開始時のイベントハンドラー"""
        session_type = "作業" if timer.is_work_session else "休憩"
        print(f"\n🚀 {session_type}セッションを開始しました！")
    
    def _on_timer_end(self, timer):
        """タイマー終了時のイベントハンドラー"""
        session_type = "作業" if timer.is_work_session else "休憩"
        print(f"\n✅ {session_type}セッションが完了しました！")
    
    def _on_timer_tick(self, timer):
        """タイマーtick時のイベントハンドラー"""
        # tick音が有効な場合の表示（実際の音は_play_tick_soundで処理）
        pass
    
    def _on_break_start(self, timer):
        """休憩開始時のイベントハンドラー"""
        print(f"\n☕ 休憩時間です！{timer.settings.break_duration}分間リラックスしましょう。")
    
    def _on_settings_changed(self, timer):
        """設定変更時のイベントハンドラー"""
        # 設定変更の記録やログ出力など
        pass


if __name__ == "__main__":
    app = PomodoroApp()
    app.run()
