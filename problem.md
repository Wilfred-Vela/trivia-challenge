# Problem
Students and people who enjoy trivia often want a simple way to test their general knowledge and challenge themselves. However, finding a quick trivia game that runs locally without requiring an account or internet connection can be inconvenient.

# Initial requirements
- R1: The game must run in the terminal on the user's computer with one command, and must not require an internet connection, API key, account, or paid service.
- R2: The game must display trivia questions with multiple-choice answers.
- R3: The player must be able to select an answer by typing its letter (A, B, C, or D).
- R4: The game must tell the player whether their answer is correct or incorrect. (Changed in Round 6: a correct answer also shows the points earned; see R26.)
- R5: The game must keep track of the player's score. (Changed in Round 4; see Round 4 requirements.)
- R6: The game must display the final score when all questions have been answered. (Changed in Round 4; see Round 4 requirements.)
- R7: The player must be able to play again without restarting the program. (Changed in Round 5: the player enters a name and sees the high-score list before the play-again prompt; see R19 and R22.)

# Round 2 requirements
- R8: The game must organize trivia questions into categories, such as Science, History, Sports, and Geography. (Changed in Round 6: Literature added as a category; see R28.)
- R9: The player must be able to select a category before starting a game. (Changed in Round 5: the category menu also offers a High Scores option; see R23.)
- R10: The game must only display questions belonging to the selected category.
- R11: The game must display the selected category during gameplay.
- R12: The game must handle categories that have no available questions by displaying a helpful message.

# Round 3 requirements
- R13: The game must offer three difficulty levels: Easy, Medium, and Hard.
- R14: The player must select a difficulty level after selecting a trivia category and before starting the game. (Changed in Round 6: the difficulty menu shows each level's points; see R27.)
- R15: Each trivia question must have an assigned difficulty level.
- R16: The game must only display questions matching both the selected category and difficulty level.
- R17: The game must display the selected difficulty level during gameplay.
- R18: If the selected category has no questions at the chosen difficulty level, the game must display a helpful message and allow the player to choose another difficulty level or category without crashing.

# Round 4 requirements
- R5 (changed in Round 4): A correct answer must earn points based on the question's difficulty: Easy 1 point, Medium 3 points, Hard 5 points. Previously, every correct answer was worth 1 point.
- R6 (changed in Round 4): When all questions have been answered, the game must display the total points earned and the number of questions answered correctly, for example "Final score: 12 points (4 of 5 correct)." Previously, it displayed only the number of correct answers out of the number of questions.

# Round 5 requirements
- R19: After each completed game, the game must ask for the player's name and save a high-score entry containing the name, total points earned, category, and difficulty level to a file.
- R20: The high-score list must keep only the top 10 scores.
- R21: The high-score list must be displayed from highest to lowest score.
- R22: The high-score list must be shown automatically after each completed game.
- R23: The player must be able to view the high-score list from a High Scores option in the menu.
- R24: If the high-score file does not exist, the game must start with an empty high-score list and create the file when the first score is saved.
- R25: If the high-score file is corrupted or cannot be read, the game must start with an empty high-score list without crashing.

# Round 6 requirements
- R26: After a correct answer, the feedback must show how many points were earned, for example "Correct! +3 points".
- R27: The difficulty menu must show how many points each level is worth, for example "1) Easy (1 point)".
- R28: The bundled questions must include a Literature category, and literature questions such as "Who wrote Romeo and Juliet?" must be in Literature, not History.
