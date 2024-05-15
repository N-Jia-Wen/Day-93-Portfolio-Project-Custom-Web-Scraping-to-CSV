from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pandas
import os

csv_file_name = "Audible_Audiobooks_in_Computers_&_Technology.csv"
# The number of total pages on the website
page_num = 1
website_to_scrape = (f"https://www.audible.com/search?keywords=book&node=18573211011&pageSize=50&sort=popularity-rank&"
                     f"page={page_num}&ref_pageloadid=fkl6o86nilvAYVsD&ref=a_search_c4_pageNext&pf_rd_p=1d79b443-2f1d-"
                     f"43a3-b1dc-31a2cd242566&pf_rd_r=7Y6GEAGTZ55W0QS0H4JT&pageLoadId=sogJf4RXq0q3WDRI&"
                     f"creativeId=18cc2d83-2aa9-46ca-8a02-1d1cc7052e2a")


chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)
driver.get(website_to_scrape)
input("Press Enter after completing CAPTCHA, if any: ")


titles = driver.find_elements(By.CSS_SELECTOR, value="h3.bc-heading a")
# Finds the great-grandparent elements of each element in titles (i.e. the unordered list):
book_lists = [title.find_element(By.XPATH, value="../../../../..") for title in titles]
rating_info = driver.find_elements(By.CSS_SELECTOR, value="li.ratingsLabel")

for num_audiobooks in range(len(book_lists)):
    # Finds the grandparent element of author (i.e. the unordered list)
    book_list = book_lists[num_audiobooks]

    title = book_list.find_element(By.CSS_SELECTOR, "h3.bc-heading a").text
    try:
        description = book_list.find_element(By.CSS_SELECTOR, "li.subtitle span").text
    except NoSuchElementException:
        description = None
    author = book_list.find_element(By.CSS_SELECTOR, "li.authorLabel span").text.split(": ")[-1]
    narrator = book_list.find_element(By.CSS_SELECTOR, "li.narratorLabel span").text.split(": ")[-1]
    length = book_list.find_element(By.CSS_SELECTOR, "li.runtimeLabel span").text.split(": ")[-1]
    release_date = book_list.find_element(By.CSS_SELECTOR, "li.releaseDateLabel span").text.split(": ")[-1]
    language = book_list.find_element(By.CSS_SELECTOR, "li.languageLabel span").text.split(": ")[-1]
    no_of_ratings = rating_info[num_audiobooks].find_element(By.CSS_SELECTOR, value="span.bc-size-small.bc-color-secondary").text
    try:
        rating_value = rating_info[num_audiobooks].find_element(By.CSS_SELECTOR, value="span.bc-pub-offscreen").text
    except NoSuchElementException:  # Only occurs of audiobook has not been rated yet
        rating_value = None
    # Both rating_value and description can be blank, so these error handlers are there to address them

    new_data = [{
        "Title": title,
        "Description": description,
        "Author(s)": author,
        "Narrator": narrator,
        "Length": length,
        "Release_Date (MM-DD-YY)": release_date,
        "Language": language,
        "Number_of_Ratings": no_of_ratings,
        "Rating": rating_value
    }]
    df = pandas.DataFrame(new_data)
    df.set_index("Title", inplace=True)

    # Check if the file exists to determine if we should write the header
    file_exists = os.path.isfile(csv_file_name)
    df.to_csv(csv_file_name, mode="a", header=not file_exists)
