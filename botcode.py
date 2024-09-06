#import config required
from config import Config

# import libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import random


class MatiksBot:
    """
    A bot to automate playing the game on matiks.in.
    """
    def __init__(self):
        """
        Initializes the MatiksBot with the given URL.
        """
        chrome_options = Options()
        if Config.headless_browser:
            chrome_options.add_argument("--headless")  # Run in headless mode
        self.driver = webdriver.Chrome(service=Service(), options=chrome_options)
        self.driver.get(Config.url)
        self.segid = 5
        self.started = False

    def game_menu(self) -> None:
        """
        Navigates through the game menu to start the game.
        """
        buttons = ["Play Now", "Play as guest"]
        for button in buttons:
            self.wait_and_click(button)

    def wait_and_click(self, webtext: str) -> None:
        """
        Waits for an element containing the specified text to appear and clicks it.
        
        Args:
            webtext (str): The text to search for in the element.
        """
        try:
            WebDriverWait(self.driver, Config.pageload_waittime).until(
                EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{webtext}')]"))
            ).click()
        except Exception as e:
            print(f"Error clicking {webtext}: {e}")

    def power_nap(self) -> None:
        """
        Pauses execution for a random duration within the configured range.
        """
        time.sleep(random.uniform(*Config.botspeed_minmax))

    def findtext_and_click(self, webtext: str) -> None:
        """
        Finds an element containing the specified text and clicks it.
        
        Args:
            webtext (str): The text to search for in the element.
        """
        try:
            self.driver.find_element(By.XPATH, f"//*[contains(text(), '{webtext}')]").click()
        except Exception as e:
            print(f"Error finding and clicking {webtext}: {e}")

    def find_ans(self, content: str) -> str:
        """
        Extracts and evaluates the mathematical expression from the content.
        
        Args:
            content (str): The content containing the mathematical expression.
        
        Returns:
            str: The evaluated result of the expression.
        """
        clean = content.split('\n', self.segid)[-1].replace('\n', '')
        expression = clean.replace('÷', '/').replace('×', '*')
        return str(int(eval(expression)))

    def new_game(self) -> None:
        """
        Starts a new game by clicking the 'New Game' button.
        """
        self.findtext_and_click('New Game')

    def get_body(self) -> str:
        """
        Retrieves the text content of the body element.
        
        Returns:
            str: The text content of the body element.
        """
        return self.driver.find_element(By.XPATH, "/html/body").text

    def play(self) -> None:
        """
        Automates the gameplay by solving the mathematical expressions.
        """
        self.wait_and_click('Starting')

        while True:
            content = self.get_body()
            if not self.started and 'Starting' in content:
                print("detected start")
                self.power_nap()
            elif 'New Game' in content or 'solved' in content:
                break
            else:
                if not self.started:
                    inputfield = self.driver.find_element(By.XPATH, "//input[contains(@placeholder,'Please enter your answer here')]")
                self.started = True
                ans = self.find_ans(content)
                print(f"ans = {ans}")
                inputfield.send_keys(ans)
                self.power_nap()

    def close(self) -> None:
        """
        Closes the WebDriver.
        """
        self.driver.quit()