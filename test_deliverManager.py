"""
Unit tests for DeliveryManager and related classes
"""
import pytest
import time
from deliverManager import (
    EventArgs, Event, KitchenObjectSO, RecipeSO, RecipeListSO,
    PlateKitchenObject, KitchenGameManager, DeliveryManager
)


class TestEventArgs:
    """Test suite for EventArgs class"""
    
    def test_event_args_creation(self):
        """Test EventArgs can be instantiated"""
        args = EventArgs()
        assert isinstance(args, EventArgs)


class TestEvent:
    """Test suite for Event class"""
    
    def test_event_creation(self):
        """Test Event can be instantiated"""
        event = Event()
        assert event is not None
        assert len(event._handlers) == 0
    
    def test_add_handler(self):
        """Test adding event handler"""
        event = Event()
        handler_called = []
        
        def handler(sender, args):
            handler_called.append(True)
        
        event.add_handler(handler)
        assert len(event._handlers) == 1
        assert handler in event._handlers
    
    def test_add_handler_duplicate(self):
        """Test adding the same handler twice doesn't duplicate it"""
        event = Event()
        
        def handler(sender, args):
            pass
        
        event.add_handler(handler)
        event.add_handler(handler)
        assert len(event._handlers) == 1
    
    def test_remove_handler(self):
        """Test removing event handler"""
        event = Event()
        
        def handler(sender, args):
            pass
        
        event.add_handler(handler)
        event.remove_handler(handler)
        assert len(event._handlers) == 0
    
    def test_remove_nonexistent_handler(self):
        """Test removing a handler that was never added"""
        event = Event()
        
        def handler(sender, args):
            pass
        
        # Should not raise an error
        event.remove_handler(handler)
        assert len(event._handlers) == 0
    
    def test_invoke_no_handlers(self):
        """Test invoking event with no handlers"""
        event = Event()
        # Should not raise an error
        event.invoke(None)
    
    def test_invoke_with_handler(self):
        """Test invoking event calls handler"""
        event = Event()
        handler_data = []
        
        def handler(sender, args):
            handler_data.append((sender, args))
        
        event.add_handler(handler)
        sender_obj = "test_sender"
        event.invoke(sender_obj)
        
        assert len(handler_data) == 1
        assert handler_data[0][0] == sender_obj
        assert isinstance(handler_data[0][1], EventArgs)
    
    def test_invoke_multiple_handlers(self):
        """Test invoking event calls all handlers"""
        event = Event()
        call_order = []
        
        def handler1(sender, args):
            call_order.append(1)
        
        def handler2(sender, args):
            call_order.append(2)
        
        event.add_handler(handler1)
        event.add_handler(handler2)
        event.invoke(None)
        
        assert len(call_order) == 2
        assert 1 in call_order
        assert 2 in call_order


class TestKitchenObjectSO:
    """Test suite for KitchenObjectSO dataclass"""
    
    def test_creation(self):
        """Test KitchenObjectSO creation"""
        obj = KitchenObjectSO("Tomato", 1)
        assert obj.name == "Tomato"
        assert obj.object_id == 1
    
    def test_equality(self):
        """Test KitchenObjectSO equality"""
        obj1 = KitchenObjectSO("Tomato", 1)
        obj2 = KitchenObjectSO("Tomato", 1)
        assert obj1 == obj2
    
    def test_inequality(self):
        """Test KitchenObjectSO inequality"""
        obj1 = KitchenObjectSO("Tomato", 1)
        obj2 = KitchenObjectSO("Lettuce", 2)
        assert obj1 != obj2


class TestRecipeSO:
    """Test suite for RecipeSO dataclass"""
    
    def test_creation(self):
        """Test RecipeSO creation"""
        tomato = KitchenObjectSO("Tomato", 1)
        lettuce = KitchenObjectSO("Lettuce", 2)
        recipe = RecipeSO("Salad", [tomato, lettuce])
        
        assert recipe.name == "Salad"
        assert len(recipe.kitchen_object_so_list) == 2
        assert tomato in recipe.kitchen_object_so_list
        assert lettuce in recipe.kitchen_object_so_list
    
    def test_creation_empty(self):
        """Test RecipeSO creation with no ingredients"""
        recipe = RecipeSO("Empty Recipe")
        assert recipe.name == "Empty Recipe"
        assert len(recipe.kitchen_object_so_list) == 0


