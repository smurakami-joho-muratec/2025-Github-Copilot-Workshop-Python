#!/usr/bin/env python3
"""
シンプルなゲーミフィケーション機能デモ
直接的なポモドーロ完了シミュレーション
"""

from gamification import GamificationManager
import time


def main():
    """メインデモ"""
    print("🎮 ポモドーロ ゲーミフィケーション システム デモ")
    print("="*60)
    
    # ゲーミフィケーションマネージャーの初期化
    gm = GamificationManager("demo_gamification.json")
    
    # 初期状態表示
    print("📊 初期状態:")
    dashboard = gm.get_dashboard_data()
    print(f"  レベル: {dashboard['level']}")
    print(f"  XP: {dashboard['xp']}")
    print(f"  ストリーク: {dashboard['current_streak']}日")
    print(f"  総ポモドーロ数: {dashboard['total_pomodoros']}")
    
    print("\n🍅 ポモドーロセッション開始...")
    
    # ポモドーロセッション1: 5回完了
    print(f"\n=== セッション1: 基本的なポモドーロ完了 ===")
    for i in range(5):
        result = gm.complete_pomodoro(25)
        print(f"ポモドーロ {i+1}: +{result['xp_gained']} XP")
        if result['new_level']:
            print(f"  🎊 レベルアップ! レベル {result['current_level']} に到達!")
        print(f"  現在のXP: {result['current_xp']} (次レベルまで: {result['xp_to_next_level']})")
        print(f"  ストリーク: {result['current_streak']}日")
    
    # 現在の状態表示
    dashboard = gm.get_dashboard_data()
    print(f"\n📊 セッション1後の状態:")
    print(f"  レベル: {dashboard['level']}")
    print(f"  XP: {dashboard['xp']}")
    print(f"  総ポモドーロ数: {dashboard['total_pomodoros']}")
    
    # 達成バッジ表示
    print(f"\n🏆 達成バッジ:")
    for achievement in dashboard['unlocked_achievements']:
        print(f"  ✅ {achievement.name}: {achievement.description}")
    
    # ポモドーロセッション2: レベルアップを狙う
    print(f"\n=== セッション2: レベルアップを狙う ===")
    remaining_xp = dashboard['xp_to_next_level']
    needed_pomodoros = (remaining_xp + 9) // 10  # 切り上げ
    print(f"レベルアップまで {needed_pomodoros} 個のポモドーロが必要")
    
    for i in range(needed_pomodoros + 2):  # 少し余分に
        result = gm.complete_pomodoro(25)
        print(f"ポモドーロ {i+1}: +{result['xp_gained']} XP")
        if result['new_level']:
            print(f"  🎊 レベルアップ! レベル {result['current_level']} に到達!")
    
    # 最終状態表示
    dashboard = gm.get_dashboard_data()
    print(f"\n📊 最終状態:")
    print(f"  レベル: {dashboard['level']}")
    print(f"  XP: {dashboard['xp']}")
    print(f"  ストリーク: {dashboard['current_streak']}日 (最高: {dashboard['best_streak']}日)")
    print(f"  総ポモドーロ数: {dashboard['total_pomodoros']}")
    print(f"  今週のポモドーロ: {dashboard['weekly_pomodoros']}")
    print(f"  今月のポモドーロ: {dashboard['monthly_pomodoros']}")
    
    # すべての達成バッジ表示
    print(f"\n🏆 達成バッジ ({len(dashboard['unlocked_achievements'])}/{len(dashboard['unlocked_achievements']) + len(dashboard['locked_achievements'])}):")
    for achievement in dashboard['unlocked_achievements']:
        print(f"  ✅ {achievement.name}: {achievement.description}")
        print(f"      アンロック日時: {achievement.unlocked_date}")
    
    print(f"\n🔒 未達成バッジ:")
    for achievement in dashboard['locked_achievements'][:5]:  # 最初の5つ
        print(f"  ⏳ {achievement.name}: {achievement.description}")
    
    # 週間統計表示
    print(f"\n📊 週間統計:")
    weekly_stats = dashboard['weekly_stats']
    if weekly_stats:
        current_week = weekly_stats[0]
        print(f"  今週のポモドーロ数: {current_week.total_pomodoros}")
        print(f"  今週の集中時間: {current_week.total_focus_time}分")
        print(f"  平均完了率: {current_week.average_completion_rate:.1f}%")
    
    # 長期間のシミュレーション（週間10回達成を狙う）
    print(f"\n=== 追加セッション: 週間10回達成を狙う ===")
    current_weekly = dashboard['weekly_pomodoros']
    needed_for_weekly_10 = max(0, 10 - current_weekly)
    
    if needed_for_weekly_10 > 0:
        print(f"週間10回達成まで {needed_for_weekly_10} 個のポモドーロが必要")
        for i in range(needed_for_weekly_10):
            result = gm.complete_pomodoro(25)
            print(f"追加ポモドーロ {i+1}: +{result['xp_gained']} XP")
        
        # 週間10回バッジがアンロックされたかチェック
        final_dashboard = gm.get_dashboard_data()
        weekly_10_unlocked = any(a.id == 'weekly_10' for a in final_dashboard['unlocked_achievements'])
        if weekly_10_unlocked:
            print("  🏆 週間10回バッジを獲得!")
    
    print(f"\n🎉 デモ完了!")
    final_dashboard = gm.get_dashboard_data()
    print(f"最終レベル: {final_dashboard['level']}")
    print(f"最終XP: {final_dashboard['xp']}")
    print(f"最終ポモドーロ数: {final_dashboard['total_pomodoros']}")
    print(f"獲得バッジ数: {len(final_dashboard['unlocked_achievements'])}")


if __name__ == "__main__":
    main()