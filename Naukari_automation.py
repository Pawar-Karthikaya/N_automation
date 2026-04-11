from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

EMAIL = os.environ.get("NAUKRI_EMAIL")
PASSWORD = os.environ.get("NAUKRI_PASSWORD")

def update_naukri_profile():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    wait = WebDriverWait(driver, 20)

    try:
        logging.info("🔐 Logging in...")
        driver.get("https://www.naukri.com/nlogin/login")
        time.sleep(2)
        wait.until(EC.presence_of_element_located((By.ID, "usernameField"))).send_keys(EMAIL)
        driver.find_element(By.ID, "passwordField").send_keys(PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(4)
        logging.info(f"✅ Logged in | URL: {driver.current_url}")

        driver.get("https://www.naukri.com/mnjuser/profile")
        time.sleep(3)

        edit_icon = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class,'profileSummary')]//img[contains(@alt,'pencil')]/..")
        ))
        driver.execute_script("arguments[0].click();", edit_icon)
        time.sleep(2)

        summary_box = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//textarea[contains(@placeholder,'summary') or contains(@id,'summary') or contains(@id,'Summary')]")
        ))

        current_text = summary_box.get_attribute("value").strip()
        summary_box.clear()
        time.sleep(0.5)

        if current_text.endswith(" "):
            summary_box.send_keys(current_text.rstrip())
        else:
            summary_box.send_keys(current_text + " ")

        time.sleep(1)

        save_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Save')] | //button[@type='submit']")
        ))
        driver.execute_script("arguments[0].click();", save_btn)
        time.sleep(2)

        logging.info("✅ Profile Summary updated successfully!")

    except Exception as e:
        logging.error(f"❌ Error: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    update_naukri_profile()
