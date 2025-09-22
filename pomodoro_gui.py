import tkinter as tk
from tkinter import ttk, messagebox
import math
import time
from pomodoro_timer import PomodoroTimer, TimerConfig, TimerState, VisualEffects


class CircularProgressBar:
    """円形プログレスバー"""
    
    def __init__(self, canvas: tk.Canvas, x: int, y: int, radius: int):
        self.canvas = canvas
        self.center_x = x
        self.center_y = y
        self.radius = radius
        self.progress = 0.0
        self.color = "#4a90e2"  # 初期色（青）
        
        # 背景円を描画
        self.bg_circle = self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            outline="#e0e0e0", width=8, fill=""
        )
        
        # プログレス円弧を描画
        self.progress_arc = self.canvas.create_arc(
            x - radius, y - radius, x + radius, y + radius,
            start=90, extent=0, outline=self.color, width=8,
            style="arc"
        )
    
    def update_progress(self, progress: float, timer_state: TimerState):
        """プログレス更新"""
        self.progress = max(0.0, min(1.0, progress))
        
        # 色を計算（時間経過に応じて青→黄→赤）
        self.color = self.calculate_color(progress, timer_state)
        
        # 円弧の角度を計算（時計回りで減少）
        extent = -360 * self.progress
        
        # 円弧を更新
        self.canvas.itemconfig(self.progress_arc, 
                             extent=extent, outline=self.color)
    
    def calculate_color(self, progress: float, timer_state: TimerState) -> str:
        """進捗に応じた色を計算"""
        if timer_state == TimerState.COMPLETED:
            return "#4caf50"  # 緑（完了）
        elif timer_state == TimerState.PAUSED:
            return "#ff9800"  # オレンジ（一時停止）
        
        # 作業時間の色変化：青→黄→赤
        if progress < 0.5:
            # 青から黄へ（0-50%）
            ratio = progress * 2
            r = int(74 + (255 - 74) * ratio)
            g = int(144 + (193 - 144) * ratio)
            b = int(226 + (7 - 226) * ratio)
        else:
            # 黄から赤へ（50-100%）
            ratio = (progress - 0.5) * 2
            r = int(255)
            g = int(193 - (193 - 87) * ratio)
            b = int(7)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def reset(self):
        """リセット"""
        self.progress = 0.0
        self.color = "#4a90e2"
        self.canvas.itemconfig(self.progress_arc, extent=0, outline=self.color)


