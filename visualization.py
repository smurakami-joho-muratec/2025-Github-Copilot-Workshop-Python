#!/usr/bin/env python3
"""
ゲーミフィケーション統計の可視化モジュール
ASCIIアートグラフとチャートを使用
"""

from gamification import GamificationManager
from datetime import datetime, timedelta
import math


def draw_progress_bar(current, maximum, width=30, char="█"):
    """プログレスバーを描画"""
    if maximum == 0:
        percentage = 0
    else:
        percentage = min(current / maximum, 1.0)
    
    filled = int(width * percentage)
    bar = char * filled + "░" * (width - filled)
    percentage_text = f"{percentage * 100:.1f}%"
    
    return f"[{bar}] {percentage_text} ({current}/{maximum})"


def draw_bar_chart(data, title, width=50, max_height=10):
    """横棒グラフを描画"""
    if not data:
        return [title, "データがありません"]
    
    max_value = max(data.values()) if data.values() else 1
    lines = [title, "=" * len(title)]
    
    for label, value in data.items():
        if max_value == 0:
            bar_length = 0
        else:
            bar_length = int((value / max_value) * width)
        
        bar = "█" * bar_length
        lines.append(f"{label:12} {bar} {value}")
    
    return lines


def draw_line_chart(data_points, title, width=60, height=10):
    """シンプルな線グラフを描画"""
    if not data_points:
        return [title, "データがありません"]
    
    lines = [title, "=" * len(title)]
    
    if len(data_points) < 2:
        lines.append("データ点が不足しています")
        return lines
    
    max_val = max(data_points)
    min_val = min(data_points)
    
    if max_val == min_val:
        max_val = min_val + 1
    
    # Y軸のスケール作成
    scale = height / (max_val - min_val) if max_val != min_val else 1
    
    # グラフの作成
    chart = []
    for y in range(height, -1, -1):
        line = f"{int(min_val + y/scale):4} |"
        
        for i, value in enumerate(data_points):
            if len(data_points) > 1:
                x_pos = int(i * width / (len(data_points) - 1))
            else:
                x_pos = width // 2
            
            normalized_y = int((value - min_val) * scale)
            
            if y == normalized_y:
                line += "●"
            elif y == 0:  # X軸
                line += "─"
            else:
                line += " "
        
        chart.append(line)
    
    # X軸ラベル
    x_axis = "     " + "─" * width
    chart.append(x_axis)
    
    lines.extend(chart)
    return lines


def generate_weekly_chart(weekly_stats):
    """週間統計のチャートを生成"""
    if not weekly_stats:
        return ["週間統計: データなし"]
    
    # 最新4週間のデータ
    weeks_data = {}
    for i, week in enumerate(weekly_stats[:4]):
        week_label = f"週{i+1}"
        weeks_data[week_label] = week.total_pomodoros
    
    return draw_bar_chart(weeks_data, "📊 週間ポモドーロ数推移")


def generate_daily_chart(daily_stats):
    """日別統計のチャートを生成"""
    if not daily_stats:
        return ["日別統計: データなし"]
    
    # 最新7日間のデータ
    today = datetime.now()
    daily_data = {}
    
    for i in range(7):
        date = (today - timedelta(days=6-i)).strftime("%m/%d")
        date_key = (today - timedelta(days=6-i)).strftime("%Y-%m-%d")
        
        if date_key in daily_stats:
            daily_data[date] = daily_stats[date_key].completed_pomodoros
        else:
            daily_data[date] = 0
    
    return draw_bar_chart(daily_data, "📅 過去7日間のポモドーロ数")


def generate_level_progress_chart(current_xp, level, xp_per_level):
    """レベル進行度チャート"""
    current_level_xp = (level - 1) * xp_per_level
    next_level_xp = level * xp_per_level
    progress_in_level = current_xp - current_level_xp
    xp_needed_for_level = next_level_xp - current_level_xp
    
    lines = [
        "🎯 レベル進行度",
        "=" * 20,
        f"現在のレベル: {level}",
        f"現在のXP: {current_xp}",
        "",
        "進行度:",
        draw_progress_bar(progress_in_level, xp_needed_for_level, 40),
        "",
        f"次のレベルまで: {next_level_xp - current_xp} XP"
    ]
    
    return lines


