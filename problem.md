# Problem
Students and people who enjoy trivia often want a simple way to test their general knowledge and challenge themselves. However, finding a quick trivia game that runs locally without requiring an account or internet connection can be inconvenient.

# Initial requirements
- R1: The game must run in the terminal on the user's computer with one command, and must not require an internet connection, API key, account, or paid service.
- R2: The game must display trivia questions with multiple-choice answers.
- R3: The player must be able to select an answer by typing its letter (A, B, C, or D).
- R4: The game must tell the player whether their answer is correct or incorrect.
- R5: The game must keep track of the player's score. (Changed in Round 4; see Round 4 requirements.)
- R6: The game must display the final score when all questions have been answered. (Changed in Round 4; see Round 4 requirements.)
- R7: The player must be able to play again without restarting the program.

# Round 2 requirements
- R8: The game must organize trivia questions into categories, such as Science, History, Sports, and Geography.
- R9: The player must be able to select a category before starting a game.
- R10: The game must only display questions belonging to the selected category.
- R11: The game must display the selected category during gameplay.
- R12: The game must handle categories that have no available questions by displaying a helpful message.

# Round 3 requirements
- R13: The game must offer three difficulty levels: Easy, Medium, and Hard.
- R14: The player must select a difficulty level after selecting a trivia category and before starting the game.
- R15: Each trivia question must have an assigned difficulty level.
- R16: The game must only display questions matching both the selected category and difficulty level.
- R17: The game must display the selected difficulty level during gameplay.
- R18: If the selected category has no questions at the chosen difficulty level, the game must display a helpful message and allow the player to choose another difficulty level or category without crashing.

# Round 4 requirements
- R5 (changed in Round 4): A correct answer must earn points based on the question's difficulty: Easy 1 point, Medium 3 points, Hard 5 points. Previously, every correct answer was worth 1 point.
- R6 (changed in Round 4): When all questions have been answered, the game must display the total points earned and the number of questions answered correctly, for example "Final score: 12 points (4 of 5 correct)." Previously, it displayed only the number of correct answers out of the number of questions.
