#!/usr/bin/env python3
"""
ポモドーロタイマー with ゲーミフィケーション機能
メインアプリケーション
"""

from deliverManager import *
from gamification import GamificationManager
import time


def display_gamification_stats(delivery_manager):
    """ゲーミフィケーション統計を表示"""
    print("\n" + "="*50)
    print("🎮 ゲーミフィケーション統計")
    print("="*50)
    
    dashboard = delivery_manager.get_gamification_dashboard()
    
    # 基本情報
    print(f"📊 レベル: {dashboard['level']}")
    print(f"⭐ XP: {dashboard['xp']} / {dashboard['xp'] + dashboard['xp_to_next_level']}")
    print(f"📈 次レベルまで: {dashboard['xp_to_next_level']} XP")
    print(f"🔥 現在のストリーク: {dashboard['current_streak']}日")
    print(f"🏆 最高ストリーク: {dashboard['best_streak']}日")
    
    # 統計情報
    print(f"\n📈 統計:")
    print(f"  総ポモドーロ数: {dashboard['total_pomodoros']}")
    print(f"  今週のポモドーロ: {dashboard['weekly_pomodoros']}")
    print(f"  今月のポモドーロ: {dashboard['monthly_pomodoros']}")
    
    # 達成バッジ
    print(f"\n🏆 達成バッジ ({len(dashboard['unlocked_achievements'])}/{len(dashboard['unlocked_achievements']) + len(dashboard['locked_achievements'])}):")
    for achievement in dashboard['unlocked_achievements']:
        print(f"  ✅ {achievement.name}: {achievement.description}")
    
    if dashboard['locked_achievements']:
        print(f"\n🔒 未達成バッジ (次の目標):")
        for achievement in dashboard['locked_achievements'][:3]:  # 最初の3つのみ表示
            print(f"  ⏳ {achievement.name}: {achievement.description}")


def simulate_pomodoro_session(delivery_manager, session_name, recipes_to_complete):
    """ポモドーロセッションをシミュレート"""
    print(f"\n🍅 {session_name} 開始!")
    print(f"目標: {recipes_to_complete}個のレシピ完了")
    
    # サンプル材料
    tomato = KitchenObjectSO("Tomato", 1)
    lettuce = KitchenObjectSO("Lettuce", 2)
    bread = KitchenObjectSO("Bread", 3)
    
    # レシピのパターン
    recipe_patterns = [
        ([bread, lettuce, tomato], "サンドイッチ"),  # 3つの材料
        ([lettuce, tomato], "サラダ"),               # 2つの材料
        ([bread], "トースト"),                       # 1つの材料
    ]
    
    completed = 0
    attempts = 0
    max_attempts = recipes_to_complete * 3  # 最大試行回数
    
    while completed < recipes_to_complete and attempts < max_attempts:
        attempts += 1
        
        # 待機中のレシピを確認
        waiting_recipes = delivery_manager.get_waiting_recipe_so_list()
        if not waiting_recipes:
            # レシピ生成のためにアップデート
            delivery_manager.update()
            time.sleep(0.1)
            continue
        
        # 最初の待機レシピを取得
        target_recipe = waiting_recipes[0]
        
        # そのレシピに合う皿を作成
        plate = PlateKitchenObject()
        for ingredient in target_recipe.kitchen_object_so_list:
            plate.add_kitchen_object(ingredient)
        
        # 配達を試行
        old_success_count = delivery_manager.get_successful_recipes_amount()
        delivery_manager.deliver_recipe(plate)
        new_success_count = delivery_manager.get_successful_recipes_amount()
        
        if new_success_count > old_success_count:
            completed += 1
            print(f"  ✅ {target_recipe.name} 完了! ({completed}/{recipes_to_complete})")
        
        # 短い間隔を置く
        time.sleep(0.1)
    
    print(f"セッション完了! {completed}/{recipes_to_complete} レシピを完了")
    return completed


