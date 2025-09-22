import tkinter as tk
import math
import time
import threading
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum


class TimerState(Enum):
    """タイマーの状態"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class TimerConfig:
    """タイマー設定"""
    work_duration: int = 25 * 60  # 25分（秒）
    break_duration: int = 5 * 60  # 5分（秒）
    long_break_duration: int = 15 * 60  # 15分（秒）
    sessions_until_long_break: int = 4


class PomodoroTimer:
    """Pomodoroタイマークラス"""
    
    def __init__(self, config: TimerConfig = None):
        self.config = config or TimerConfig()
        self.state = TimerState.IDLE
        self.current_session = 0
        self.total_sessions = 0
        self.remaining_time = self.config.work_duration
        self.start_time = 0
        self.pause_time = 0
        self.is_work_session = True
        
        # コールバック
        self.on_state_changed: Optional[Callable] = None
        self.on_time_updated: Optional[Callable] = None
        self.on_session_completed: Optional[Callable] = None
    
    def start(self):
        """タイマー開始"""
        if self.state == TimerState.IDLE:
            self.start_time = time.time()
            self.state = TimerState.RUNNING
        elif self.state == TimerState.PAUSED:
            # 一時停止からの再開
            pause_duration = time.time() - self.pause_time
            self.start_time += pause_duration
            self.state = TimerState.RUNNING
        
        if self.on_state_changed:
            self.on_state_changed(self.state)
    
    def pause(self):
        """タイマー一時停止"""
        if self.state == TimerState.RUNNING:
            self.pause_time = time.time()
            self.state = TimerState.PAUSED
            if self.on_state_changed:
                self.on_state_changed(self.state)
    
    def stop(self):
        """タイマー停止"""
        self.state = TimerState.IDLE
        self.remaining_time = self.config.work_duration
        self.current_session = 0
        self.is_work_session = True
        if self.on_state_changed:
            self.on_state_changed(self.state)
    
    def update(self):
        """タイマー更新（メインループから呼び出し）"""
        if self.state != TimerState.RUNNING:
            return
        
        current_time = time.time()
        elapsed = current_time - self.start_time
        session_duration = self.get_current_session_duration()
        
        self.remaining_time = max(0, session_duration - elapsed)
        
        if self.on_time_updated:
            self.on_time_updated(self.remaining_time, session_duration)
        
        # セッション完了チェック
        if self.remaining_time <= 0:
            self.complete_session()
    
    def complete_session(self):
        """セッション完了処理"""
        self.state = TimerState.COMPLETED
        self.current_session += 1
        
        if self.is_work_session:
            self.total_sessions += 1
        
        if self.on_session_completed:
            self.on_session_completed(self.is_work_session, self.current_session)
        
        # 次のセッションの準備
        self.prepare_next_session()
    
    def prepare_next_session(self):
        """次のセッションの準備"""
        if self.is_work_session:
            # 作業セッション完了 -> 休憩セッション
            self.is_work_session = False
            if self.total_sessions % self.config.sessions_until_long_break == 0:
                self.remaining_time = self.config.long_break_duration
            else:
                self.remaining_time = self.config.break_duration
        else:
            # 休憩セッション完了 -> 作業セッション
            self.is_work_session = True
            self.remaining_time = self.config.work_duration
        
        self.state = TimerState.IDLE
    
    def get_current_session_duration(self) -> int:
        """現在のセッション期間を取得"""
        if self.is_work_session:
            return self.config.work_duration
        elif self.total_sessions % self.config.sessions_until_long_break == 0:
            return self.config.long_break_duration
        else:
            return self.config.break_duration
    
    def get_progress_ratio(self) -> float:
        """進捗率を取得（0.0 - 1.0）"""
        session_duration = self.get_current_session_duration()
        if session_duration == 0:
            return 0.0
        return 1.0 - (self.remaining_time / session_duration)
    
    def format_time(self, seconds: int) -> str:
        """時間をフォーマット（MM:SS）"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"


