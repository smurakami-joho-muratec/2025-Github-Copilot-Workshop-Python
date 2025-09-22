"""
Pomodoro Timer with Customization Features (Pattern B)
カスタマイズ性の向上パターンB実装
"""

import time
import threading
from enum import Enum
from typing import Dict, Callable, Optional
from dataclasses import dataclass


class TimerState(Enum):
    """タイマーの状態"""
    STOPPED = "stopped"
    RUNNING = "running" 
    PAUSED = "paused"
    BREAK = "break"


class Theme(Enum):
    """テーマの種類"""
    LIGHT = "light"
    DARK = "dark"
    FOCUS = "focus"


@dataclass
class SoundSettings:
    """サウンド設定"""
    start_sound: bool = True
    end_sound: bool = True
    tick_sound: bool = False


@dataclass
class TimerSettings:
    """タイマー設定"""
    work_duration: int = 25  # 作業時間（分）
    break_duration: int = 5  # 休憩時間（分）
    theme: Theme = Theme.LIGHT
    sound_settings: SoundSettings = None
    
    def __post_init__(self):
        if self.sound_settings is None:
            self.sound_settings = SoundSettings()


class PomodoroTimer:
    """カスタマイズ可能なポモドーロタイマー"""
    
    # 利用可能な作業時間オプション（分）
    WORK_TIME_OPTIONS = [15, 25, 35, 45]
    
    # 利用可能な休憩時間オプション（分）
    BREAK_TIME_OPTIONS = [5, 10, 15]
    
    # テーマ設定
    THEME_CONFIGS = {
        Theme.LIGHT: {
            "background": "#FFFFFF",
            "text": "#000000",
            "accent": "#4A90E2"
        },
        Theme.DARK: {
            "background": "#2C3E50", 
            "text": "#FFFFFF",
            "accent": "#E74C3C"
        },
        Theme.FOCUS: {
            "background": "#1E1E1E",
            "text": "#00FF00", 
            "accent": "#FFD700"
        }
    }
    
    def __init__(self, settings: TimerSettings = None):
        self.settings = settings or TimerSettings()
        self.state = TimerState.STOPPED
        self.remaining_time = self.settings.work_duration * 60  # 秒に変換
        self.is_work_session = True
        self.completed_pomodoros = 0
        
        # イベントハンドラー
        self.on_timer_start: Optional[Callable] = None
        self.on_timer_end: Optional[Callable] = None
        self.on_timer_tick: Optional[Callable] = None
        self.on_break_start: Optional[Callable] = None
        self.on_settings_changed: Optional[Callable] = None
        
        # 内部タイマー用
        self._timer_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
    
    def set_work_duration(self, minutes: int) -> bool:
        """作業時間を設定（15/25/35/45分から選択）"""
        if minutes in self.WORK_TIME_OPTIONS:
            self.settings.work_duration = minutes
            if self.is_work_session and self.state == TimerState.STOPPED:
                self.remaining_time = minutes * 60
            self._notify_settings_changed()
            return True
        return False
    
    def set_break_duration(self, minutes: int) -> bool:
        """休憩時間を設定（5/10/15分から選択）"""
        if minutes in self.BREAK_TIME_OPTIONS:
            self.settings.break_duration = minutes
            if not self.is_work_session and self.state == TimerState.STOPPED:
                self.remaining_time = minutes * 60
            self._notify_settings_changed()
            return True
        return False
    
    def set_theme(self, theme: Theme) -> bool:
        """テーマを変更（ダーク/ライト/フォーカスモード）"""
        if isinstance(theme, Theme):
            self.settings.theme = theme
            self._notify_settings_changed()
            return True
        return False
    
    def toggle_start_sound(self) -> bool:
        """開始音のオン・オフ切り替え"""
        self.settings.sound_settings.start_sound = not self.settings.sound_settings.start_sound
        self._notify_settings_changed()
        return self.settings.sound_settings.start_sound
    
    def toggle_end_sound(self) -> bool:
        """終了音のオン・オフ切り替え"""
        self.settings.sound_settings.end_sound = not self.settings.sound_settings.end_sound
        self._notify_settings_changed()
        return self.settings.sound_settings.end_sound
    
    def toggle_tick_sound(self) -> bool:
        """tick音のオン・オフ切り替え"""
        self.settings.sound_settings.tick_sound = not self.settings.sound_settings.tick_sound
        self._notify_settings_changed()
        return self.settings.sound_settings.tick_sound
    
    def start_timer(self) -> bool:
        """タイマーを開始"""
        if self.state in [TimerState.STOPPED, TimerState.PAUSED]:
            self.state = TimerState.RUNNING
            self._play_start_sound()
            self._start_countdown()
            self._notify_timer_start()
            return True
        return False
    
    def pause_timer(self) -> bool:
        """タイマーを一時停止"""
        if self.state == TimerState.RUNNING:
            self.state = TimerState.PAUSED
            self._stop_countdown()
            return True
        return False
    
    def stop_timer(self) -> bool:
        """タイマーを停止"""
        if self.state in [TimerState.RUNNING, TimerState.PAUSED]:
            self.state = TimerState.STOPPED
            self._stop_countdown()
            self._reset_timer()
            return True
        return False
    
    def reset_timer(self) -> bool:
        """タイマーをリセット"""
        self.stop_timer()
        self.is_work_session = True
        self.remaining_time = self.settings.work_duration * 60
        return True
    
    def get_current_theme_config(self) -> Dict[str, str]:
        """現在のテーマ設定を取得"""
        return self.THEME_CONFIGS[self.settings.theme].copy()
    
    def get_remaining_time_formatted(self) -> str:
        """残り時間を「MM:SS」形式で取得"""
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_progress_percentage(self) -> float:
        """進捗をパーセンテージで取得"""
        total_time = (self.settings.work_duration if self.is_work_session 
                     else self.settings.break_duration) * 60
        return ((total_time - self.remaining_time) / total_time) * 100
    
    def get_session_info(self) -> Dict:
        """現在のセッション情報を取得"""
        return {
            "is_work_session": self.is_work_session,
            "session_type": "作業中" if self.is_work_session else "休憩中",
            "completed_pomodoros": self.completed_pomodoros,
            "state": self.state.value,
            "remaining_time": self.get_remaining_time_formatted(),
            "progress_percentage": self.get_progress_percentage()
        }
    
    def _start_countdown(self):
        """カウントダウンを開始"""
        if self._timer_thread and self._timer_thread.is_alive():
            return
        
        self._stop_event.clear()
        self._timer_thread = threading.Thread(target=self._countdown_loop)
        self._timer_thread.daemon = True
        self._timer_thread.start()
    
    def _stop_countdown(self):
        """カウントダウンを停止"""
        self._stop_event.set()
        if self._timer_thread:
            self._timer_thread.join(timeout=1.0)
    
    def _countdown_loop(self):
        """カウントダウンのメインループ"""
        while not self._stop_event.is_set() and self.remaining_time > 0:
            time.sleep(1)
            if self.state == TimerState.RUNNING:
                self.remaining_time -= 1
                self._play_tick_sound()
                self._notify_timer_tick()
        
        if self.remaining_time <= 0:
            self._timer_completed()
    
    def _timer_completed(self):
        """タイマー完了時の処理"""
        self._play_end_sound()
        self._notify_timer_end()
        
        if self.is_work_session:
            # 作業セッション完了 → 休憩開始
            self.completed_pomodoros += 1
            self.is_work_session = False
            self.remaining_time = self.settings.break_duration * 60
            self.state = TimerState.BREAK
            self._notify_break_start()
        else:
            # 休憩完了 → 次の作業セッションへ
            self.is_work_session = True
            self.remaining_time = self.settings.work_duration * 60
            self.state = TimerState.STOPPED
    
    def _reset_timer(self):
        """タイマーをリセット"""
        if self.is_work_session:
            self.remaining_time = self.settings.work_duration * 60
        else:
            self.remaining_time = self.settings.break_duration * 60
    
    def _play_start_sound(self):
        """開始音を再生"""
        if self.settings.sound_settings.start_sound:
            print("🔔 タイマー開始音")  # 実際の実装では音声ファイル再生
    
    def _play_end_sound(self):
        """終了音を再生"""
        if self.settings.sound_settings.end_sound:
            print("🔔 タイマー終了音")  # 実際の実装では音声ファイル再生
    
    def _play_tick_sound(self):
        """tick音を再生"""
        if self.settings.sound_settings.tick_sound:
            print("⏰", end="", flush=True)  # 実際の実装では音声ファイル再生
    
    def _notify_timer_start(self):
        """タイマー開始イベントを通知"""
        if self.on_timer_start:
            self.on_timer_start(self)
    
    def _notify_timer_end(self):
        """タイマー終了イベントを通知"""
        if self.on_timer_end:
            self.on_timer_end(self)
    
    def _notify_timer_tick(self):
        """タイマーtickイベントを通知"""
        if self.on_timer_tick:
            self.on_timer_tick(self)
    
    def _notify_break_start(self):
        """休憩開始イベントを通知"""
        if self.on_break_start:
            self.on_break_start(self)
    
    def _notify_settings_changed(self):
        """設定変更イベントを通知"""
        if self.on_settings_changed:
            self.on_settings_changed(self)