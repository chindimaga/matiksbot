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
import re


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
        self.segid = -1
        self.started = False
        # Define a regex pattern for a valid arithmetic expression without parentheses
        self.pattern = re.compile(r'^[\d+\-*/\s]+$')
        self.operators = ["+", "-", "×", "÷"]

    def reset(self):
        self.started = False
        self.segid = 1000

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

    def make_expression(self, content: str, checkid: int) ->str:
        """
        Processes the given content to extract and format a mathematical expression.

        Args:
            content (str): The content containing the mathematical expression.
            checkid (int): The index to split the content and extract the expression.

        Returns:
            str: The formatted mathematical expression with operators replaced.
        """
        clean = content.split('\n', checkid)[-1].replace('\n', '')
        return clean.replace('÷', '/').replace('×', '*')
    
    def is_valid_expression(self, expression: str) -> bool:
        """
        Validates if the given expression matches the predefined pattern for arithmetic expressions.

        Args:
            expression (str): The mathematical expression to validate.

        Returns:
            bool: True if the expression is valid, False otherwise.
        """
        # Check if the expression matches the pattern
        if not self.pattern.match(expression):
            return False
        
        return True

    def find_ans(self, content: str) -> str:
        """
        Extracts and evaluates the mathematical expression from the content.
        
        Args:
            content (str): The content containing the mathematical expression.
        
        Returns:
            str: The evaluated result of the expression.
        """
        expression = self.make_expression(content,self.segid)
        if self.is_valid_expression(expression):
            return str(int(eval(expression)))
        else:
            return str(random.randint(0,1000))

    def new_game(self) -> None:
        """
        Starts a new game by clicking the 'New Game' button.
        """
        body = self.get_body()
        if 'New Game' in body:
            self.wait_and_click('New Game')
        elif 'Go Home' in body:
            self.wait_and_click('Go Home')

    def get_body(self) -> str:
        """
        Retrieves the text content of the body element.
        
        Returns:
            str: The text content of the body element.
        """
        return self.driver.find_element(By.XPATH, "/html/body").text
    
    def set_segid(self, content):
        """
        Sets the segment ID (segid) based on the position of the first operator in the content.

        Args:
            content (str): The content to search for operators.

        Returns:
            None
        """
        # Iterate through the string and check for operators
        lst = content.split('\n')
        n = len(lst)
        while(not lst[n-1].isdigit() and n>=0):
            n-=1
        for i in range(len(lst) - 1):
            if not ((lst[i].isdigit() and lst[i-1] in self.operators) or (lst[i-1].isdigit() and lst[i] in self.operators)):
                self.segid = i
                return
        return

    def play(self) -> None:
        """
        Automates the gameplay by solving the mathematical expressions.
        """
        self.reset()
        self.wait_and_click('Starting')

        while True:
            content = self.get_body()
            # print(content)
            if not self.started and 'Starting' in content:
                print("detected start")
                self.power_nap()
            elif not ('YOUR' in content and 'SCORE' in content):
                if not self.started:
                    inputfield = self.driver.find_element(By.XPATH, "//input[contains(@placeholder,'Please enter your answer here')]")
                    self.set_segid(content)
                self.started = True
                ans = self.find_ans(content)
                print(f"ans = {ans}")
                inputfield.send_keys(ans)
                self.power_nap()
            else:
                break    

    def close(self) -> None:
        """
        Closes the WebDriver.
        """
        self.driver.quit()