class VisualEffects:
    """視覚効果クラス"""
    
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.particles = []
        self.ripples = []
        self.animation_running = False
    
    def start_background_effects(self):
        """背景エフェクト開始"""
        self.animation_running = True
        self.animate_particles()
        self.animate_ripples()
    
    def stop_background_effects(self):
        """背景エフェクト停止"""
        self.animation_running = False
        self.clear_effects()
    
    def clear_effects(self):
        """エフェクトをクリア"""
        for particle in self.particles:
            self.canvas.delete(particle['id'])
        for ripple in self.ripples:
            self.canvas.delete(ripple['id'])
        self.particles.clear()
        self.ripples.clear()
    
    def animate_particles(self):
        """パーティクルアニメーション"""
        if not self.animation_running:
            return
        
        # 新しいパーティクルを追加
        if len(self.particles) < 20 and tk._default_root.tk.call('expr', 'rand()') < 0.3:
            self.create_particle()
        
        # パーティクルを更新
        particles_to_remove = []
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            
            # 透明度を更新
            alpha = particle['life'] / particle['max_life']
            color = f"#{int(100 + 155 * alpha):02x}{int(150 + 105 * alpha):02x}{int(255 * alpha):02x}"
            
            self.canvas.coords(particle['id'], 
                             particle['x'] - 2, particle['y'] - 2,
                             particle['x'] + 2, particle['y'] + 2)
            self.canvas.itemconfig(particle['id'], fill=color, outline=color)
            
            if particle['life'] <= 0:
                particles_to_remove.append(particle)
        
        # 寿命が尽きたパーティクルを削除
        for particle in particles_to_remove:
            self.canvas.delete(particle['id'])
            self.particles.remove(particle)
        
        # 次のフレーム
        if self.animation_running:
            self.canvas.after(50, self.animate_particles)
    
    def create_particle(self):
        """パーティクル作成"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        x = tk._default_root.tk.call('expr', f'rand() * {canvas_width}')
        y = tk._default_root.tk.call('expr', f'rand() * {canvas_height}')
        
        particle_id = self.canvas.create_oval(x-2, y-2, x+2, y+2, 
                                            fill="#64a0ff", outline="#64a0ff")
        
        particle = {
            'id': particle_id,
            'x': x,
            'y': y,
            'vx': (tk._default_root.tk.call('expr', 'rand()') - 0.5) * 2,
            'vy': (tk._default_root.tk.call('expr', 'rand()') - 0.5) * 2,
            'life': 100,
            'max_life': 100
        }
        
        self.particles.append(particle)
    
    def animate_ripples(self):
        """波紋アニメーション"""
        if not self.animation_running:
            return
        
        # 新しい波紋を追加
        if len(self.ripples) < 3 and tk._default_root.tk.call('expr', 'rand()') < 0.1:
            self.create_ripple()
        
        # 波紋を更新
        ripples_to_remove = []
        for ripple in self.ripples:
            ripple['radius'] += ripple['speed']
            ripple['life'] -= 1
            
            # 透明度を更新
            alpha = ripple['life'] / ripple['max_life']
            color = f"#{int(100 * alpha):02x}{int(150 * alpha):02x}{int(255 * alpha):02x}"
            
            self.canvas.coords(ripple['id'],
                             ripple['x'] - ripple['radius'], ripple['y'] - ripple['radius'],
                             ripple['x'] + ripple['radius'], ripple['y'] + ripple['radius'])
            self.canvas.itemconfig(ripple['id'], outline=color)
            
            if ripple['life'] <= 0:
                ripples_to_remove.append(ripple)
        
        # 寿命が尽きた波紋を削除
        for ripple in ripples_to_remove:
            self.canvas.delete(ripple['id'])
            self.ripples.remove(ripple)
        
        # 次のフレーム
        if self.animation_running:
            self.canvas.after(100, self.animate_ripples)
    
    def create_ripple(self):
        """波紋作成"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        x = tk._default_root.tk.call('expr', f'rand() * {canvas_width}')
        y = tk._default_root.tk.call('expr', f'rand() * {canvas_height}')
        
        ripple_id = self.canvas.create_oval(x-1, y-1, x+1, y+1,
                                          fill="", outline="#6495ed", width=2)
        
        ripple = {
            'id': ripple_id,
            'x': x,
            'y': y,
            'radius': 1,
            'speed': 2,
            'life': 50,
            'max_life': 50
        }
        
        self.ripples.append(ripple)