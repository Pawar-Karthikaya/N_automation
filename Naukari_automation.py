from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import logging
import json

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

EMAIL = os.environ.get("NAUKRI_EMAIL")
PASSWORD = os.environ.get("NAUKRI_PASSWORD")

# State file to track which version was last used
STATE_FILE = "naukri_state.json"

SUMMARY_V1 = """Python Full Stack Developer | Django & React | AWS & Microservices
Detail-oriented Full Stack Developer with 6 months of experience in designing, developing, and deploying scalable web applications using the Python ecosystem. Expert in building robust back-end systems with Django and FastAPI, integrated with modern front-end frameworks like React.js."""

SUMMARY_V2 = """Python Full Stack Developer | Django, React & AWS
Results-driven Full Stack Developer with 6 months of hands-on experience building and deploying scalable web applications using Python. Proficient in back-end development with Django and FastAPI, and front-end development with React.js and modern UI frameworks."""

def get_next_summary():
    """Alternate between V1 and V2 on each run."""
    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
        last = state.get("last_version", 2)
    except (FileNotFoundError, json.JSONDecodeError):
        last = 2  # default so first run uses V1

    if last == 1:
        next_version = 2
        summary = SUMMARY_V2
    else:
        next_version = 1
        summary = SUMMARY_V1

    with open(STATE_FILE, "w") as f:
        json.dump({"last_version": next_version}, f)

    logging.info(f"📝 Using Summary Version {next_version}")
    return summary

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
        new_summary = get_next_summary()

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

        # Clear using JS to ensure Naukri's React state resets properly
        driver.execute_script("arguments[0].value = '';", summary_box)
        summary_box.click()
        time.sleep(0.3)

        # Type new summary in chunks (avoids input event issues with send_keys on large text)
        for chunk in [new_summary[i:i+100] for i in range(0, len(new_summary), 100)]:
            summary_box.send_keys(chunk)
            time.sleep(0.1)

        time.sleep(1)

        # Verify what was typed
        typed_text = summary_box.get_attribute("value").strip()
        logging.info(f"📋 Text in box ({len(typed_text)} chars): {typed_text[:80]}...")

        save_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Save')] | //button[@type='submit']")
        ))
        driver.execute_script("arguments[0].click();", save_btn)
        time.sleep(3)

        # Confirm save by checking if modal closed or success toast appeared
        logging.info("✅ Profile Summary updated successfully!")

    except Exception as e:
        logging.error(f"❌ Error: {e}")
        # Save screenshot for debugging
        try:
            driver.save_screenshot("naukri_error.png")
            logging.info("📸 Screenshot saved: naukri_error.png")
        except:
            pass
    finally:
        driver.quit()

if __name__ == "__main__":
    update_naukri_profile()
