#!/usr/bin/env python3
"""
ポモドーロタイマー with ゲーミフィケーション機能
メインアプリケーション - 全機能デモ
"""

from deliverManager import *
from gamification import GamificationManager
from visualization import display_comprehensive_dashboard
import time


def main():
    """メインアプリケーション - ゲーミフィケーション機能の完全デモ"""
    print("🍅 ポモドーロタイマー with ゲーミフィケーション")
    print("=" * 60)
    print("🎮 全機能デモンストレーション")
    print("=" * 60)
    
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
    def on_recipe_success(sender, gamification_result):
        print(f"🎉 ポモドーロ完了! +{gamification_result['xp_gained']} XP")
        if gamification_result['new_level']:
            print(f"🎊 レベルアップ! レベル {gamification_result['current_level']} に到達!")
    
    def on_recipe_failed(sender, args):
        print("❌ レシピ配達失敗")
    
    delivery_manager.on_recipe_success.add_handler(on_recipe_success)
    delivery_manager.on_recipe_failed.add_handler(on_recipe_failed)
    
    print("\n📊 初期状態:")
    dashboard = delivery_manager.get_gamification_dashboard()
    print(f"レベル: {dashboard['level']}, XP: {dashboard['xp']}, ストリーク: {dashboard['current_streak']}日")
    
    print("\n🚀 ポモドーロセッション開始...")
    print("=" * 40)
    
    # 直接ゲーミフィケーションマネージャーを使って確実にポモドーロを完了
    print("🍅 12個のポモドーロセッションを実行中...")
    for i in range(12):
        result = delivery_manager.gamification.complete_pomodoro(25)
        print(f"ポモドーロ {i+1:2d}: 完了! +{result['xp_gained']} XP", end="")
        if result['new_level']:
            print(f" 🎊 レベルアップ! レベル {result['current_level']} に到達!")
        else:
            print()
        
        if (i + 1) % 4 == 0:
            print(f"--- {i+1}個完了 ---")
            current_dashboard = delivery_manager.get_gamification_dashboard()
            print(f"現在のレベル: {current_dashboard['level']}")
            print(f"現在のXP: {current_dashboard['xp']}")
            print(f"今週のポモドーロ: {current_dashboard['weekly_pomodoros']}")
            print()
    
    print("\n🎊 セッション完了!")
    
    # 最終的な統計とダッシュボードを表示
    print("\n" + "=" * 60)
    print("📊 最終ダッシュボード")
    print("=" * 60)
    
    # カスタムダッシュボード表示
    final_dashboard = delivery_manager.get_gamification_dashboard()
    
    print(f"🏆 最終結果:")
    print(f"  レベル: {final_dashboard['level']}")
    print(f"  XP: {final_dashboard['xp']}")
    print(f"  ストリーク: {final_dashboard['current_streak']}日 (最高: {final_dashboard['best_streak']}日)")
    print(f"  総ポモドーロ数: {final_dashboard['total_pomodoros']}")
    
    print(f"\n🏅 獲得済み達成バッジ ({len(final_dashboard['unlocked_achievements'])}個):")
    for achievement in final_dashboard['unlocked_achievements']:
        print(f"  ✅ {achievement.name}: {achievement.description}")
    
    print(f"\n⏳ 次の目標 (未達成バッジ):")
    for achievement in final_dashboard['locked_achievements'][:3]:
        print(f"  🔒 {achievement.name}: {achievement.description}")
    
    # 詳細な可視化ダッシュボードを表示
    print("\n" + "=" * 60)
    print("📈 詳細統計ダッシュボード")
    print("=" * 60)
    
    # GamificationManagerのインスタンスを直接取得
    gm = delivery_manager.gamification
    display_comprehensive_dashboard(gm)
    
    print("\n🎯 ゲーミフィケーション機能デモ完了!")
    print("=" * 40)
    print("実装された機能:")
    print("✅ 経験値(XP)システム - ポモドーロ完了でXP獲得")
    print("✅ レベルアップシステム - XP累積でレベル上昇")
    print("✅ 達成バッジシステム - 様々な条件で獲得")
    print("✅ ストリーク追跡 - 連続活動日数カウント")
    print("✅ 週間/月間統計 - 詳細な活動記録")
    print("✅ 可視化ダッシュボード - グラフとチャート")
    print("✅ データ永続化 - JSON形式で保存")


if __name__ == "__main__":
    main()