def generate_achievement_chart(unlocked, total):
    """達成バッジの進行度チャート"""
    lines = [
        "🏆 達成バッジ進行度",
        "=" * 25,
        draw_progress_bar(unlocked, total, 30),
        f"獲得済み: {unlocked}/{total} バッジ"
    ]
    
    return lines


def generate_streak_visualization(current_streak, best_streak):
    """ストリーク可視化"""
    lines = [
        "🔥 ストリーク統計",
        "=" * 20,
        f"現在のストリーク: {current_streak}日",
        f"最高記録: {best_streak}日",
        "",
        "ストリーク進行度:"
    ]
    
    # ストリークを視覚的に表現
    max_display = 30
    current_display = min(current_streak, max_display)
    
    streak_bar = "🔥" * current_display
    if current_streak > max_display:
        streak_bar += f"... (+{current_streak - max_display})"
    
    lines.append(streak_bar if streak_bar else "まだストリークがありません")
    
    return lines


def display_comprehensive_dashboard(gamification_manager):
    """包括的なダッシュボードを表示"""
    dashboard = gamification_manager.get_dashboard_data()
    
    print("🎮 ゲーミフィケーション ダッシュボード")
    print("=" * 60)
    
    # レベル進行度
    level_chart = generate_level_progress_chart(
        dashboard['xp'], 
        dashboard['level'], 
        gamification_manager.xp_per_level
    )
    for line in level_chart:
        print(line)
    print()
    
    # ストリーク可視化
    streak_chart = generate_streak_visualization(
        dashboard['current_streak'], 
        dashboard['best_streak']
    )
    for line in streak_chart:
        print(line)
    print()
    
    # 達成バッジ進行度
    achievement_chart = generate_achievement_chart(
        len(dashboard['unlocked_achievements']),
        len(dashboard['unlocked_achievements']) + len(dashboard['locked_achievements'])
    )
    for line in achievement_chart:
        print(line)
    print()
    
    # 週間統計チャート
    weekly_chart = generate_weekly_chart(dashboard['weekly_stats'])
    for line in weekly_chart:
        print(line)
    print()
    
    # 日別統計チャート
    daily_chart = generate_daily_chart(gamification_manager.daily_stats)
    for line in daily_chart:
        print(line)
    print()
    
    # 統計サマリー
    print("📊 統計サマリー")
    print("=" * 20)
    print(f"📈 総ポモドーロ数: {dashboard['total_pomodoros']}")
    print(f"📅 今週のポモドーロ: {dashboard['weekly_pomodoros']}")
    print(f"📆 今月のポモドーロ: {dashboard['monthly_pomodoros']}")
    
    if dashboard['weekly_stats']:
        current_week = dashboard['weekly_stats'][0]
        print(f"⏰ 今週の集中時間: {current_week.total_focus_time}分")
        print(f"📊 平均完了率: {current_week.average_completion_rate:.1f}%")
    
    print()
    
    # 達成バッジ詳細
    print("🏆 達成バッジ詳細")
    print("=" * 25)
    
    if dashboard['unlocked_achievements']:
        print("✅ 獲得済みバッジ:")
        for achievement in dashboard['unlocked_achievements']:
            print(f"  🏆 {achievement.name}")
            print(f"      {achievement.description}")
            if achievement.unlocked_date:
                print(f"      獲得日時: {achievement.unlocked_date}")
        print()
    
    if dashboard['locked_achievements']:
        print("🔒 未達成バッジ (次の目標):")
        for achievement in dashboard['locked_achievements'][:5]:
            print(f"  ⏳ {achievement.name}")
            print(f"      {achievement.description}")
        print()


def main():
    """デモンストレーション"""
    # ゲーミフィケーションマネージャーの初期化
    gm = GamificationManager("visualization_demo.json")
    
    # サンプルデータを作成（複数日にわたるポモドーロを模擬）
    print("📊 ゲーミフィケーション可視化デモ")
    print("サンプルデータを生成中...")
    
    # 15個のポモドーロを完了してサンプルデータを作成
    for i in range(15):
        gm.complete_pomodoro(25)
        if i % 5 == 4:
            print(f"  {i+1}個のポモドーロ完了...")
    
    print("データ生成完了!\n")
    
    # 包括的ダッシュボードを表示
    display_comprehensive_dashboard(gm)


if __name__ == "__main__":
    main()