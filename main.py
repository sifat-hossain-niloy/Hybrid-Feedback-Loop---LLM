import os
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_codeforces_problem(url):

    pattern = r'/problem/(\d+)/(\w+)'  # Captures contest ID and problem index
    match = re.search(pattern, url)
    if match:
        contest_id = match.group(1)
        problem_index = match.group(2)
        filename = f"{contest_id}-{problem_index}.json"
    else:
        # Fallback if regex doesn't match (unlikely for standard CF URLs)
        filename = "problem-data.json"

    # --- Check if we already have a cached file ---
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            print(f"Loading cached data from {filename}...")
            return json.load(f)
    # Set up Firefox options (headless mode)
    options = webdriver.FirefoxOptions()
    options.headless = False  # Change to True if you prefer headless mode

    # Initialize Firefox with Geckodriver
    service = FirefoxService()  # Use default; specify executable_path if required.
    driver = webdriver.Firefox(service=service, options=options)

    # Open the given Codeforces problem URL
    driver.get(url)
    
    # Wait until the problem statement (or any known element) is present
    wait = WebDriverWait(driver, 10)
    # You can adjust this XPath to a more generic one if needed
    wait.until(EC.presence_of_element_located(
        (By.XPATH, "/html/body/div[6]/div[4]/div[2]/div[3]/div[2]/div")
    ))
    
    # --- Extract the problem statement ---
    #   (Keeping your original absolute XPath, but you could also switch to a relative one)
    try:
        statement_elem = driver.find_element(
            By.XPATH, "/html/body/div[6]/div[4]/div[2]/div[3]/div[2]/div/div[2]"
        )
        statement = statement_elem.text
    except Exception:
        statement = "Not found"
    
    # --- Extract the input clarification (all p tags) ---
    try:
        input_spec_elems = driver.find_elements(
            By.XPATH, "/html/body/div[6]/div[4]/div[2]/div[3]/div[2]/div/div[3]//p"
        )
        if input_spec_elems:
            # Join all paragraph texts with a newline
            input_spec = "\n".join(elem.text for elem in input_spec_elems)
        else:
            input_spec = "Not found"
    except Exception:
        input_spec = "Not found"
    
    # --- Extract the output clarification (all p tags) ---
    try:
        output_spec_elems = driver.find_elements(
            By.XPATH, "/html/body/div[6]/div[4]/div[2]/div[3]/div[2]/div/div[4]//p"
        )
        if output_spec_elems:
            output_spec = "\n".join(elem.text for elem in output_spec_elems)
        else:
            output_spec = "Not found"
    except Exception:
        output_spec = "Not found"
    
    # --- Extract multiple sample tests from within the single 'sample-test' container ---
    sample_tests = []
    try:
        # Find the single container that holds all sample test data
        sample_test_container = driver.find_element(By.XPATH, "//div[@class='sample-test']")
        
        # Within that container, find all input blocks
        input_blocks = sample_test_container.find_elements(By.XPATH, ".//div[@class='input']")
        # Similarly, find all output blocks
        output_blocks = sample_test_container.find_elements(By.XPATH, ".//div[@class='output']")
        
        # Pair each input block with the corresponding output block by index
        for in_block, out_block in zip(input_blocks, output_blocks):
            try:
                in_pre = in_block.find_element(By.XPATH, ".//pre")
                out_pre = out_block.find_element(By.XPATH, ".//pre")
                
                sample_tests.append({
                    "input": in_pre.text.strip(),
                    "output": out_pre.text.strip()
                })
            except Exception:
                # If something goes wrong (e.g., no <pre> found), skip gracefully
                pass
    except Exception:
        sample_tests = []

    # --- Extract problem tags (if available) ---
    try:
        # Adjust XPath if the tags are located elsewhere for your specific problem
        tags_elem = driver.find_element(
            By.XPATH, "/html/body/div[6]/div[4]/div[1]/div[3]/div[2]"
        )
        tag_elements = tags_elem.find_elements(By.XPATH, ".//a")
        tags = [tag.text.strip() for tag in tag_elements if tag.text.strip()]
    except Exception:
        tags = []
    
    # --- Extract problem rating (if available) ---
    try:
        rating_elem = driver.find_element(By.XPATH, "//span[contains(@class, 'problem-rating')]")
        rating = rating_elem.text.strip()
    except Exception:
        rating = "Not found"
    
    # Close the browser
    driver.quit()

    problem_data = {
        "statement": statement,
        "input_specification": input_spec,
        "output_specification": output_spec,
        "sample_tests": sample_tests,
        "tags": tags,
        "rating": rating
    }


    # --- Save scraped data to JSON for future reuse ---
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(problem_data, f, indent=4, ensure_ascii=False)
    
    # Return the scraped data as a dictionary
    return problem_data

# Example usage:
if __name__ == "__main__":
    url = "https://codeforces.com/problemset/problem/30/D"  # Replace with any CF problem URL
    problem_data = scrape_codeforces_problem(url)
    
    from pprint import pprint
    pprint(problem_data)
