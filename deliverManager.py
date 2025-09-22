import time
import random
from typing import List, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
from gamification import GamificationManager


class EventArgs:
    """イベント引数の基底クラス"""
    pass


class Event:
    """C#のeventに相当するクラス"""
    
    def __init__(self):
        self._handlers: List[Callable] = []
    
    def add_handler(self, handler: Callable):
        """イベントハンドラーを追加"""
        if handler not in self._handlers:
            self._handlers.append(handler)
    
    def remove_handler(self, handler: Callable):
        """イベントハンドラーを削除"""
        if handler in self._handlers:
            self._handlers.remove(handler)
    
    def invoke(self, sender, args: EventArgs = None):
        """イベントを発火"""
        for handler in self._handlers:
            handler(sender, args or EventArgs())


@dataclass
class KitchenObjectSO:
    """キッチンオブジェクトのデータクラス"""
    name: str
    object_id: int


@dataclass
class RecipeSO:
    """レシピのデータクラス"""
    name: str
    kitchen_object_so_list: List[KitchenObjectSO] = field(default_factory=list)


@dataclass
class RecipeListSO:
    """レシピリストのデータクラス"""
    recipe_so_list: List[RecipeSO] = field(default_factory=list)


class PlateKitchenObject:
    """皿のキッチンオブジェクト"""
    
    def __init__(self):
        self._kitchen_object_so_list: List[KitchenObjectSO] = []
    
    def add_kitchen_object(self, kitchen_object: KitchenObjectSO):
        """キッチンオブジェクトを追加"""
        self._kitchen_object_so_list.append(kitchen_object)
    
    def get_kitchen_object_so_list(self) -> List[KitchenObjectSO]:
        """キッチンオブジェクトリストを取得"""
        return self._kitchen_object_so_list.copy()


