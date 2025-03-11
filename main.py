

# def submit_codeforces_solution(url, llm_response, cf_email, cf_password):
#     """
#     1. Extracts code from llm_response
#     2. Logs in to Codeforcesz
#     3. Submits the code to the problem found at 'url'
#     4. Intercepts the 'submitSource' API call response
#     5. Returns the submission ID and the intercepted response body (if found)
#     """

#     # --- Extract the code from LLM response ---
#     code_to_submit = extract_cpp_code(llm_response)
    
#     # --- Set up Selenium-wire (Firefox) ---
#     options = webdriver.FirefoxOptions()
#     options.headless = True  # Change to True to run headless
#     service = FirefoxService()
#     driver = webdriver.Firefox(service=service, options=options)

#     try:
#         # --- 1. Log in to Codeforces ---
#         driver.get("https://codeforces.com/enter")

#         # Wait for the login form
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div[4]/div/div/div/form/table/tbody/tr[1]/td[2]/input"))
#         )

#         # Fill email/username
#         driver.find_element(By.XPATH, "/html/body/div[6]/div[4]/div/div/div/form/table/tbody/tr[1]/td[2]/input").send_keys(cf_email)
#         # Fill password
#         driver.find_element(By.XPATH, "/html/body/div[6]/div[4]/div/div/div/form/table/tbody/tr[2]/td[2]/input").send_keys(cf_password)
#         # Click the submit button
#         driver.find_element(By.XPATH, "/html/body/div[6]/div[4]/div/div/div/form/table/tbody/tr[4]/td/div[1]/input").click()

#         # Wait for successful login (check if user is recognized or if page changes)
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CLASS_NAME, "avatar"))
#         )

#         # --- 2. Go to the problem page ---
#         driver.get(url)

#         # Wait for page to load
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div[5]/div[2]/div[1]/ul/li[3]/a"))
#         )

#         # Click the "Submit" button
#         driver.find_element(By.XPATH, "/html/body/div[6]/div[5]/div[2]/div[1]/ul/li[3]/a").click()

#         # Wait for the submit form
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div[5]/div[2]/form/table/tbody/tr[4]/td[2]/textarea"))
#         )

#         # --- 3. Paste the code ---
#         code_area = driver.find_element(By.XPATH, "/html/body/div[6]/div[5]/div[2]/form/table/tbody/tr[4]/td[2]/textarea")
#         code_area.clear()
#         code_area.send_keys(code_to_submit)

#         # (Optional) Select the language if not automatically set to C++
#         # For example, if you need "GNU C++17", you'd do something like:
#         # language_select = Select(driver.find_element(By.NAME, "programTypeId"))
#         # language_select.select_by_visible_text("GNU C++17")

#         # --- 4. Submit the solution ---
#         driver.find_element(By.XPATH, "/html/body/div[6]/div[5]/div[2]/form/table/tbody/tr[6]/td/div/div/input").click()

#         # Wait for the status page to load
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div[5]/div/div[4]/div[6]/table"))
#         )

#         # --- 5. Find the first row's submission ID ---
#         submission_table = driver.find_element(By.XPATH, "/html/body/div[6]/div[5]/div/div[4]/div[6]/table")
#         first_row = submission_table.find_element(By.XPATH, ".//tr[@data-submission-id]")
#         submission_id = first_row.get_attribute("data-submission-id")

#         print(f"Submission ID: {submission_id}")

#         # Click on the row to open the submission details
#         first_row.click()

#         # --- 6. Intercept the "submitSource" API call ---
#         # We'll wait a few seconds for that request to occur.
#         # Then we scan driver.requests to find the relevant one.
#         time.sleep(5)  # Adjust if needed

#         submit_source_response_body = None
#         for request in driver.requests:
#             if request.url.startswith("https://codeforces.com/data/submitSource"):
#                 if request.response:
#                     try:
#                         submit_source_response_body = request.response.body.decode("utf-8", errors="ignore")
#                         break
#                     except:
#                         pass

#         if submit_source_response_body:
#             print("Intercepted submitSource response:")
#             print(submit_source_response_body)
#         else:
#             print("No submitSource response found or could not decode.")

#         return submission_id, submit_source_response_body

#     finally:
#         driver.quit()

import os
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# def save_solution_code(final_code, url):
    # Extract the contest ID and problem index from the URL
    # cpp_code = final_code.strip()
    # pattern = r'/problem/(\d+)/(\w+)'
    # match = re.search(pattern, url)

    # CF_EMAIL = os.getenv("CF_EMAIL")
    # CF_PASSWORD = os.getenv("CF_PASSWORD")

    # if match:
    #     contest_id = match.group(1)
    #     problem_index = match.group(2)
    #     filename = f"{contest_id}-{problem_index}-solution.cpp"
    # else:
    #     filename = "unknown-solution.cpp"
    
    # os.makedirs("solution", exist_ok=True)
    # filepath = os.path.join("solution", filename)
    
    # with open(filepath, "w", encoding="utf-8") as f:
    #     f.write(cpp_code)
    
    # print(f"Solution saved to {filepath}")

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

    # Set up Firefox
    options = webdriver.FirefoxOptions()
    options.headless = True  # or False if you want to see the browser
    service = FirefoxService()
    driver = webdriver.Firefox(service=service, options=options)

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

def scrape_multiple_problems(num_problems=5):
    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    
    driver.get("https://codeforces.com/problemset?tags=1200-1700")

    row_index = 2
    problems_scraped = 0
    while problems_scraped < num_problems:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"/html/body/div[6]/div[4]/div[2]/div[2]/div[6]/table/tbody/tr[{row_index}]/td[2]/div[1]/a")
                )
            )

            problem_link_elem = driver.find_element(By.XPATH, f"/html/body/div[6]/div[4]/div[2]/div[2]/div[6]/table/tbody/tr[{row_index}]/td[2]/div[1]/a")
            problem_url = problem_link_elem.get_attribute("href")
            print(f"Scraping problem: {problem_url}")

            scrape_codeforces_problem(problem_url)

            problems_scraped += 1
            row_index += 1

        except Exception as e:
            print(f"Error occurred: {e}")
            break

    driver.quit()

# Example usage:
if __name__ == "__main__":
    num_problems_to_scrape = 50
    scrape_multiple_problems(num_problems_to_scrape)


