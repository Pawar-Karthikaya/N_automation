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

# ✅ Read from environment variables (GitHub Secrets)
EMAIL = "karthikayapawar114@gmail.com"
PASSWORD = "Naukari_Password@2026"

STATE_FILE = "naukri_state.json"

SUMMARY_V1 = """Python Full Stack Developer | Django & React | AWS & Microservices
Detail-oriented Full Stack Developer with 6 months of experience in designing, developing, and deploying scalable web applications using the Python ecosystem. Expert in building robust back-end systems with Django and FastAPI, integrated with modern front-end frameworks like React.js."""

SUMMARY_V2 = """Python Full Stack Developer | Django, React & AWS
Results-driven Full Stack Developer with 6 months of hands-on experience building and deploying scalable web applications using Python. Proficient in back-end development with Django and FastAPI, and front-end development with React.js and modern UI frameworks."""


def get_next_summary():
    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
        last = state.get("last_version", 2)
    except (FileNotFoundError, json.JSONDecodeError):
        last = 2

    next_version = 2 if last == 1 else 1
    summary = SUMMARY_V2 if last == 1 else SUMMARY_V1

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
    options.add_argument("--disable-extensions")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-running-insecure-content")
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

    # ✅ Hide webdriver flag from Naukri's bot detection
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    wait = WebDriverWait(driver, 30)

    try:
        # ✅ Verify secrets loaded
        if not EMAIL or not PASSWORD:
            raise Exception("❌ EMAIL or PASSWORD env variable is missing!")
        logging.info(f"✅ Credentials loaded | Email: {EMAIL[:6]}***")

        new_summary = get_next_summary()

        # ── LOGIN ──────────────────────────────────────────────
        logging.info("🔐 Opening Naukri login page...")
        driver.get("https://www.naukri.com/nlogin/login")
        time.sleep(5)

        # ✅ Debug screenshot before login
        driver.save_screenshot("login_page.png")
        logging.info(f"📸 Page title: {driver.title}")
        logging.info(f"🌐 Current URL: {driver.current_url}")

        # ✅ Find email field
        logging.info("🔍 Looking for email field...")
        try:
            email_field = wait.until(EC.presence_of_element_located((By.ID, "usernameField")))
        except:
            email_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @type='email']")))
        
        email_field.clear()
        email_field.send_keys(EMAIL)
        logging.info("✅ Email entered")
        time.sleep(1)

        # ✅ Find password field
        try:
            pwd_field = driver.find_element(By.ID, "passwordField")
        except:
            pwd_field = driver.find_element(By.XPATH, "//input[@type='password']")
        
        pwd_field.clear()
        pwd_field.send_keys(PASSWORD)
        logging.info("✅ Password entered")
        time.sleep(1)

        # ✅ Click login
        try:
            login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        except:
            login_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Login')]")
        
        driver.execute_script("arguments[0].click();", login_btn)
        logging.info("✅ Login button clicked")
        time.sleep(6)

        # ✅ Screenshot after login attempt
        driver.save_screenshot("after_login.png")
        logging.info(f"🌐 URL after login: {driver.current_url}")

        # ✅ Wait until redirected away from login page
        wait.until(lambda d: "nlogin" not in d.current_url)
        logging.info(f"✅ Logged in successfully | URL: {driver.current_url}")

        # ── PROFILE PAGE ───────────────────────────────────────
        driver.get("https://www.naukri.com/mnjuser/profile")
        time.sleep(5)
        driver.save_screenshot("profile_page.png")
        logging.info("✅ Profile page loaded")

        # ── FIND EDIT BUTTON ───────────────────────────────────
        edit_xpaths = [
            "//div[contains(@class,'profileSummary')]//img[contains(@alt,'pencil')]/..",
            "//div[contains(@class,'profileSummary')]//span[contains(@class,'edit')]",
            "//div[contains(@class,'profileSummary')]//button",
            "//section[contains(@class,'summary')]//img[contains(@alt,'edit')]/..",
            "//div[contains(@class,'summary')]//span[@class='edit']",
        ]

        edit_icon = None
        for xpath in edit_xpaths:
            try:
                edit_icon = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                logging.info(f"✅ Found edit button: {xpath}")
                break
            except:
                logging.info(f"⚠️ Not found: {xpath}")

        if not edit_icon:
            driver.save_screenshot("edit_button_error.png")
            raise Exception("Could not find profile summary edit button")

        driver.execute_script("arguments[0].click();", edit_icon)
        time.sleep(3)

        # ── FIND TEXTAREA ──────────────────────────────────────
        textarea_xpaths = [
            "//textarea[contains(@placeholder,'summary')]",
            "//textarea[contains(@placeholder,'Summary')]",
            "//textarea[contains(@id,'summary')]",
            "//textarea[contains(@id,'Summary')]",
            "//textarea",
        ]

        summary_box = None
        for xpath in textarea_xpaths:
            try:
                summary_box = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                logging.info(f"✅ Found textarea: {xpath}")
                break
            except:
                logging.info(f"⚠️ Textarea not found: {xpath}")

        if not summary_box:
            driver.save_screenshot("textarea_error.png")
            raise Exception("Could not find summary textarea")

        # ── TYPE NEW SUMMARY ───────────────────────────────────
        driver.execute_script("arguments[0].value = '';", summary_box)
        summary_box.click()
        time.sleep(0.5)

        for chunk in [new_summary[i:i+100] for i in range(0, len(new_summary), 100)]:
            summary_box.send_keys(chunk)
            time.sleep(0.1)

        time.sleep(1)
        typed_text = summary_box.get_attribute("value").strip()
        logging.info(f"📋 Text in box ({len(typed_text)} chars): {typed_text[:80]}...")

        # ── SAVE ───────────────────────────────────────────────
        save_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Save')] | //button[@type='submit']")
        ))
        driver.execute_script("arguments[0].click();", save_btn)
        time.sleep(3)
        driver.save_screenshot("after_save.png")
        logging.info("✅ Profile Summary updated successfully!")

    except Exception as e:
        logging.error(f"❌ Error: {e}")
        try:
            driver.save_screenshot("naukri_error.png")
            logging.info("📸 Screenshot saved: naukri_error.png")
        except:
            pass
    finally:
        driver.quit()


if __name__ == "__main__":
    update_naukri_profile()