class KitchenGameManager:
    """キッチンゲームマネージャー（Singleton）"""
    
    _instance: Optional['KitchenGameManager'] = None
    
    def __init__(self):
        self._is_game_playing = False
    
    @classmethod
    def get_instance(cls) -> 'KitchenGameManager':
        """Singletonインスタンスを取得"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def is_game_playing(self) -> bool:
        """ゲームが進行中かどうか"""
        return self._is_game_playing
    
    def start_game(self):
        """ゲーム開始"""
        self._is_game_playing = True
    
    def stop_game(self):
        """ゲーム停止"""
        self._is_game_playing = False


class DeliveryManager:
    def get_recipe_by_name(self, user_input):
        query = f"SELECT * FROM recipes WHERE name = '{user_input}'"
        print(f"実行クエリ: {query}")
        return query
    
    """配達管理クラス（Python版）"""
    
    _instance: Optional['DeliveryManager'] = None
    
    def __init__(self, recipe_list_so: RecipeListSO):
        # イベント定義
        self.on_recipe_spawned = Event()
        self.on_recipe_completed = Event()
        self.on_recipe_success = Event()
        self.on_recipe_failed = Event()
        
        # プライベート変数
        self._recipe_list_so = recipe_list_so
        self._waiting_recipe_so_list: List[RecipeSO] = []
        self._spawn_recipe_timer = 0.0
        self._spawn_recipe_timer_max = 4.0
        self._waiting_recipes_max = 4
        self._successful_recipes_amount = 0
        self._last_update_time = time.time()
        
        # ゲーミフィケーション機能の初期化
        self.gamification = GamificationManager()
    
    @classmethod
    def get_instance(cls, recipe_list_so: RecipeListSO = None) -> 'DeliveryManager':
        """Singletonインスタンスを取得"""
        if cls._instance is None:
            if recipe_list_so is None:
                raise ValueError("初回作成時にはrecipe_list_soが必要です")
            cls._instance = cls(recipe_list_so)
        return cls._instance
    
    def update(self):
        """フレーム更新処理（UnityのUpdate相当）"""
        current_time = time.time()
        delta_time = current_time - self._last_update_time
        self._last_update_time = current_time
        
        self._spawn_recipe_timer -= delta_time
        
        if self._spawn_recipe_timer <= 0.0:
            self._spawn_recipe_timer = self._spawn_recipe_timer_max
            
            kitchen_game_manager = KitchenGameManager.get_instance()
            if (kitchen_game_manager.is_game_playing() and 
                len(self._waiting_recipe_so_list) < self._waiting_recipes_max):
                
                # ランダムにレシピを選択
                waiting_recipe_so = random.choice(self._recipe_list_so.recipe_so_list)
                self._waiting_recipe_so_list.append(waiting_recipe_so)
                
                # イベント発火
                self.on_recipe_spawned.invoke(self)
    
    def deliver_recipe(self, plate_kitchen_object: PlateKitchenObject):
        """レシピの材料と皿の材料が一致しているかどうかを確認する"""
        
        for i, waiting_recipe_so in enumerate(self._waiting_recipe_so_list):
            plate_ingredients = plate_kitchen_object.get_kitchen_object_so_list()
            
            # 材料数が一致するかチェック
            if len(waiting_recipe_so.kitchen_object_so_list) == len(plate_ingredients):
                plate_contents_matches_recipe = True
                
                # レシピの各材料をチェック
                for recipe_kitchen_object_so in waiting_recipe_so.kitchen_object_so_list:
                    ingredient_found = False
                    
                    # 皿の材料と照合
                    for plate_kitchen_object_so in plate_ingredients:
                        if plate_kitchen_object_so == recipe_kitchen_object_so:
                            ingredient_found = True
                            break
                    
                    if not ingredient_found:
                        plate_contents_matches_recipe = False
                        break
                
                # 材料が完全に一致した場合
                if plate_contents_matches_recipe:
                    self._successful_recipes_amount += 1
                    self._waiting_recipe_so_list.pop(i)
                    
                    # ゲーミフィケーション: ポモドーロ完了
                    gamification_result = self.gamification.complete_pomodoro(25)
                    
                    # 成功イベント発火
                    self.on_recipe_completed.invoke(self)
                    self.on_recipe_success.invoke(self, gamification_result)
                    return
        
        # 一致するレシピが見つからなかった場合
        self.on_recipe_failed.invoke(self)
    
    def get_waiting_recipe_so_list(self) -> List[RecipeSO]:
        """待機中のレシピリストを取得"""
        return self._waiting_recipe_so_list.copy()
    
    def get_successful_recipes_amount(self) -> int:
        """成功したレシピ数を取得"""
        return self._successful_recipes_amount
    
    def get_gamification_dashboard(self) -> dict:
        """ゲーミフィケーションダッシュボードデータを取得"""
        return self.gamification.get_dashboard_data()
    
    def get_player_level(self) -> int:
        """プレイヤーレベルを取得"""
        return self.gamification.level
    
    def get_player_xp(self) -> int:
        """プレイヤーXPを取得"""
        return self.gamification.xp
    
    def get_current_streak(self) -> int:
        """現在のストリークを取得"""
        return self.gamification.current_streak
    
    def get_achievements(self) -> dict:
        """達成バッジ情報を取得"""
        return {
            "unlocked": [a for a in self.gamification.achievements.values() if a.unlocked],
            "locked": [a for a in self.gamification.achievements.values() if not a.unlocked]
        }


# 使用例
if __name__ == "__main__":
    # サンプルデータ作成
    tomato = KitchenObjectSO("Tomato", 1)
    lettuce = KitchenObjectSO("Lettuce", 2)
    bread = KitchenObjectSO("Bread", 3)
    
    # サンプルレシピ
    sandwich_recipe = RecipeSO("Sandwich", [bread, lettuce, tomato])
    salad_recipe = RecipeSO("Salad", [lettuce, tomato])
    
    recipe_list = RecipeListSO([sandwich_recipe, salad_recipe])
    
    # ゲームマネージャーとデリバリーマネージャーを初期化
    game_manager = KitchenGameManager.get_instance()
    game_manager.start_game()
    
    delivery_manager = DeliveryManager.get_instance(recipe_list)
    
    # イベントハンドラーの設定
    def on_recipe_spawned(sender, args):
        print("新しいレシピが生成されました！")
    
    def on_recipe_success(sender, gamification_result):
        print("レシピ配達成功！")
        print(f"🎉 +{gamification_result['xp_gained']} XP獲得!")
        print(f"📊 レベル: {gamification_result['current_level']} (XP: {gamification_result['current_xp']})")
        print(f"🔥 ストリーク: {gamification_result['current_streak']}日")
        if gamification_result['new_level']:
            print(f"🎊 レベルアップ! レベル{gamification_result['current_level']}に到達!")
        print(f"📈 次レベルまであと{gamification_result['xp_to_next_level']} XP")
    
    def on_recipe_failed(sender, args):
        print("レシピ配達失敗...")
    
    delivery_manager.on_recipe_spawned.add_handler(on_recipe_spawned)
    delivery_manager.on_recipe_success.add_handler(on_recipe_success)
    delivery_manager.on_recipe_failed.add_handler(on_recipe_failed)
    
    # サンプル実行
    print("ゲーム開始...")
    
    # 5秒間更新処理を実行
    start_time = time.time()
    while time.time() - start_time < 5:
        delivery_manager.update()
        time.sleep(0.1)  # 100ms間隔で更新
    
    print(f"待機中のレシピ数: {len(delivery_manager.get_waiting_recipe_so_list())}")
    
    # サンプル配達テスト
    plate = PlateKitchenObject()
    plate.add_kitchen_object(bread)
    plate.add_kitchen_object(lettuce)
    plate.add_kitchen_object(tomato)
    
    print("サンドイッチを配達...")
    delivery_manager.deliver_recipe(plate)
    
    print(f"成功したレシピ数: {delivery_manager.get_successful_recipes_amount()}")
    
    # ゲーミフィケーション情報の表示
    print("\n=== ゲーミフィケーション情報 ===")
    dashboard = delivery_manager.get_gamification_dashboard()
    print(f"レベル: {dashboard['level']}")
    print(f"XP: {dashboard['xp']} (次レベルまで: {dashboard['xp_to_next_level']})")
    print(f"ストリーク: {dashboard['current_streak']}日 (最高記録: {dashboard['best_streak']}日)")
    print(f"総ポモドーロ数: {dashboard['total_pomodoros']}")
    print(f"今週のポモドーロ数: {dashboard['weekly_pomodoros']}")
    print(f"今月のポモドーロ数: {dashboard['monthly_pomodoros']}")
    
    print("\n=== 達成バッジ ===")
    achievements = delivery_manager.get_achievements()
    print("🏆 アンロック済み:")
    for achievement in achievements['unlocked']:
        print(f"  {achievement.name}: {achievement.description}")
    
    print("🔒 未達成:")
    for achievement in achievements['locked'][:5]:  # 最初の5つだけ表示
        print(f"  {achievement.name}: {achievement.description}")
    
    # 追加のポモドーロを実行してレベルアップをデモ
    print("\n=== 追加ポモドーロでレベルアップデモ ===")
    for i in range(7):  # 計10回でレベルアップ
        plate2 = PlateKitchenObject()
        plate2.add_kitchen_object(lettuce)
        plate2.add_kitchen_object(tomato)
        print(f"\nサラダ {i+1} を配達...")
        delivery_manager.deliver_recipe(plate2)
    
    print(f"\n最終的な成功したレシピ数: {delivery_manager.get_successful_recipes_amount()}")
    print(f"最終レベル: {delivery_manager.get_player_level()}")
    print(f"最終XP: {delivery_manager.get_player_xp()}")