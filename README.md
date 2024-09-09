# Instagram Automation Script

This project provides a Python-based automation tool to scrape and analyze Instagram follower and following data. The script logs into Instagram using provided credentials, navigates to the specified user profile, collects the list of followers and following users, and performs a comparison to detect new followers, unfollowers, and new followings. The results are saved in CSV format for analysis.

## Prerequisites

Before running the script, ensure you have the following prerequisites installed:

1. [Python](https://www.python.org/downloads/) (version 3.7 or higher recommended)
2. Required Python libraries:
   - [Selenium](https://pypi.org/project/selenium/)
   - [WebDriver Manager](https://pypi.org/project/webdriver-manager/)
   - [Pandas](https://pandas.pydata.org/)
   - [NumPy](https://numpy.org/)
   - [ConfigParser](https://docs.python.org/3/library/configparser.html)

Install the required libraries using pip:

bash
pip install selenium webdriver-manager pandas numpy


## How It Works

The script automates the following tasks:

1. *Configuration Setup*:
   - The build_config_file.py script sets up the configuration file (config_file.ini) with your Instagram credentials and the target username.
   
2. *Web Scraping*:
   - The browser.py script logs into Instagram using the Edge WebDriver, accesses the target profile, and scrapes followers and followings.

3. *Data Analysis*:
   - It compares the current followers and followings with the previous data to detect changes such as new followers, new unfollows, and new followings.
   - The results are saved in a CSV file located in the results directory.

## Usage

### Step 1: Setup Configuration

1. Run the build_config_file.py script to generate the configuration file (config/config_file.ini).
   
   bash
   python build_config_file.py
   

2. Open config/config_file.ini and update the values with your Instagram credentials and the username you want to track:

   ini
   [user_info]
   username = your-username
   password = your-password
   looking_username = target-username
   

### Step 2: Run the Automation Script

1. Ensure the configuration file (config/config_file.ini) is correctly set up.
2. Run the main script to start the scraping process:

   bash
   python browser.py
   

3. The script will:
   - Log in to Instagram.
   - Scrape the followers and followings of the target profile.
   - Compare the data with the previous session.
   - Save the updated data in the results directory as a CSV file.

### Step 3: View Results

- The results will be saved in the results folder as a CSV file named insta_<looking_username>.csv.
- The CSV file will contain columns like FOLLOWERS, FOLLOWS, UNFOLLOW, NEW_FOLLOWERS, NEW_FOLLOWS, and NEW_UNFOLLOW to help you analyze the changes.

## Script Overview

### Main Components

1. **Config Class**: Reads and stores the user credentials from the configuration file.
2. **InstaInfo Class**: Manages the scraping results and compares them with past data to track changes.
3. **Driver Class**: Handles the Selenium WebDriver actions, including logging in, navigating, scrolling, and collecting data.

### Key Functions

- **__login()**: Logs into Instagram using provided credentials.
- **__getFollowers() and __getFollows()**: Scrapes the list of followers and followings.
- **compare_and_save()**: Compares current data with previous data and saves the results.
- **run()**: Main function to execute the script workflow.
- **close()**: Closes the WebDriver session.
