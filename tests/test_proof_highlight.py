from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

chrome_options = Options()
chrome_options.binary_location = "/usr/bin/chromium-browser"
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Remote(
    command_executor="http://localhost:4444/wd/hub",
    options=chrome_options
)

SCREENSHOTS = "/home/goober/.openclaw/workspace/screenshots"

try:
    # Load the game from host server
    print("Loading game...")
    driver.get("http://172.17.0.1:9100/")
    time.sleep(3)
    driver.save_screenshot(f"{SCREENSHOTS}/proof_01_fresh.png")
    print(f"Screenshot 1: {driver.title}")

    # Open guide
    print("Opening guide...")
    guide_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "guide-btn"))
    )
    guide_btn.click()
    time.sleep(3)
    driver.save_screenshot(f"{SCREENSHOTS}/proof_02_guide_open.png")
    print("Screenshot 2: Guide open")

    # Check for proof highlights
    cells = driver.find_elements(By.CLASS_NAME, "cell")
    guide_targets = [c for c in cells if "guide-target" in c.get_attribute("class")]
    guide_proofs = [c for c in cells if "guide-proof" in c.get_attribute("class")]

    print(f"Target cells: {len(guide_targets)}")
    print(f"Proof cells (NEW!): {len(guide_proofs)}")

    # Read explanation
    try:
        expl = driver.find_element(By.ID, "guide-explanation")
        text = expl.text[:200]
        print(f"Explanation: {text}...")
    except:
        pass

    # Check candidates display
    try:
        cands = driver.find_element(By.ID, "guide-candidates")
        print(f"Candidates line: {cands.text}")
    except:
        pass

    time.sleep(2)
    driver.save_screenshot(f"{SCREENSHOTS}/proof_03_final.png")
    print("All screenshots saved!")

finally:
    pass
