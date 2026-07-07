from shared_functions import perform_filtered_similarity_search
from chromadb.api import collection_configuration
from shared_functions import *

def main():
    try:
        print("🍽️  Advanced Interactive Food Recommendation System")
        print("=" * 50)
        print("Loading food database...")
        
        food_items = load_food_data('FoodDataset.json')
        print("Food dataset loaded_successfully!")
        
        collection = create_similarity_search_collection("interactive_food_search",{'description': "a collection for interactive food search"})
        populate_similarity_collection(collection=collection,food_items=food_items)
        
        # Start the interactive chatbot
        interactive_advanced_search(collection)
        
    except Exception as e:
        print(f"Error occured: {e}")

def interactive_advanced_search(collection):
    print("\n" + "="*50)
    print("🔧 ADVANCED SEARCH WITH FILTERS")
    print("="*50)
    print("Search Options:")
    print("  1. Basic similarity search")
    print("  2. Cuisine-filtered search")  
    print("  3. Calorie-filtered search")
    print("  4. Combined filters search")
    print("  5. Demonstration mode")
    print("  6. Help")
    print("  7. Exit")
    print("-" * 50)

    while True:
        try:
            choice = input("\n📋 Select option (1-7): ").strip()
            
            if choice == '1':
                perform_basic_search(collection)
            elif choice == '2':
                perform_cuisine_filtered_search(collection)
            elif choice == '3':
                perform_calorie_filtered_search(collection)
            elif choice == '4':
                perform_combined_filtered_search(collection)
            elif choice == '5':
                run_search_demonstrations(collection)
            elif choice == '6':
                show_advanced_help()
            elif choice == '7':
                print("👋 Exiting Advanced Search System. Goodbye!")
                break
            else:
                print("❌ Invalid option. Please select 1-7.")
        except KeyboardInterrupt:
            print("\n👋 System interrupted. Exiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("   Please try again.")
    
def perform_basic_search(collection):
    print("\n🔍 BASIC SIMILARITY SEARCH")
    print("-" * 30)

    query = input("enter search query: ").strip()
    if not query:
        print("Pls enter a search term!")
        return
    
    results = perform_similarity_search(collection,query,5)
    display_search_results(results)

def perform_cuisine_filtered_search(collection):
    print("\n🔍 CUISINE-FILTERED SEARCH")
    print("-" * 30)

    cuisines = ["Italian", "Thai", "Mexican", "Indian", "Japanese", "French", 
                "Mediterranean", "American", "Health Food", "Dessert"]
    print("Available cuisines:")
    for i, cuisine in enumerate(cuisines, 1):
        print(f"  {i}. {cuisine}")

    query = input("\nEnter search query: ").strip()
    cuisine_choice = input("Enter cuisine number (or cuisine name): ").strip()
    
    if not query:
        print("❌ Please enter a search term")
        return
    
    cuisine_filter = None
    if cuisine_choice.isdigit():
        idx = int(cuisine_choice)-1
        if 0 <= idx <= len(cuisines):
            cuisine_filter = cuisines[idx]
    else:
        cuisine_filter = cuisine_choice.strip()

    if not cuisine_filter:
        print("❌ Invalid cuisine selection")
        return

    results = perform_filtered_similarity_search(collection,query,cuisine_filter,n_results=3)
    
    display_search_results(results, f"Cuisine-Filtered Results ({cuisine_filter})")

def perform_calorie_filtered_search(collection):
    print("\n🔍 CALORIE FILTERED SEARCH")
    print("-" * 30)

    query = input("\nEnter search query: ").strip()
    max_calories_input = input("\nEnter max calories you would like: ")

    if not query:
        print("❌ Please enter a search term")
        return

    if max_calories_input.isdigit():
        max_calories = int(max_calories_input)

    print(f"\n🔍 Searching for '{query}'" + 
          (f" with max {max_calories} calories..." if max_calories else "..."))

    results = perform_filtered_similarity_search(collection,query,max_calories,n_results=3)

    display_search_results(results)

def perform_combined_filtered_search(collection):
    print("\n🎯 COMBINED FILTERS SEARCH")
    print("-" * 30)


   
    cuisines = ["Italian", "Thai", "Mexican", "Indian", "Japanese", "French", 
                "Mediterranean", "American", "Health Food", "Dessert"]
    print("Available cuisines:")
    for i, cuisine in enumerate(cuisines, 1):
        print(f"  {i}. {cuisine}")

    query = input("\nEnter search query: ").strip()
    cuisine_choice = input("Enter cuisine number (or cuisine name): ").strip()
    max_calories_input = input("\nEnter max calories you would like: ")

    if not query:
        print("❌ Please enter a search term")
        return

    if max_calories_input.isdigit():
        max_calories = int(max_calories_input)
    else:
        print("Please enter a number for calories or press enter to leave blank!")

    cuisine_filter = None
    if cuisine_choice.isdigit():
        idx = int(cuisine_choice)-1
        if 0 <= idx <= len(cuisines):
            cuisine_filter = cuisines[idx]
    else:
        cuisine_filter = cuisine_choice.strip()

    if not cuisine_filter:
        print("❌ Invalid cuisine selection")
        return

    results = perform_filtered_similarity_search(collection,query,cuisine_filter,max_calories,n_results=3)
    display_search_results(results)

def run_search_demonstrations(collection):
    print("\n📊 SEARCH DEMONSTRATIONS")
    print("=" * 40)
    
    demonstrations = [
        {
            "title": "Italian Cuisine Search",
            "query": "creamy pasta",
            "cuisine_filter": "Italian",
            "max_calories": None
        },
        {
            "title": "Low-Calorie Healthy Options",
            "query": "healthy meal",
            "cuisine_filter": None,
            "max_calories": 300
        },
        {
            "title": "Asian Light Dishes",
            "query": "light fresh meal",
            "cuisine_filter": "Japanese",
            "max_calories": 250
        }
    ]
    
    for i, demo in enumerate(demonstrations, 1):
        print(f"\n{i}. {demo['title']}")
        print(f"   Query: '{demo['query']}'")
        
        filters = []
        if demo['cuisine_filter']:
            filters.append(f"Cuisine: {demo['cuisine_filter']}")
        if demo['max_calories']:
            filters.append(f"Max Calories: {demo['max_calories']}")
        
        if filters:
            print(f"   Filters: {', '.join(filters)}")
        
        results = perform_filtered_similarity_search(
            collection,
            demo['query'],
            cuisine_filter=demo['cuisine_filter'],
            max_calories=demo['max_calories'],
            n_results=3
        )
        
        display_search_results(results, demo['title'], show_details=False)
        
        input("\n⏸️  Press Enter to continue to next demonstration...")

def display_search_results(results, title, show_details=True):
    print(f"\n📋 {title}")
    print("=" * 50)
    
    if not results:
        print("❌ No matching results found")
        print("💡 Try adjusting your search terms or filters")
        return
    
    for i, result in enumerate(results, 1):
        score_percentage = result['similarity_score'] * 100
        
        if show_details:
            print(f"\n{i}. 🍽️  {result['food_name']}")
            print(f"   📊 Similarity Score: {score_percentage:.1f}%")
            print(f"   🏷️  Cuisine: {result['cuisine_type']}")
            print(f"   🔥 Calories: {result['food_calories_per_serving']}")
            print(f"   📝 Description: {result['food_description']}")
        else:
            print(f"   {i}. {result['food_name']} ({score_percentage:.1f}% match)")
    
    print("=" * 50)

def show_advanced_help():
    """Display help information for advanced search"""
    print("\n📖 ADVANCED SEARCH HELP")
    print("=" * 40)
    print("Search Types:")
    print("  1. Basic Search - Standard similarity search")
    print("  2. Cuisine Filter - Search within specific cuisine types")
    print("  3. Calorie Filter - Search for foods under calorie limits")
    print("  4. Combined Filters - Use multiple filters together")
    print("  5. Demonstrations - See predefined search examples")
    print("\nTips:")
    print("  • Use descriptive terms: 'creamy', 'spicy', 'light'")
    print("  • Combine ingredients: 'chicken vegetables'")
    print("  • Try cuisine names: 'Italian', 'Thai', 'Mexican'")
    print("  • Filter by calories for dietary goals")

if __name__ == '__main__':
    main()



    
    