def main():
    """メインアプリケーション"""
    print("🍅 ポモドーロタイマー with ゲーミフィケーション")
    print("="*60)
    
    # サンプルデータ作成
    tomato = KitchenObjectSO("Tomato", 1)
    lettuce = KitchenObjectSO("Lettuce", 2) 
    bread = KitchenObjectSO("Bread", 3)
    
    # サンプルレシピ
    sandwich_recipe = RecipeSO("Sandwich", [bread, lettuce, tomato])
    salad_recipe = RecipeSO("Salad", [lettuce, tomato])
    toast_recipe = RecipeSO("Toast", [bread])
    
    recipe_list = RecipeListSO([sandwich_recipe, salad_recipe, toast_recipe])
    
    # ゲームマネージャーとデリバリーマネージャーを初期化
    game_manager = KitchenGameManager.get_instance()
    game_manager.start_game()
    
    delivery_manager = DeliveryManager.get_instance(recipe_list)
    
    # イベントハンドラーの設定
    def on_recipe_spawned(sender, args):
        pass  # サイレント
    
    def on_recipe_success(sender, gamification_result):
        if gamification_result['new_level']:
            print(f"    🎊 レベルアップ! レベル {gamification_result['current_level']} に到達!")
        
        # 新しい達成バッジがあるかチェック（簡易版）
        dashboard = sender.get_gamification_dashboard()
        unlocked_today = [a for a in dashboard['unlocked_achievements'] 
                         if a.unlocked_date and a.unlocked_date.startswith("2025-09-22")]
        if unlocked_today:
            for achievement in unlocked_today[-1:]:  # 最新の1つだけ
                print(f"    🏆 新しいバッジ獲得: {achievement.name}")
    
    def on_recipe_failed(sender, args):
        pass  # サイレント
    
    delivery_manager.on_recipe_spawned.add_handler(on_recipe_spawned)
    delivery_manager.on_recipe_success.add_handler(on_recipe_success)
    delivery_manager.on_recipe_failed.add_handler(on_recipe_failed)
    
    # 初期状態表示
    display_gamification_stats(delivery_manager)
    
    # ポモドーロセッションのシミュレーション
    print("\n" + "="*60)
    print("🚀 ポモドーロセッション シミュレーション開始")
    print("="*60)
    
    # セッション1: 短いセッション
    simulate_pomodoro_session(delivery_manager, "朝の集中セッション", 3)
    display_gamification_stats(delivery_manager)
    
    # セッション2: 中程度のセッション  
    simulate_pomodoro_session(delivery_manager, "午後の作業セッション", 5)
    display_gamification_stats(delivery_manager)
    
    # セッション3: 長いセッション（レベルアップを狙う）
    simulate_pomodoro_session(delivery_manager, "夕方の集中セッション", 4)
    display_gamification_stats(delivery_manager)
    
    # 週間統計の表示
    print("\n" + "="*50)
    print("📊 週間統計")
    print("="*50)
    
    dashboard = delivery_manager.get_gamification_dashboard()
    weekly_stats = dashboard['weekly_stats']
    
    if weekly_stats:
        current_week = weekly_stats[0]
        print(f"今週のポモドーロ数: {current_week.total_pomodoros}")
        print(f"今週の集中時間: {current_week.total_focus_time}分")
        print(f"平均完了率: {current_week.average_completion_rate:.1f}%")
        
        print("\n日別の詳細:")
        for daily in current_week.daily_stats:
            if daily.completed_pomodoros > 0:
                print(f"  {daily.date}: {daily.completed_pomodoros}個のポモドーロ ({daily.focus_time_minutes}分)")
    
    print(f"\n🎉 セッション完了!")
    print(f"最終レベル: {delivery_manager.get_player_level()}")
    print(f"最終XP: {delivery_manager.get_player_xp()}")
    print(f"総ポモドーロ数: {delivery_manager.get_gamification_dashboard()['total_pomodoros']}")


if __name__ == "__main__":
    main()