from pages.login_page import LoginPage

def test_valid_login(setup_driver):
    driver = setup_driver
    driver.get("https://leave-management-8kuk.onrender.com/login")
    login_page = LoginPage(driver)
    login_page.login("student1", "pass123")
    print(driver.title)
    #assert "Dashboard" in driver.title
'''
def test_invalid_login(setup_driver):
    driver = setup_driver
    driver.get("https://example.com/login")
    login_page = LoginPage(driver)
    login_page.login("wrong", "wrong")
    assert "Invalid credentials" in login_page.get_error_message()
'''