class TestRecipeListSO:
    """Test suite for RecipeListSO dataclass"""
    
    def test_creation(self):
        """Test RecipeListSO creation"""
        recipe1 = RecipeSO("Salad", [])
        recipe2 = RecipeSO("Sandwich", [])
        recipe_list = RecipeListSO([recipe1, recipe2])
        
        assert len(recipe_list.recipe_so_list) == 2
        assert recipe1 in recipe_list.recipe_so_list
        assert recipe2 in recipe_list.recipe_so_list
    
    def test_creation_empty(self):
        """Test RecipeListSO creation with no recipes"""
        recipe_list = RecipeListSO()
        assert len(recipe_list.recipe_so_list) == 0


class TestPlateKitchenObject:
    """Test suite for PlateKitchenObject class"""
    
    def test_creation(self):
        """Test PlateKitchenObject creation"""
        plate = PlateKitchenObject()
        assert len(plate.get_kitchen_object_so_list()) == 0
    
    def test_add_kitchen_object(self):
        """Test adding kitchen objects to plate"""
        plate = PlateKitchenObject()
        tomato = KitchenObjectSO("Tomato", 1)
        
        plate.add_kitchen_object(tomato)
        objects = plate.get_kitchen_object_so_list()
        
        assert len(objects) == 1
        assert tomato in objects
    
    def test_add_multiple_objects(self):
        """Test adding multiple kitchen objects"""
        plate = PlateKitchenObject()
        tomato = KitchenObjectSO("Tomato", 1)
        lettuce = KitchenObjectSO("Lettuce", 2)
        bread = KitchenObjectSO("Bread", 3)
        
        plate.add_kitchen_object(tomato)
        plate.add_kitchen_object(lettuce)
        plate.add_kitchen_object(bread)
        
        objects = plate.get_kitchen_object_so_list()
        assert len(objects) == 3
        assert tomato in objects
        assert lettuce in objects
        assert bread in objects
    
    def test_get_returns_copy(self):
        """Test that get_kitchen_object_so_list returns a copy"""
        plate = PlateKitchenObject()
        tomato = KitchenObjectSO("Tomato", 1)
        plate.add_kitchen_object(tomato)
        
        list1 = plate.get_kitchen_object_so_list()
        list2 = plate.get_kitchen_object_so_list()
        
        # Modifying one list shouldn't affect the other
        list1.append(KitchenObjectSO("Extra", 99))
        assert len(list2) == 1
        assert len(plate.get_kitchen_object_so_list()) == 1


class TestKitchenGameManager:
    """Test suite for KitchenGameManager singleton"""
    
    def setup_method(self):
        """Reset singleton instance before each test"""
        KitchenGameManager._instance = None
    
    def test_singleton_pattern(self):
        """Test that KitchenGameManager follows singleton pattern"""
        manager1 = KitchenGameManager.get_instance()
        manager2 = KitchenGameManager.get_instance()
        assert manager1 is manager2
    
    def test_initial_state(self):
        """Test initial game state is not playing"""
        manager = KitchenGameManager.get_instance()
        assert manager.is_game_playing() is False
    
    def test_start_game(self):
        """Test starting the game"""
        manager = KitchenGameManager.get_instance()
        manager.start_game()
        assert manager.is_game_playing() is True
    
    def test_stop_game(self):
        """Test stopping the game"""
        manager = KitchenGameManager.get_instance()
        manager.start_game()
        manager.stop_game()
        assert manager.is_game_playing() is False
    
    def test_start_stop_cycle(self):
        """Test multiple start/stop cycles"""
        manager = KitchenGameManager.get_instance()
        
        manager.start_game()
        assert manager.is_game_playing() is True
        
        manager.stop_game()
        assert manager.is_game_playing() is False
        
        manager.start_game()
        assert manager.is_game_playing() is True


