import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import os


@dataclass
class Achievement:
    """達成バッジのデータクラス"""
    id: str
    name: str
    description: str
    unlocked: bool = False
    unlocked_date: Optional[str] = None


@dataclass
class DailyStats:
    """日別統計データ"""
    date: str
    completed_pomodoros: int = 0
    focus_time_minutes: int = 0
    completion_rate: float = 0.0


@dataclass
class WeeklyStats:
    """週別統計データ"""
    week_start: str
    total_pomodoros: int = 0
    total_focus_time: int = 0
    average_completion_rate: float = 0.0
    daily_stats: List[DailyStats] = field(default_factory=list)


@dataclass
class MonthlyStats:
    """月別統計データ"""
    month: str
    total_pomodoros: int = 0
    total_focus_time: int = 0
    average_completion_rate: float = 0.0
    weekly_stats: List[WeeklyStats] = field(default_factory=list)


class GamificationManager:
    """ゲーミフィケーション管理クラス"""
    
    def __init__(self, save_file: str = "gamification_data.json"):
        self.save_file = save_file
        
        # 基本データ
        self.xp = 0
        self.level = 1
        self.current_streak = 0
        self.best_streak = 0
        self.last_activity_date: Optional[str] = None
        
        # 統計データ
        self.daily_stats: Dict[str, DailyStats] = {}
        self.achievements: Dict[str, Achievement] = {}
        
        # XPとレベルの設定
        self.xp_per_pomodoro = 10
        self.xp_per_level = 100
        
        # 達成バッジの初期化
        self._initialize_achievements()
        
        # データ読み込み
        self.load_data()
    
    def _initialize_achievements(self):
        """達成バッジの初期化"""
        achievements_data = [
            ("first_pomodoro", "初回完了", "初めてのポモドーロを完了"),
            ("streak_3", "3日連続", "3日連続でポモドーロを完了"),
            ("streak_7", "1週間連続", "7日連続でポモドーロを完了"),
            ("streak_30", "1ヶ月連続", "30日連続でポモドーロを完了"),
            ("weekly_10", "週間10回", "1週間で10回のポモドーロを完了"),
            ("weekly_25", "週間25回", "1週間で25回のポモドーロを完了"),
            ("monthly_50", "月間50回", "1ヶ月で50回のポモドーロを完了"),
            ("monthly_100", "月間100回", "1ヶ月で100回のポモドーロを完了"),
            ("level_5", "レベル5到達", "レベル5に到達"),
            ("level_10", "レベル10到達", "レベル10に到達"),
            ("focus_master", "集中マスター", "1日で5時間以上の集中時間を達成"),
        ]
        
        for achievement_id, name, description in achievements_data:
            self.achievements[achievement_id] = Achievement(
                achievement_id, name, description
            )
    
    def complete_pomodoro(self, focus_time_minutes: int = 25):
        """ポモドーロ完了時の処理"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # XP獲得
        self.xp += self.xp_per_pomodoro
        
        # レベルアップチェック
        old_level = self.level
        self._check_level_up()
        
        # 日別統計更新
        if today not in self.daily_stats:
            self.daily_stats[today] = DailyStats(today)
        
        daily_stat = self.daily_stats[today]
        daily_stat.completed_pomodoros += 1
        daily_stat.focus_time_minutes += focus_time_minutes
        daily_stat.completion_rate = self._calculate_completion_rate(today)
        
        # ストリーク更新
        self._update_streak(today)
        
        # 達成バッジチェック
        self._check_achievements()
        
        # データ保存
        self.save_data()
        
        return {
            "xp_gained": self.xp_per_pomodoro,
            "new_level": self.level > old_level,
            "current_level": self.level,
            "current_xp": self.xp,
            "xp_to_next_level": self._xp_to_next_level(),
            "current_streak": self.current_streak,
            "new_achievements": self._get_newly_unlocked_achievements()
        }
    
    def _check_level_up(self):
        """レベルアップのチェック"""
        required_xp = self.level * self.xp_per_level
        while self.xp >= required_xp:
            self.level += 1
            required_xp = self.level * self.xp_per_level
    
    def _xp_to_next_level(self) -> int:
        """次のレベルまでに必要なXP"""
        required_xp = self.level * self.xp_per_level
        return required_xp - self.xp
    
    def _update_streak(self, today: str):
        """ストリークの更新"""
        if self.last_activity_date is None:
            # 初回
            self.current_streak = 1
            self.best_streak = 1
        else:
            last_date = datetime.strptime(self.last_activity_date, "%Y-%m-%d")
            current_date = datetime.strptime(today, "%Y-%m-%d")
            days_diff = (current_date - last_date).days
            
            if days_diff == 1:
                # 連続
                self.current_streak += 1
                self.best_streak = max(self.best_streak, self.current_streak)
            elif days_diff == 0:
                # 同日（ストリークは変更なし）
                pass
            else:
                # 連続が途切れた
                self.current_streak = 1
        
        self.last_activity_date = today
    
    def _calculate_completion_rate(self, date: str) -> float:
        """完了率の計算（シンプルに100%として扱う）"""
        # 実際のアプリケーションでは、予定されたポモドーロ数との比率で計算
        return 100.0
    
    def _check_achievements(self):
        """達成バッジのチェック"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 初回完了
        if not self.achievements["first_pomodoro"].unlocked:
            if self._get_total_pomodoros() >= 1:
                self._unlock_achievement("first_pomodoro")
        
        # ストリーク系
        if not self.achievements["streak_3"].unlocked and self.current_streak >= 3:
            self._unlock_achievement("streak_3")
        if not self.achievements["streak_7"].unlocked and self.current_streak >= 7:
            self._unlock_achievement("streak_7")
        if not self.achievements["streak_30"].unlocked and self.current_streak >= 30:
            self._unlock_achievement("streak_30")
        
        # レベル系
        if not self.achievements["level_5"].unlocked and self.level >= 5:
            self._unlock_achievement("level_5")
        if not self.achievements["level_10"].unlocked and self.level >= 10:
            self._unlock_achievement("level_10")
        
        # 週間・月間系
        weekly_count = self._get_weekly_pomodoro_count()
        if not self.achievements["weekly_10"].unlocked and weekly_count >= 10:
            self._unlock_achievement("weekly_10")
        if not self.achievements["weekly_25"].unlocked and weekly_count >= 25:
            self._unlock_achievement("weekly_25")
        
        monthly_count = self._get_monthly_pomodoro_count()
        if not self.achievements["monthly_50"].unlocked and monthly_count >= 50:
            self._unlock_achievement("monthly_50")
        if not self.achievements["monthly_100"].unlocked and monthly_count >= 100:
            self._unlock_achievement("monthly_100")
        
        # 集中マスター
        if not self.achievements["focus_master"].unlocked:
            if today in self.daily_stats and self.daily_stats[today].focus_time_minutes >= 300:
                self._unlock_achievement("focus_master")
    
    def _unlock_achievement(self, achievement_id: str):
        """達成バッジのアンロック"""
        if achievement_id in self.achievements:
            achievement = self.achievements[achievement_id]
            achievement.unlocked = True
            achievement.unlocked_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_newly_unlocked_achievements(self) -> List[Achievement]:
        """新しくアンロックされた達成バッジを取得"""
        # 実装の簡単化のため、ここでは空リストを返す
        # 実際のアプリケーションでは、前回チェック以降のアンロックを追跡
        return []
    
    def _get_total_pomodoros(self) -> int:
        """総ポモドーロ数を取得"""
        return sum(stat.completed_pomodoros for stat in self.daily_stats.values())
    
    def _get_weekly_pomodoro_count(self) -> int:
        """今週のポモドーロ数を取得"""
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_start_str = week_start.strftime("%Y-%m-%d")
        
        count = 0
        for i in range(7):
            date = (week_start + timedelta(days=i)).strftime("%Y-%m-%d")
            if date in self.daily_stats:
                count += self.daily_stats[date].completed_pomodoros
        return count
    
    def _get_monthly_pomodoro_count(self) -> int:
        """今月のポモドーロ数を取得"""
        today = datetime.now()
        month_start = today.replace(day=1).strftime("%Y-%m-%d")
        
        count = 0
        for date_str, stat in self.daily_stats.items():
            if date_str >= month_start:
                count += stat.completed_pomodoros
        return count
    
    def get_weekly_stats(self, weeks_back: int = 4) -> List[WeeklyStats]:
        """週間統計を取得"""
        stats = []
        today = datetime.now()
        
        for i in range(weeks_back):
            week_start = today - timedelta(days=today.weekday() + i * 7)
            week_start_str = week_start.strftime("%Y-%m-%d")
            
            weekly_stat = WeeklyStats(week_start_str)
            daily_stats_list = []
            
            for j in range(7):
                date = (week_start + timedelta(days=j)).strftime("%Y-%m-%d")
                if date in self.daily_stats:
                    daily_stat = self.daily_stats[date]
                    daily_stats_list.append(daily_stat)
                    weekly_stat.total_pomodoros += daily_stat.completed_pomodoros
                    weekly_stat.total_focus_time += daily_stat.focus_time_minutes
                else:
                    daily_stats_list.append(DailyStats(date))
            
            weekly_stat.daily_stats = daily_stats_list
            if len([d for d in daily_stats_list if d.completed_pomodoros > 0]) > 0:
                weekly_stat.average_completion_rate = sum(
                    d.completion_rate for d in daily_stats_list if d.completed_pomodoros > 0
                ) / len([d for d in daily_stats_list if d.completed_pomodoros > 0])
            
            stats.append(weekly_stat)
        
        return stats
    
    def get_monthly_stats(self, months_back: int = 6) -> List[MonthlyStats]:
        """月間統計を取得"""
        stats = []
        today = datetime.now()
        
        for i in range(months_back):
            if i == 0:
                month_start = today.replace(day=1)
            else:
                if today.month - i <= 0:
                    month_start = today.replace(year=today.year - 1, month=12 + (today.month - i), day=1)
                else:
                    month_start = today.replace(month=today.month - i, day=1)
            
            month_str = month_start.strftime("%Y-%m")
            monthly_stat = MonthlyStats(month_str)
            
            # その月の全ての日をチェック
            for date_str, stat in self.daily_stats.items():
                if date_str.startswith(month_str):
                    monthly_stat.total_pomodoros += stat.completed_pomodoros
                    monthly_stat.total_focus_time += stat.focus_time_minutes
            
            stats.append(monthly_stat)
        
        return stats
    
    def get_dashboard_data(self) -> Dict:
        """ダッシュボード用データを取得"""
        return {
            "level": self.level,
            "xp": self.xp,
            "xp_to_next_level": self._xp_to_next_level(),
            "current_streak": self.current_streak,
            "best_streak": self.best_streak,
            "total_pomodoros": self._get_total_pomodoros(),
            "weekly_pomodoros": self._get_weekly_pomodoro_count(),
            "monthly_pomodoros": self._get_monthly_pomodoro_count(),
            "unlocked_achievements": [a for a in self.achievements.values() if a.unlocked],
            "locked_achievements": [a for a in self.achievements.values() if not a.unlocked],
            "weekly_stats": self.get_weekly_stats(),
            "monthly_stats": self.get_monthly_stats()
        }
    
    def save_data(self):
        """データをファイルに保存"""
        data = {
            "xp": self.xp,
            "level": self.level,
            "current_streak": self.current_streak,
            "best_streak": self.best_streak,
            "last_activity_date": self.last_activity_date,
            "daily_stats": {k: asdict(v) for k, v in self.daily_stats.items()},
            "achievements": {k: asdict(v) for k, v in self.achievements.items()}
        }
        
        try:
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"データ保存エラー: {e}")
    
    def load_data(self):
        """ファイルからデータを読み込み"""
        if not os.path.exists(self.save_file):
            return
        
        try:
            with open(self.save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.xp = data.get("xp", 0)
            self.level = data.get("level", 1)
            self.current_streak = data.get("current_streak", 0)
            self.best_streak = data.get("best_streak", 0)
            self.last_activity_date = data.get("last_activity_date")
            
            # 日別統計の復元
            daily_stats_data = data.get("daily_stats", {})
            for date_str, stat_data in daily_stats_data.items():
                self.daily_stats[date_str] = DailyStats(**stat_data)
            
            # 達成バッジの復元
            achievements_data = data.get("achievements", {})
            for achievement_id, achievement_data in achievements_data.items():
                if achievement_id in self.achievements:
                    self.achievements[achievement_id] = Achievement(**achievement_data)
        
        except Exception as e:
            print(f"データ読み込みエラー: {e}")


# 使用例とテスト
if __name__ == "__main__":
    # ゲーミフィケーションマネージャーの初期化
    gamification = GamificationManager()
    
    print("=== ゲーミフィケーションシステム デモ ===")
    print(f"現在のレベル: {gamification.level}")
    print(f"現在のXP: {gamification.xp}")
    print(f"現在のストリーク: {gamification.current_streak}")
    print()
    
    # ポモドーロ完了のシミュレーション
    print("ポモドーロを3回完了...")
    for i in range(3):
        result = gamification.complete_pomodoro(25)
        print(f"ポモドーロ {i+1} 完了!")
        print(f"  獲得XP: {result['xp_gained']}")
        print(f"  レベル: {result['current_level']}")
        print(f"  次レベルまでのXP: {result['xp_to_next_level']}")
        print(f"  ストリーク: {result['current_streak']}")
        print()
    
    # ダッシュボードデータの表示
    dashboard = gamification.get_dashboard_data()
    print("=== ダッシュボード ===")
    print(f"レベル: {dashboard['level']}")
    print(f"XP: {dashboard['xp']}")
    print(f"ストリーク: {dashboard['current_streak']} (最高: {dashboard['best_streak']})")
    print(f"総ポモドーロ数: {dashboard['total_pomodoros']}")
    print(f"今週のポモドーロ数: {dashboard['weekly_pomodoros']}")
    print(f"今月のポモドーロ数: {dashboard['monthly_pomodoros']}")
    print()
    
    print("=== アンロック済み達成バッジ ===")
    for achievement in dashboard['unlocked_achievements']:
        print(f"🏆 {achievement.name}: {achievement.description}")
        print(f"   アンロック日時: {achievement.unlocked_date}")
    
    print()
    print("=== 未達成バッジ ===")
    for achievement in dashboard['locked_achievements']:
        print(f"🔒 {achievement.name}: {achievement.description}")