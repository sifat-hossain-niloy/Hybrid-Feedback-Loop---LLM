import os
import json
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def init_webdriver(webdriver_path):
    options = webdriver.ChromeOptions()
    service = Service(executable_path=webdriver_path)
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options, service=service)
    return driver


def scrape_codeforces_problem(url):
    pattern = r'/problem/(\d+)/(\w+)'
    match = re.search(pattern, url)
    if match:
        contest_id = match.group(1)
        problem_index = match.group(2)
        filename = f"{contest_id}-{problem_index}.json"
    else:
        filename = "problem-data.json"

    # Check cache
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            print(f"Loading cached data from {filename}...")
            return json.load(f)

    # Initialize Chrome WebDriver
    driver = init_webdriver('/usr/bin/chromedriver')

    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located(
        (By.XPATH, "/html/body/div[6]/div[4]/div[2]/div[3]/div[2]/div")
    ))

    # --- Problem Statement ---
    try:
        statement_elem = driver.find_element(By.XPATH, "/html/body/div[6]/div[4]/div[2]/div[3]/div[2]/div/div[2]")
        statement = statement_elem.text
    except Exception:
        statement = "Not found"
    
    # --- Input Specification ---
    try:
        input_spec_elems = driver.find_elements(By.XPATH, "/html/body/div[6]/div[4]/div[2]/div[3]/div[2]/div/div[3]//p")
        input_spec = "\n".join(elem.text for elem in input_spec_elems) if input_spec_elems else "Not found"
    except Exception:
        input_spec = "Not found"

    # --- Output Specification ---
    try:
        output_spec_elems = driver.find_elements(By.XPATH, "/html/body/div[6]/div[4]/div[2]/div[3]/div[2]/div/div[4]//p")
        output_spec = "\n".join(elem.text for elem in output_spec_elems) if output_spec_elems else "Not found"
    except Exception:
        output_spec = "Not found"

    # --- Sample Tests ---
    sample_tests = []
    try:
        sample_test_container = driver.find_element(By.XPATH, "//div[@class='sample-test']")
        input_blocks = sample_test_container.find_elements(By.XPATH, ".//div[@class='input']")
        output_blocks = sample_test_container.find_elements(By.XPATH, ".//div[@class='output']")

        for in_block, out_block in zip(input_blocks, output_blocks):
            in_pre = in_block.find_element(By.XPATH, ".//pre")
            out_pre = out_block.find_element(By.XPATH, ".//pre")
            sample_tests.append({
                "input": in_pre.text.strip(),
                "output": out_pre.text.strip()
            })
    except Exception:
        sample_tests = []

    # --- Note (optional) ---
    #   If a div with class "note" is present, gather the text from all <p> tags.
    #   XPATH example: /html/body/div[6]/div[5]/div[2]/div[3]/div[2]/div/div[6]
    try:
        note_div = driver.find_element(By.XPATH, "//div[@class='note']")
        note_p_elems = note_div.find_elements(By.TAG_NAME, "p")
        if note_p_elems:
            note = "\n".join(p.text for p in note_p_elems)
        else:
            note = "Not found"
    except Exception:
        note = "Not found"

    # --- Tags and Rating (from tags) ---
    tags = []
    rating = "Not found"

    # Collect tags from the incrementing div elements
    try:
        for i in range(1, 10):
            try:
                tag_elem = driver.find_element(By.XPATH, f"/html/body/div[6]/div[4]/div[1]/div[3]/div[2]/div[{i}]")
                tag_text = tag_elem.text.strip()
                tags.append(tag_text)
            except Exception:
                pass
    except Exception:
        pass

    # Remove the last tag if it is "No tag edit access"
    if tags and tags[-1] == "No tag edit access":
        tags.pop()

    # If the new last tag starts with '*', treat it as rating
    if tags and tags[-1].startswith("*"):
        rating_str = tags.pop()
        rating = rating_str[1:]  # Remove the asterisk, e.g. "*1300" -> "1300"

    driver.quit()

    problem_data = {
        "statement": statement,
        "input_specification": input_spec,
        "output_specification": output_spec,
        "sample_tests": sample_tests,
        "note": note,  # The newly added note field
        "tags": tags,
        "rating": rating
    }

    # Save to JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(problem_data, f, indent=4, ensure_ascii=False)

    return problem_data

def scrape_multiple_problems(num_problems):
    # Initialize Chrome WebDriver
    driver = init_webdriver('/usr/bin/chromedriver')
    
    try:
        print("Navigating to Codeforces problemset...")
        driver.get("https://codeforces.com/problemset?tags=1200-1700")
        
        # Wait for page to load
        time.sleep(5)
        
        print("Page loaded successfully")
        
        row_index = 2
        problems_scraped = 0
        while problems_scraped < num_problems:
            try:
                print(f"Looking for problem at row {row_index}...")
                
                # Wait for the problem link to be present
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f"/html/body/div[6]/div[4]/div[2]/div[2]/div[6]/table/tbody/tr[{row_index}]/td[2]/div[1]/a")
                    )
                )

                problem_link_elem = driver.find_element(By.XPATH, f"/html/body/div[6]/div[4]/div[2]/div[2]/div[6]/table/tbody/tr[{row_index}]/td[2]/div[1]/a")
                problem_url = problem_link_elem.get_attribute("href")
                print(f"Found problem: {problem_url}")

                scrape_codeforces_problem(problem_url)

                problems_scraped += 1
                row_index += 1

            except Exception as e:
                print(f"Error occurred at row {row_index}: {e}")
                print("Trying next row...")
                row_index += 1
                if row_index > 50:  # Safety limit
                    print("Reached safety limit, stopping...")
                    break

    except Exception as e:
        print(f"Error in main scraping function: {e}")
    finally:
        driver.quit()

# Example usage:
if __name__ == "__main__":
    num_problems_to_scrape = 60
    scrape_multiple_problems(num_problems_to_scrape)