class PomodoroGUI:
    """Pomodoro GUI クラス"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pomodoro Timer - 視覚的フィードバック強化版")
        self.root.geometry("500x600")
        self.root.configure(bg="#2c3e50")
        
        # タイマー初期化
        self.timer = PomodoroTimer()
        self.timer.on_state_changed = self.on_timer_state_changed
        self.timer.on_time_updated = self.on_timer_updated
        self.timer.on_session_completed = self.on_session_completed
        
        # GUI要素を作成
        self.create_widgets()
        
        # 視覚効果初期化
        self.visual_effects = VisualEffects(self.canvas)
        
        # 更新ループ開始
        self.update_timer()
    
    def create_widgets(self):
        """GUI要素作成"""
        # タイトル
        title_label = tk.Label(
            self.root, 
            text="🍅 Pomodoro Timer",
            font=("Arial", 20, "bold"),
            fg="#ecf0f1",
            bg="#2c3e50"
        )
        title_label.pack(pady=20)
        
        # キャンバス（プログレスバーと背景エフェクト用）
        self.canvas = tk.Canvas(
            self.root,
            width=300,
            height=300,
            bg="#34495e",
            highlightthickness=0
        )
        self.canvas.pack(pady=20)
        
        # 円形プログレスバー
        self.progress_bar = CircularProgressBar(
            self.canvas, 150, 150, 120
        )
        
        # 時間表示
        self.time_label = tk.Label(
            self.canvas,
            text="25:00",
            font=("Arial", 24, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        )
        self.time_window = self.canvas.create_window(
            150, 150, window=self.time_label
        )
        
        # セッション情報
        self.session_label = tk.Label(
            self.root,
            text="作業セッション | セッション: 0",
            font=("Arial", 12),
            fg="#bdc3c7",
            bg="#2c3e50"
        )
        self.session_label.pack(pady=10)
        
        # ボタンフレーム
        button_frame = tk.Frame(self.root, bg="#2c3e50")
        button_frame.pack(pady=20)
        
        # ボタンスタイル
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.TButton",
                       font=("Arial", 12, "bold"),
                       padding=10)
        
        # 開始/一時停止ボタン
        self.start_pause_button = ttk.Button(
            button_frame,
            text="開始",
            style="Custom.TButton",
            command=self.toggle_timer
        )
        self.start_pause_button.pack(side=tk.LEFT, padx=10)
        
        # 停止ボタン
        self.stop_button = ttk.Button(
            button_frame,
            text="停止",
            style="Custom.TButton",
            command=self.stop_timer
        )
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        # 設定ボタン
        self.settings_button = ttk.Button(
            button_frame,
            text="設定",
            style="Custom.TButton",
            command=self.show_settings
        )
        self.settings_button.pack(side=tk.LEFT, padx=10)
        
        # 統計表示
        stats_frame = tk.Frame(self.root, bg="#2c3e50")
        stats_frame.pack(pady=20)
        
        self.stats_label = tk.Label(
            stats_frame,
            text="本日の完了セッション: 0 | 合計時間: 0分",
            font=("Arial", 10),
            fg="#95a5a6",
            bg="#2c3e50"
        )
        self.stats_label.pack()
    
    def toggle_timer(self):
        """タイマー開始/一時停止切り替え"""
        if self.timer.state == TimerState.IDLE or self.timer.state == TimerState.PAUSED:
            self.timer.start()
        elif self.timer.state == TimerState.RUNNING:
            self.timer.pause()
    
    def stop_timer(self):
        """タイマー停止"""
        self.timer.stop()
        self.progress_bar.reset()
        self.visual_effects.stop_background_effects()
    
    def show_settings(self):
        """設定画面表示"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("タイマー設定")
        settings_window.geometry("300x250")
        settings_window.configure(bg="#2c3e50")
        
        # 作業時間設定
        tk.Label(
            settings_window,
            text="作業時間 (分):",
            fg="#ecf0f1",
            bg="#2c3e50"
        ).pack(pady=5)
        
        work_var = tk.StringVar(value=str(self.timer.config.work_duration // 60))
        work_entry = tk.Entry(settings_window, textvariable=work_var)
        work_entry.pack(pady=5)
        
        # 短い休憩時間設定
        tk.Label(
            settings_window,
            text="短い休憩時間 (分):",
            fg="#ecf0f1",
            bg="#2c3e50"
        ).pack(pady=5)
        
        break_var = tk.StringVar(value=str(self.timer.config.break_duration // 60))
        break_entry = tk.Entry(settings_window, textvariable=break_var)
        break_entry.pack(pady=5)
        
        # 長い休憩時間設定
        tk.Label(
            settings_window,
            text="長い休憩時間 (分):",
            fg="#ecf0f1",
            bg="#2c3e50"
        ).pack(pady=5)
        
        long_break_var = tk.StringVar(value=str(self.timer.config.long_break_duration // 60))
        long_break_entry = tk.Entry(settings_window, textvariable=long_break_var)
        long_break_entry.pack(pady=5)
        
        def save_settings():
            try:
                self.timer.config.work_duration = int(work_var.get()) * 60
                self.timer.config.break_duration = int(break_var.get()) * 60
                self.timer.config.long_break_duration = int(long_break_var.get()) * 60
                settings_window.destroy()
                messagebox.showinfo("設定", "設定が保存されました！")
            except ValueError:
                messagebox.showerror("エラー", "有効な数値を入力してください")
        
        ttk.Button(
            settings_window,
            text="保存",
            command=save_settings
        ).pack(pady=20)
    
    def on_timer_state_changed(self, state: TimerState):
        """タイマー状態変更時のコールバック"""
        if state == TimerState.RUNNING:
            self.start_pause_button.config(text="一時停止")
            self.visual_effects.start_background_effects()
        elif state == TimerState.PAUSED:
            self.start_pause_button.config(text="再開")
            self.visual_effects.stop_background_effects()
        elif state == TimerState.IDLE:
            self.start_pause_button.config(text="開始")
            self.visual_effects.stop_background_effects()
        elif state == TimerState.COMPLETED:
            self.start_pause_button.config(text="開始")
            self.visual_effects.stop_background_effects()
    
    def on_timer_updated(self, remaining_time: float, total_time: int):
        """タイマー更新時のコールバック"""
        # 時間表示更新
        self.time_label.config(text=self.timer.format_time(int(remaining_time)))
        
        # プログレスバー更新
        progress = self.timer.get_progress_ratio()
        self.progress_bar.update_progress(progress, self.timer.state)
    
    def on_session_completed(self, was_work_session: bool, session_count: int):
        """セッション完了時のコールバック"""
        if was_work_session:
            messagebox.showinfo("セッション完了", "作業セッションが完了しました！\n休憩を取りましょう。")
        else:
            messagebox.showinfo("休憩終了", "休憩が終了しました！\n次の作業セッションを始めましょう。")
    
    def update_timer(self):
        """タイマー更新ループ"""
        self.timer.update()
        
        # セッション情報更新
        session_type = "作業セッション" if self.timer.is_work_session else "休憩セッション"
        self.session_label.config(
            text=f"{session_type} | 完了セッション: {self.timer.total_sessions}"
        )
        
        # 統計更新
        total_minutes = self.timer.total_sessions * (self.timer.config.work_duration // 60)
        self.stats_label.config(
            text=f"本日の完了セッション: {self.timer.total_sessions} | 合計時間: {total_minutes}分"
        )
        
        # 100ms後に再実行
        self.root.after(100, self.update_timer)
    
    def run(self):
        """アプリケーション実行"""
        self.root.mainloop()


if __name__ == "__main__":
    app = PomodoroGUI()
    app.run()