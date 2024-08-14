from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
import os
import shutil
import json
from datetime import date
from pathlib import Path


def find_file_in_directory(directory, file_name):
    # Normalize the file name to search (remove extension if it exists)
    base_name = os.path.splitext(file_name)[0]

    # List all files and directories in the given directory
    try:
        for entry in os.listdir(directory):
            # Check if the entry is a file and matches the base name
            if os.path.isfile(os.path.join(directory, entry)) and entry.startswith(base_name):
                print(f"File '{entry}' found in directory '{directory}'.")
                return os.path.join(directory, entry)

        print(f"File '{file_name}' not found in directory '{directory}'.")
        return None
    except FileNotFoundError:
        print(f"The directory '{directory}' does not exist.")
        return None
    except PermissionError:
        print(f"Permission denied to access directory '{directory}'.")
        return None


def save_photo_name(browser, photo_name, json_path="photo_names.json"):
    # Load existing photo names from the JSON file
    if os.path.exists(json_path):
        with open(json_path, "r") as json_file:
            photo_names = json.load(json_file)
    else:
        photo_names = []

    # Check if the photo name is already in the list
    if photo_name in photo_names:
        #print(f"The photo name '{photo_name}' is already present.")
        return False
    else:
        # Add the new photo name to the list
        photo_names.append(photo_name)
        with open(json_path, "w") as json_file:
            json.dump(photo_names, json_file, indent=4)
        browser.find_element(by=By.ID, value="download").click()
        print(f"The photo '{photo_name}' has been downloaded.")
        return True
    
def move_downloaded_photo(filename, source_path, destination_path = False):
    try:
        if(source_path == False):
            source_path = str(Path.home()) + "\\Downloads"
        source_file_path = find_file_in_directory(source_path, filename)
        #file_path = os.path.join(os.getcwd(), date.today().strftime("%Y-%m-%d"))
        # Ensure the destination directory exists; create it if it doesn't
        destination_path = os.path.join(os.getcwd(), date.today().strftime("%Y-%m-%d"))
        os.makedirs(destination_path, exist_ok=True)
        #source_file = os.path.join(source_path, filename)

        # Move the file
        shutil.move(source_file_path, destination_path)
        print(f"File moved from '{source_path}' to '{destination_path}' successfully.")
    except FileNotFoundError:
        print(f"Error: The file '{source_path}' was not found.")
    except PermissionError:
        print(f"Error: Permission denied when moving the file '{source_path}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def move_photo(source_path, json_path="photo_names.json"):
    try:
        if os.path.exists(json_path):
            with open(json_path, "r") as json_file:
                photo_names = json.load(json_file)
        else:
            return
        for item in photo_names:
            print(item)
            move_downloaded_photo(item, source_path)
    except FileNotFoundError:
        print(f"Error: While moving files.")

#Loop to detect, if all photos are loaded by skald (dynamic loading finished)
def check_image_loaded(browser) -> int:
    image_count = len(browser.find_elements(by=By.CLASS_NAME, value="image-container"))
    while True:
        print(f"Anzahl Bilder auf Skald: '{image_count}'")
        time.sleep(10)
        image_count_new = len(browser.find_elements(by=By.CLASS_NAME, value="image-container"))
        if image_count < image_count_new:
            image_count = image_count_new
        else:
            return image_count

def main(gallery_id, move_files=False, source_path=False) -> None:
    gallery_url='https://skald.com/event/gallery?lang=en&id=' + str(gallery_id)
    browser = webdriver.Firefox()
    browser.get(gallery_url)
    time.sleep(5)
    try:
        wait = WebDriverWait(browser, timeout=5)
        alert = wait.until(lambda d : d.switch_to.alert)
        alert.dismiss() 
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    try:
        cookie_button = browser.find_element(by=By.ID, value="cookiePrompt-accept")
        cookie_button.click()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    gallery_title = browser.find_element(by=By.ID, value="page-title").text.split(': ', 1)[1]
    print(f"Galeriename: '{gallery_title}'")
    #Wait 2min to login to skald & load all thumbnails to get the count of the photos
    print(f"Bitte in Skald einloggen, falls die Bilder im Early Access sind.")
    time.sleep(60) 

    image_count =  check_image_loaded(browser)

    #Open first image
    first_image = browser.find_element(by=By.ID, value="slideIndex-0")
    first_image.click()

    for x in range(image_count-1): #Counter starts with 0
        current_url = browser.current_url
        file_name = current_url.rsplit('=', 1)[1].split('.', 1)[0]
        save_photo_name(browser, file_name) 
        if x < (image_count-2): #At the last element it isn't possible to click the element
            browser.find_element(by=By.ID, value="next").click()

    #Wait 2min to ensure that the download is finished
    time.sleep(120)
    if(move_files):
        move_photo(source_path)
    browser.close()

if __name__ == '__main__':
    main(33)