class TestDeliveryManager:
    """Test suite for DeliveryManager class"""
    
    def setup_method(self):
        """Reset singleton instances before each test"""
        DeliveryManager._instance = None
        KitchenGameManager._instance = None
    
    def create_sample_recipes(self):
        """Helper to create sample recipes"""
        tomato = KitchenObjectSO("Tomato", 1)
        lettuce = KitchenObjectSO("Lettuce", 2)
        bread = KitchenObjectSO("Bread", 3)
        
        sandwich_recipe = RecipeSO("Sandwich", [bread, lettuce, tomato])
        salad_recipe = RecipeSO("Salad", [lettuce, tomato])
        
        return RecipeListSO([sandwich_recipe, salad_recipe])
    
    def test_singleton_pattern(self):
        """Test that DeliveryManager follows singleton pattern"""
        recipe_list = self.create_sample_recipes()
        manager1 = DeliveryManager.get_instance(recipe_list)
        manager2 = DeliveryManager.get_instance()
        assert manager1 is manager2
    
    def test_creation_requires_recipe_list(self):
        """Test that first creation requires recipe list"""
        with pytest.raises(ValueError):
            DeliveryManager.get_instance()
    
    def test_initial_state(self):
        """Test initial state of delivery manager"""
        recipe_list = self.create_sample_recipes()
        manager = DeliveryManager.get_instance(recipe_list)
        
        assert len(manager.get_waiting_recipe_so_list()) == 0
        assert manager.get_successful_recipes_amount() == 0
    
    def test_events_exist(self):
        """Test that all events are properly initialized"""
        recipe_list = self.create_sample_recipes()
        manager = DeliveryManager.get_instance(recipe_list)
        
        assert hasattr(manager, 'on_recipe_spawned')
        assert hasattr(manager, 'on_recipe_completed')
        assert hasattr(manager, 'on_recipe_success')
        assert hasattr(manager, 'on_recipe_failed')
        assert isinstance(manager.on_recipe_spawned, Event)
    
    def test_update_spawns_recipes(self):
        """Test that update spawns recipes when game is playing"""
        recipe_list = self.create_sample_recipes()
        manager = DeliveryManager.get_instance(recipe_list)
        game_manager = KitchenGameManager.get_instance()
        
        spawned_count = []
        
        def on_spawned(sender, args):
            spawned_count.append(1)
        
        manager.on_recipe_spawned.add_handler(on_spawned)
        game_manager.start_game()
        
        # Force timer to expire
        manager._spawn_recipe_timer = 0
        manager.update()
        
        assert len(spawned_count) > 0
        assert len(manager.get_waiting_recipe_so_list()) > 0
    
    def test_update_no_spawn_when_not_playing(self):
        """Test that recipes don't spawn when game is not playing"""
        recipe_list = self.create_sample_recipes()
        manager = DeliveryManager.get_instance(recipe_list)
        game_manager = KitchenGameManager.get_instance()
        
        # Ensure game is not playing
        game_manager.stop_game()
        
        # Force timer to expire
        manager._spawn_recipe_timer = 0
        manager.update()
        
        assert len(manager.get_waiting_recipe_so_list()) == 0
    
    def test_update_respects_max_recipes(self):
        """Test that update doesn't spawn more than max recipes"""
        recipe_list = self.create_sample_recipes()
        manager = DeliveryManager.get_instance(recipe_list)
        game_manager = KitchenGameManager.get_instance()
        game_manager.start_game()
        
        # Spawn max number of recipes
        for _ in range(manager._waiting_recipes_max):
            manager._spawn_recipe_timer = 0
            manager.update()
        
        initial_count = len(manager.get_waiting_recipe_so_list())
        
        # Try to spawn one more
        manager._spawn_recipe_timer = 0
        manager.update()
        
        # Should not exceed max
        assert len(manager.get_waiting_recipe_so_list()) == initial_count
        assert len(manager.get_waiting_recipe_so_list()) <= manager._waiting_recipes_max
    
    def test_deliver_recipe_success(self):
        """Test successful recipe delivery"""
        recipe_list = self.create_sample_recipes()
        manager = DeliveryManager.get_instance(recipe_list)
        
        # Create a sandwich
        tomato = KitchenObjectSO("Tomato", 1)
        lettuce = KitchenObjectSO("Lettuce", 2)
        bread = KitchenObjectSO("Bread", 3)
        
        # Add sandwich recipe to waiting list
        sandwich_recipe = RecipeSO("Sandwich", [bread, lettuce, tomato])
        manager._waiting_recipe_so_list.append(sandwich_recipe)
        
        # Create matching plate
        plate = PlateKitchenObject()
        plate.add_kitchen_object(bread)
        plate.add_kitchen_object(lettuce)
        plate.add_kitchen_object(tomato)
        
        success_called = []
        
        def on_success(sender, args):
            success_called.append(True)
        
        manager.on_recipe_success.add_handler(on_success)
        
        # Deliver the recipe
        manager.deliver_recipe(plate)
        
        assert len(success_called) == 1
        assert manager.get_successful_recipes_amount() == 1
        assert len(manager.get_waiting_recipe_so_list()) == 0
    
    def test_deliver_recipe_wrong_ingredients(self):
        """Test failed recipe delivery with wrong ingredients"""
        recipe_list = self.create_sample_recipes()
        manager = DeliveryManager.get_instance(recipe_list)
        
        # Add sandwich recipe to waiting list
        tomato = KitchenObjectSO("Tomato", 1)
        lettuce = KitchenObjectSO("Lettuce", 2)
        bread = KitchenObjectSO("Bread", 3)
        sandwich_recipe = RecipeSO("Sandwich", [bread, lettuce, tomato])
        manager._waiting_recipe_so_list.append(sandwich_recipe)
        
        # Create plate with wrong ingredients
        plate = PlateKitchenObject()
        plate.add_kitchen_object(bread)
        plate.add_kitchen_object(bread)  # Wrong!
        plate.add_kitchen_object(bread)  # Wrong!
        
        failed_called = []
        
        def on_failed(sender, args):
            failed_called.append(True)
        
        manager.on_recipe_failed.add_handler(on_failed)
        
        # Deliver the recipe
        manager.deliver_recipe(plate)
        
        assert len(failed_called) == 1
        assert manager.get_successful_recipes_amount() == 0
        assert len(manager.get_waiting_recipe_so_list()) == 1
    
    def test_deliver_recipe_wrong_count(self):
        """Test failed recipe delivery with wrong ingredient count"""
        recipe_list = self.create_sample_recipes()
        manager = DeliveryManager.get_instance(recipe_list)
        
        # Add sandwich recipe to waiting list
        tomato = KitchenObjectSO("Tomato", 1)
        lettuce = KitchenObjectSO("Lettuce", 2)
        bread = KitchenObjectSO("Bread", 3)
        sandwich_recipe = RecipeSO("Sandwich", [bread, lettuce, tomato])
        manager._waiting_recipe_so_list.append(sandwich_recipe)
        
        # Create plate with too few ingredients
        plate = PlateKitchenObject()
        plate.add_kitchen_object(bread)
        plate.add_kitchen_object(lettuce)
        
        failed_called = []
        
        def on_failed(sender, args):
            failed_called.append(True)
        
        manager.on_recipe_failed.add_handler(on_failed)
        
        # Deliver the recipe
        manager.deliver_recipe(plate)
        
        assert len(failed_called) == 1
        assert manager.get_successful_recipes_amount() == 0
    
    def test_deliver_recipe_order_independent(self):
        """Test that ingredient order doesn't matter"""
        recipe_list = self.create_sample_recipes()
        manager = DeliveryManager.get_instance(recipe_list)
        
        # Create ingredients
        tomato = KitchenObjectSO("Tomato", 1)
        lettuce = KitchenObjectSO("Lettuce", 2)
        bread = KitchenObjectSO("Bread", 3)
        
        # Recipe in one order
        sandwich_recipe = RecipeSO("Sandwich", [bread, lettuce, tomato])
        manager._waiting_recipe_so_list.append(sandwich_recipe)
        
        # Plate in different order
        plate = PlateKitchenObject()
        plate.add_kitchen_object(tomato)
        plate.add_kitchen_object(bread)
        plate.add_kitchen_object(lettuce)
        
        # Should still succeed
        manager.deliver_recipe(plate)
        assert manager.get_successful_recipes_amount() == 1
    
    def test_deliver_multiple_recipes(self):
        """Test delivering multiple recipes in sequence"""
        recipe_list = self.create_sample_recipes()
        manager = DeliveryManager.get_instance(recipe_list)
        
        tomato = KitchenObjectSO("Tomato", 1)
        lettuce = KitchenObjectSO("Lettuce", 2)
        
        # Add salad recipe
        salad_recipe = RecipeSO("Salad", [lettuce, tomato])
        manager._waiting_recipe_so_list.append(salad_recipe)
        manager._waiting_recipe_so_list.append(salad_recipe)
        
        # Deliver first salad
        plate1 = PlateKitchenObject()
        plate1.add_kitchen_object(lettuce)
        plate1.add_kitchen_object(tomato)
        manager.deliver_recipe(plate1)
        
        assert manager.get_successful_recipes_amount() == 1
        assert len(manager.get_waiting_recipe_so_list()) == 1
        
        # Deliver second salad
        plate2 = PlateKitchenObject()
        plate2.add_kitchen_object(lettuce)
        plate2.add_kitchen_object(tomato)
        manager.deliver_recipe(plate2)
        
        assert manager.get_successful_recipes_amount() == 2
        assert len(manager.get_waiting_recipe_so_list()) == 0
    
    def test_get_waiting_recipe_so_list_returns_copy(self):
        """Test that get_waiting_recipe_so_list returns a copy"""
        recipe_list = self.create_sample_recipes()
        manager = DeliveryManager.get_instance(recipe_list)
        
        list1 = manager.get_waiting_recipe_so_list()
        list2 = manager.get_waiting_recipe_so_list()
        
        # Modifying one list shouldn't affect the other
        list1.append(RecipeSO("Fake", []))
        assert len(list2) == 0
        assert len(manager.get_waiting_recipe_so_list()) == 0
