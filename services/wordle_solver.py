"""
Automated Wordle Solver
Solves the daily Wordle game on the NYT website automatically
"""

import time
import logging
from typing import Optional, List, Dict, Set, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from .word_lists import COMMON_ANSWERS, WORD_LIST

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress verbose Selenium logging
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)


class WordleSolver:
    """Solves Wordle automatically using Selenium"""
    
    def __init__(self, headless: bool = False, use_undetected: bool = True):
        """
        Initialize the Wordle solver
        
        Args:
            headless: Whether to run the browser in headless mode
            use_undetected: Whether to use undetected-chromedriver to avoid detection
        """
        self.headless = headless
        self.use_undetected = use_undetected
        self.driver = None
        self.guesses = []
        self.green_letters: Dict[int, str] = {}  # Position -> Letter (correct position)
        self.yellow_letters: Set[str] = set()    # Letters in word but wrong position
        self.gray_letters: Set[str] = set()      # Letters not in word
        self.eliminated_positions: Dict[str, Set[int]] = {}  # Letter -> positions where it's NOT
        
    def setup_driver(self):
        """Setup Selenium WebDriver"""
        try:
            if self.use_undetected:
                try:
                    import undetected_chromedriver as uc
                    options = uc.ChromeOptions()
                    if self.headless:
                        options.add_argument("--headless")
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                    self.driver = uc.Chrome(options=options)
                    logger.info("Using undetected-chromedriver")
                except ImportError:
                    logger.warning("undetected-chromedriver not installed, using regular Chrome")
                    self._setup_regular_chrome()
            else:
                self._setup_regular_chrome()
        except Exception as e:
            logger.error(f"Failed to setup driver: {e}")
            raise
    
    def _setup_regular_chrome(self):
        """Setup regular Chrome driver"""
        options = Options()
        if self.headless:
            options.add_argument("--headless=new") # Use new headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Check for environment variables (Cloud Run / Docker)
        import os
        chrome_bin = os.environ.get('CHROME_BIN')
        chromedriver_path = os.environ.get('CHROMEDRIVER')

        if chrome_bin:
            options.binary_location = chrome_bin

        try:
            if chromedriver_path and os.path.exists(chromedriver_path):
                logger.info(f"Using configured ChromeDriver at {chromedriver_path}")
                service = Service(executable_path=chromedriver_path)
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                # Try to use the local Chrome installation
                logger.info("Using ChromeDriverManager to install driver")
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            logger.warning(f"Failed with primary method: {e}")
            # Fallback: try to find Chrome in common locations
            import subprocess
            import os
            chrome_path = None
            try:
                chrome_path = subprocess.check_output(
                    ['which', 'chromium-browser'], stderr=subprocess.DEVNULL
                ).decode().strip()
            except:
                try:
                    chrome_path = subprocess.check_output(
                        ['which', 'google-chrome'], stderr=subprocess.DEVNULL
                    ).decode().strip()
                except:
                    # Try common locations
                    common_paths = [
                        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # Mac
                        r"C:\Program Files\Google\Chrome\Application\chrome.exe",  # Windows 64-bit
                        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",  # Windows 32-bit
                    ]
                    for path in common_paths:
                        if os.path.exists(path):
                            chrome_path = path
                            break
            
            if chrome_path:
                options.binary_location = chrome_path
                logger.info(f"Using Chrome at: {chrome_path}")
            else:
                logger.error("Chrome binary not found")
                raise Exception("Chrome not found")
            
            self.driver = webdriver.Chrome(options=options)
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
    
    def navigate_to_wordle(self):
        """Navigate to the Wordle website"""
        logger.info("Navigating to Wordle website...")
        self.driver.get("https://www.nytimes.com/games/wordle/")
        time.sleep(3)  # Wait for page to load
        
        # Dismiss cookie banner if present
        self.dismiss_cookie_banner()
        
        # Click play button if present
        self.click_play_button()
        
        # Try to dismiss any popups including rules
        self.dismiss_popups()
    
    def dismiss_cookie_banner(self):
        """Dismiss the NYT cookie banner if it appears"""
        try:
            logger.info("Checking for cookie banner...")
            # Common selectors for cookie banners
            selectors = [
                "button[data-testid='GDPR-accept']",
                "button[id='onetrust-accept-btn-handler']",
                "button.purr-blocker-card__button",
                "button[aria-label='Accept']",
                "button[aria-label='Agree']",
                "button:contains('Accept')",
                "button:contains('Continue')"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            logger.info(f"Found cookie banner button: {selector}")
                            element.click()
                            time.sleep(1)
                            return
                except:
                    pass
        except Exception as e:
            logger.warning(f"Error checking cookie banner: {e}")

    def click_play_button(self):
        """Click the play button to start the game"""
        try:
            logger.info("Looking for play button...")
            time.sleep(1)
            
            # Try various selectors for the play button
            play_selectors = [
                "button[aria-label='Play']",
                "button[aria-label='play']",
                "button[aria-label*='Play']",
                "button[aria-label*='play']",
                "button[class*='play']",
                "button[class*='Play']",
                "[data-testid='play-button']",
                "div[class*='Intro'] button",
                "div[class*='intro'] button",
                "button[type='button']",
            ]
            
            found_button = False
            for selector in play_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        try:
                            if button.is_displayed():
                                button_text = button.text.strip().lower()
                                button_aria = (button.get_attribute("aria-label") or "").lower()
                                
                                # Check if this looks like a play button
                                if "play" in button_text or "play" in button_aria or "intro" in button.get_attribute("class"):
                                    logger.info(f"Found play button: {button_text} | {button_aria}")
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                                    time.sleep(0.5)
                                    button.click()
                                    time.sleep(1)
                                    logger.info("Clicked play button")
                                    found_button = True
                                    break
                        except:
                            pass
                    if found_button:
                        break
                except:
                    pass
            
            if not found_button:
                logger.info("No play button found, game may already be active")
            
        except Exception as e:
            logger.warning(f"Could not find play button: {e}")
    
    def dismiss_popups(self):
        """Dismiss any popups that appear on the site"""
        try:
            # Wait for page to be interactive
            time.sleep(2)
            
            # Try to find and close the rules dialog or any other dialogs
            dialog_close_selectors = [
                "button[aria-label='Close']",
                "button[aria-label='close']",
                "button[aria-label='Close rules']",
                "button[aria-label='close rules']",
                "div[role='dialog'] button:last-child",
                "div[class*='Modal'] button[aria-label*='lose']",
                "div[class*='Modal'] button[aria-label*='ose']",
                ".modal-close",
                "button.close-btn",
                "button[class*='close']",
                "button[class*='Close']",
            ]
            
            for selector in dialog_close_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        try:
                            if element.is_displayed():
                                logger.info(f"Closing dialog with selector: {selector}")
                                element.click()
                                time.sleep(1)
                        except:
                            pass
                except:
                    pass
            
            # Check for any remaining dialogs
            try:
                dialogs = self.driver.find_elements(By.CSS_SELECTOR, "[role='dialog']")
                if dialogs:
                    logger.info(f"Found {len(dialogs)} dialog(s)")
                    for dialog in dialogs:
                        try:
                            # Try to find close button within the dialog
                            close_btn = dialog.find_element(By.CSS_SELECTOR, "button[aria-label*='lose'], button[aria-label*='ose']")
                            close_btn.click()
                            time.sleep(0.5)
                            logger.info("Closed dialog via internal close button")
                        except:
                            pass
            except:
                pass
                
        except Exception as e:
            logger.warning(f"Could not dismiss popups: {e}")
    
    def filter_candidates(self, candidates: List[str]) -> List[str]:
        """
        Filter candidate words based on known constraints
        
        Args:
            candidates: List of potential words
            
        Returns:
            Filtered list of valid candidates
        """
        logger.debug(f"Filtering {len(candidates)} candidates")
        logger.debug(f"Green letters: {self.green_letters}")
        logger.debug(f"Yellow letters: {self.yellow_letters}")
        logger.debug(f"Gray letters: {self.gray_letters}")
        logger.debug(f"Eliminated positions: {self.eliminated_positions}")
        
        filtered = []
        
        for word in candidates:
            # Check if word contains any gray letters
            if any(letter in word for letter in self.gray_letters):
                continue
            
            # Check if all green letters are in correct positions
            valid = True
            for position, letter in self.green_letters.items():
                if word[position] != letter:
                    valid = False
                    break
            
            if not valid:
                continue
            
            # Check if all yellow letters are in the word (but not in known wrong positions)
            for letter in self.yellow_letters:
                if letter not in word:
                    valid = False
                    break
                
                # Check that yellow letter is not in positions where we know it's wrong
                if letter in self.eliminated_positions:
                    for pos in self.eliminated_positions[letter]:
                        if word[pos] == letter:
                            valid = False
                            break
            
            if valid:
                filtered.append(word)
        
        logger.debug(f"Filtered down to {len(filtered)} candidates")
        return filtered
    
    def select_best_guess(self, candidates: List[str]) -> str:
        """
        Select the best guess based on letter frequency
        
        Args:
            candidates: List of valid candidate words
            
        Returns:
            Best word to guess
        """
        if not candidates:
            logger.warning("No valid candidates, using default word")
            return "slate"
        
        if len(candidates) == 1:
            return candidates[0]
        
        # If we have 10 or fewer candidates left, just guess one of them
        if len(candidates) <= 10:
            return candidates[0]
        
        # Score words by letter frequency
        letter_freq = {}
        for word in candidates:
            for letter in set(word):  # Use set to count unique letters
                letter_freq[letter] = letter_freq.get(letter, 0) + 1
        
        best_word = None
        best_score = -1
        
        for word in candidates:
            # Calculate score based on letter frequency and uniqueness
            score = sum(letter_freq.get(letter, 0) for letter in set(word))
            if score > best_score:
                best_score = score
                best_word = word
        
        return best_word or candidates[0]
    
    def make_guess(self, word: str) -> bool:
        """
        Type a word guess into Wordle
        
        Args:
            word: The word to guess
            
        Returns:
            True if guess was successful, False otherwise
        """
        logger.info(f"Making guess: {word}")
        
        try:
            # Wait a bit for the game to be ready
            time.sleep(0.5)
            
            # Type each letter
            for letter in word.lower():
                self.driver.find_element(By.TAG_NAME, "body").send_keys(letter)
                time.sleep(0.1)  # Small delay between key presses
            
            # Press Enter to submit
            time.sleep(0.2)
            self.driver.find_element(By.TAG_NAME, "body").send_keys('\n')
            
            # Wait for the guess to be processed
            time.sleep(2)
            
            self.guesses.append(word)
            return True
            
        except Exception as e:
            logger.error(f"Failed to make guess: {e}")
            return False
    
    def get_guess_feedback(self, guess_number: int = None) -> Optional[Dict[str, List[Tuple[str, str]]]]:
        """
        Get feedback from a specific guess row
        
        Args:
            guess_number: The row number to check (1-indexed). If None, uses the last guess.
            
        Returns:
            Dictionary with feedback or None if unable to get it
            Format: {'tiles': [('letter', 'correct'|'present'|'absent'), ...]}
        """
        try:
            # Wait for tiles to update and animate (increased for Cloud Run)
            time.sleep(5.5)
            
            # Get all rows
            rows = self.driver.find_elements(By.CSS_SELECTOR, "div[role='group'][aria-label*='Row']")
            
            if not rows:
                logger.warning("Could not find any rows. Page source snippet:")
                logger.warning(self.driver.page_source[:1000])
                return None
            
            logger.info(f"Found {len(rows)} rows total")
            
            # Find the row we need to check
            target_row = None
            if guess_number:
                # Look for "Row X" where X = guess_number
                for row in rows:
                    row_label = row.get_attribute("aria-label") or ""
                    if f"Row {guess_number}" in row_label:
                        target_row = row
                        logger.info(f"Found target row: {row_label}")
                        break
            else:
                # If no guess number specified, find the first row with completed feedback
                for row in rows:
                    tiles_with_state = row.find_elements(By.CSS_SELECTOR, "[data-testid='tile'][data-state]")
                    # Filter out empty/tbd states
                    valid_tiles = [t for t in tiles_with_state if t.get_attribute("data-state") not in ['empty', 'tbd']]
                    if len(valid_tiles) == 5:
                        target_row = row
            
            if not target_row:
                logger.warning(f"Could not find row {guess_number if guess_number else 'with feedback'}")
                return None
            
            # Get the 5 tiles from this row
            tiles = target_row.find_elements(By.CSS_SELECTOR, "[data-testid='tile']")
            
            if len(tiles) != 5:
                logger.warning(f"Expected 5 tiles in row, got {len(tiles)}")
                return None
            
            feedback = []
            for position, tile in enumerate(tiles):
                try:
                    # Get the state attribute (correct, present, absent)
                    state = tile.get_attribute("data-state")
                    
                    # Wait for state to populate if it's empty/tbd
                    if not state or state in ['empty', 'tbd']:
                        logger.info(f"Tile {position} state is '{state}', waiting...")
                        time.sleep(1)
                        state = tile.get_attribute("data-state")
                    
                    # Get the letter from text content
                    letter = tile.text.strip().lower()
                    
                    if letter and state and state not in ['empty', 'tbd']:
                        feedback.append((letter, state))
                        logger.info(f"Letter '{letter}': {state}")
                    else:
                        logger.warning(f"Could not get valid letter/state from tile {position}: letter='{letter}', state='{state}'")
                except Exception as tile_error:
                    logger.warning(f"Failed to process tile: {tile_error}")
                    pass
            
            if len(feedback) == 5:
                return {'tiles': feedback}
            else:
                logger.warning(f"Got {len(feedback)} tiles with feedback, expected 5")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get feedback: {e}")
            return None
            return None
    
    def process_feedback(self, word: str, feedback: Dict) -> bool:
        """
        Process the feedback and update constraints
        
        Args:
            word: The word that was guessed
            feedback: The feedback from the guess
            
        Returns:
            True if all letters are correct (green), False otherwise
        """
        tiles = feedback.get('tiles', [])
        
        if len(tiles) != 5:
            logger.warning(f"Invalid feedback, expected 5 tiles, got {len(tiles)}")
            return False
        
        all_correct = True
        
        for position, (letter, state) in enumerate(tiles):
            if state == "correct":
                self.green_letters[position] = letter
                logger.info(f"Position {position}: {letter} is CORRECT")
            elif state == "present":
                self.yellow_letters.add(letter)
                if letter not in self.eliminated_positions:
                    self.eliminated_positions[letter] = set()
                self.eliminated_positions[letter].add(position)
                logger.info(f"Letter {letter} is in word but not at position {position}")
                all_correct = False
            elif state == "absent":
                self.gray_letters.add(letter)
                logger.info(f"Letter {letter} is not in word")
                all_correct = False
        
        return all_correct
    
    def capture_share_results(self) -> Optional[str]:
        """
        Capture the game board and convert it to Wordle share format
        
        Returns:
            The share text in Wordle format, or None if unable to get it
        """
        try:
            import json
            from datetime import datetime
            
            # Extract the game board from the tiles (no need to wait for popups)
            share_text = self._extract_game_board_emoji()
            
            if share_text:
                # Save to JSON file with metadata
                try:
                    results_data = {
                        "timestamp": datetime.now().isoformat(),
                        "guesses": self.guesses,
                        "num_guesses": len(self.guesses),
                        "share_text": share_text,
                        "result": "SUCCESS"
                    }

                    # Also save as text
                    with open('wordle_results.txt', 'w', encoding='utf-8') as f:
                        f.write(share_text)
                    
                    logger.info("Results saved to wordle_results.txt")
                    logger.info(f"Results:\n{share_text}")
                except Exception as e:
                    logger.warning(f"Could not save results: {e}")
                
                return share_text
            else:
                logger.warning("Could not capture game board")
                return None
                
        except Exception as e:
            logger.error(f"Error capturing share results: {e}")
            return None
    
    def _extract_game_board_emoji(self) -> Optional[str]:
        """
        Extract the game board tiles and convert them to emoji format
        
        Returns:
            String in Wordle share format with header and emoji grid
        """
        try:
            # Get all tiles from all rows
            all_rows = self.driver.find_elements(By.CSS_SELECTOR, "div[role='group'][aria-label*='Row']")
            
            if not all_rows:
                logger.warning("Could not find any rows")
                return None
            
            emoji_rows = []
            
            # Process each row (only process rows with actual guesses)
            for row_idx, row in enumerate(all_rows):
                # Get all tiles in this row (with or without state)
                all_tiles = row.find_elements(By.CSS_SELECTOR, "[data-testid='tile']")
                
                if len(all_tiles) != 5:
                    continue
                
                # Check if this row has actual content (at least one tile with a letter)
                has_content = False
                row_emoji = ""
                
                for tile in all_tiles:
                    letter = tile.text.strip()
                    state = tile.get_attribute("data-state")
                    
                    # If tile has a letter, it's a real guess
                    if letter:
                        has_content = True
                    
                    # Only convert to emoji if it has a state (completed guess)
                    if state:
                        if state == "correct":
                            row_emoji += "🟩"
                        elif state == "present":
                            row_emoji += "🟨"
                        elif state == "absent":
                            row_emoji += "⬜"
                        else:
                            row_emoji += "⬛"
                    else:
                        # Empty tile, not part of a guess
                        has_content = False
                        break
                
                # Only add rows that have actual guesses (all 5 tiles filled and have state)
                if has_content and len(row_emoji) == 5:
                    emoji_rows.append(row_emoji)
                    logger.debug(f"Row {row_idx + 1}: {row_emoji}")
            
            if not emoji_rows:
                logger.warning("No completed rows found")
                return None
            
            # Create the share format
            # Format: Wordle {puzzle_number} {num_guesses}/6
            # Then the emoji grid
            num_guesses = len(emoji_rows)
            
            # Try to extract puzzle number from page (usually in the header or URL)
            puzzle_number = self._get_puzzle_number()
            
            share_text = f"Wordle {puzzle_number} {num_guesses}/6\n\n"
            share_text += "\n".join(emoji_rows)
            
            logger.info(f"Extracted game board with {num_guesses} guesses")
            return share_text
            
        except Exception as e:
            logger.error(f"Error extracting game board: {e}")
            return None
    
    def _get_puzzle_number(self) -> str:
        """
        Calculate the puzzle number based on the date
        
        Returns:
            Puzzle number as string
        """
        from datetime import date
        start_date = date(2021, 6, 20)
        today = date.today()
        puzzle_number = (today - start_date).days + 1
        return f"{puzzle_number:,}"
    
    def check_win_state(self) -> bool:
        """
        Check if the game is won
        
        Returns:
            True if the game is won, False otherwise
        """
        try:
            # Look for a success dialog or message
            success_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "[role='dialog'], .win-container, [class*='success'], [class*='completed']"
            )
            
            for element in success_elements:
                text = element.text.lower()
                if "congratulations" in text or "you win" in text or "next wordle" in text:
                    return True
            
            # Alternative: Check if all 5 positions have green letters
            if len(self.green_letters) == 5:
                logger.info("All letters are green!")
                return True
                
        except Exception as e:
            logger.warning(f"Could not check win state: {e}")
        
        return False
    
    def solve(self, max_guesses: int = 6) -> bool:
        """
        Solve the Wordle puzzle
        
        Args:
            max_guesses: Maximum number of guesses allowed
            
        Returns:
            True if solved within max_guesses, False otherwise
        """
        try:
            self.setup_driver()
            self.navigate_to_wordle()
            
            # Start with a good initial word (high letter frequency)
            candidates = COMMON_ANSWERS.copy()
            
            for guess_num in range(1, max_guesses + 1):
                logger.info(f"Guess {guess_num}/{max_guesses}")
                
                # Select the best word to guess
                best_word = self.select_best_guess(candidates)
                
                # Make the guess
                if not self.make_guess(best_word):
                    logger.error("Failed to make guess")
                    return False
                
                # Get feedback from the correct row (using guess_num)
                feedback = self.get_guess_feedback(guess_number=guess_num)
                if not feedback:
                    logger.error("Could not get feedback")
                    return False
                
                # Process feedback
                all_correct = self.process_feedback(best_word, feedback)
                
                if all_correct:
                    logger.info(f"✓ SOLVED in {guess_num} guesses: {best_word}")
                    # Capture and save the share results
                    self.capture_share_results()
                    return True
                
                # Check win state anyway (sometimes feedback might be misleading)
                if self.check_win_state():
                    logger.info(f"✓ SOLVED in {guess_num} guesses (detected by win state)")
                    # Capture and save the share results
                    self.capture_share_results()
                    return True
                
                # Update candidates for next guess
                candidates = self.filter_candidates(candidates)
                logger.info(f"Remaining candidates: {len(candidates)}")
                
                if not candidates:
                    logger.error("No valid candidates remaining")
                    return False
                
                if len(candidates) <= 3:
                    logger.info(f"Remaining words: {candidates}")
            
            logger.error(f"Could not solve within {max_guesses} guesses")
            return False
            
        except Exception as e:
            logger.error(f"Error during solving: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            self.close()


def main():
    """Main entry point"""
    logger.info("Starting Wordle Solver...")
    
    # Create solver (set headless=True for automation, headless=False to watch)
    solver = WordleSolver(headless=False, use_undetected=False)
    
    success = solver.solve()
    
    if success:
        logger.info("✓ Wordle solved successfully!")
        return 0
    else:
        logger.error("✗ Failed to solve Wordle")
        return 1


if __name__ == "__main__":
    exit(main())
