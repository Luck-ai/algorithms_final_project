from terminal import run_game
from graphicals import GameGUI
from validation import ask_choice, ask_yes_no, ask_int
import os

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    welcome = (
        "\n🐍 Welcome to SnakeSweeper — Snake meets Minesweeper!\n"
        "Collect food to grow and score points. Avoid bombs and obstacles.\n"
    )

    rules = (
        "\nRules:\n"
        " - Collect food (🍎) to gain +10 points and grow longer.\n"
        " - Avoid bombs (💣): touching one ends the game immediately.\n"
        " - Numbers shown near the head indicate adjacent bombs (including diagonals).\n"
        " - Game over if you hit a wall, your own body, or a bomb.\n"
        " - Enable trial mode to see bomb positions for practice.\n"
        " - Scores are saved to the leaderboard after each round.\n"
        " - Navigate using W/A/S/D or arrow keys, Q to quit and Z to undo.\n"
    )

    print(welcome)
    print(rules)

    mode_choice = ask_choice("Choose your game mode:\n1) CLI (text-based)\n2) GUI (graphical)\nEnter 1 or 2: ", choices=('1', '2'), default='1')

    trial = ask_yes_no("Start a practice (trial) round?", default=False)

    if mode_choice == '2':
        print("\nStarting GUI mode...")
        game = GameGUI(food_count=3, bomb_count=7, trial=trial)
        final_score = game.run()
        print(f"\nFinal score: {final_score}\n")

    else:
        if not trial:
            print("\nDifficulty settings — leave blank to use the default shown in [brackets].")
            food_count = ask_int("How many food items?", default=3, min_value=1, max_value=100)
            bomb_count = ask_int("How many bombs?", default=7, min_value=0, max_value=200)
        else:
            print("Practice mode: bombs will be visible during play.")
            food_count = 3
            bomb_count = 7
        
        print("\nStarting CLI mode...")
        run_game(food_count=food_count, bomb_count=bomb_count, trial=trial)
  
if __name__ == '__main__':
    main()