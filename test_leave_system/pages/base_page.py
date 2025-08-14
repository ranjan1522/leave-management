from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self,driver):
        self.driver = driver
        self.wait = WebDriverWait(driver,10)

    def click(self,locator):
        self.wait.until(EC.visibility_of_element_located(locator)).click()

    def enter_text(self,locator,text):
        self.wait.until(EC.visibility_of_element_located(locator)).send_keys(text)

    def get_text(self,locator):
        return self.wait.until(EC.visibility_of_element_located(locator)).text

    def is_visible(self,locator):
        return self.wait.until(EC.visibility_of_element_located(locator))