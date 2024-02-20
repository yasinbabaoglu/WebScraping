import configparser
# from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from msedge.selenium_tools import Edge
from msedge.selenium_tools import EdgeOptions
import pickle
import json
import time
import os
import random

import pandas as pd
import numpy as np

class Config:
    username : str
    password : str
    looking_username : str
    
    def __init__(
        self,
        file_name : str
        ) -> None:
        config = configparser.ConfigParser()
        config.read(file_name)

        self.username = config['user_info']['username']
        self.password = config['user_info']['password']
        self.looking_username = config['user_info']['looking_username']
        
        
class InstaInfo:
    __path : str
    __columns : list[str]
    __insta_df : pd.DataFrame
    __old_unfollow_set : set[str]
    __old_followers_set : set[str]
    __old_follows_set : set[str]
    __followers_set : set[str]
    __follows_set : set[str]
    __unfollow_set : set[str]
    __is_init_run : bool

    def __init__(
        self,
        looking_username : str
        ) -> None:
        dir = "results"
        self.__path = f"{dir}/insta_{looking_username}.csv"
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.__columns = ["FOLLOWERS", "FOLLOWS", "UNFOLLOW", "NEW_FOLLOWERS", "NEW_FOLLOWS", "NEW_UNFOLLOW"]
        self.__is_init_run = False
        if not self.__read_df("looking_username"):
            self.__is_init_run = True
            self.__create_df()
            
    def __read_df(
        self,
        looking_username : str
        ) -> bool:
        try:
            self.__insta_df = pd.read_csv(self.__path, sep=";", columns=self.__columns)
            self.__old_unfollow_set = set(self.__insta_df["UNFOLLOW"])
            self.__old_followers_set = set(self.__insta_df["FOLLOWERS"])
            self.__old_follows_set = set(self.__insta_df["FOLLOWS"])
            dir = "backup"
            backup_path = f"{dir}/backup_{looking_username}.csv"
            if not os.path.exists(dir):
                os.makedirs(dir)
            self.__write_df(backup_path)
            return True
        except:
            return False
        
    def __write_df(
        self,
        path : str
        ) -> bool:
        try:
            self.__insta_df.to_csv(path, sep=";", columns=self.__columns, index=False)
            return True
        except:
            return False    

    def __create_df(
        self
        ) -> None:
        self.__old_unfollow_set = set()
        self.__old_followers_set = set()
        self.__old_follows_set = set()
        self.__insta_df = pd.DataFrame(columns=self.__columns)
    
    def set_data(
        self,
        followers_set : set[str],
        follows_set : set[str]
        ) -> None:
        self.__followers_set = followers_set
        self.__follows_set = follows_set
        self.__unfollow_set = set(self.__follows_set) - set(self.__followers_set)
        print("followers_set:\n", self.__followers_set)
        print("follows_set:\n", self.__follows_set)        

    def compare_and_save(
        self
        ) -> None:
        if self.__is_init_run:
            new_followers = list()
            new_follows = list()
            new_unfollow = list()
        else:
            new_followers = list(self.__followers_set - self.__old_followers_set)
            new_follows = list(self.__follows_set - self.__old_follows_set)
            new_unfollow = list(self.__unfollow_set - self.__old_unfollow_set)
            
        unfollow = list(self.__unfollow_set)
        followers = list(self.__followers_set)
        follows = list(self.__follows_set)
        
        length = {
            "NEW_FOLLOWERS" : len(new_followers),
            "NEW_FOLLOWS" : len(new_follows),
            "NEW_UNFOLLOW" : len(new_unfollow),
            "UNFOLLOW" : len(unfollow),
            "FOLLOWERS" : len(followers),
            "FOLLOWS" : len(follows)
        }
        length["MAX"] = max([length["NEW_FOLLOWERS"], 
                             length["NEW_FOLLOWS"], 
                             length["NEW_UNFOLLOW"],
                             length["UNFOLLOW"],
                             length["FOLLOWERS"],
                             length["FOLLOWS"]]
                            )
        
        new_followers.sort()
        new_follows.sort()
        new_unfollow.sort()
        unfollow.sort()
        followers.sort()
        follows.sort()
        
        self.__insta_df["NEW_FOLLOWERS"] = new_followers + (length["MAX"] - length["NEW_FOLLOWERS"]) * [np.nan]
        self.__insta_df["NEW_FOLLOWS"] = new_follows + (length["MAX"] - length["NEW_FOLLOWS"]) * [np.nan]
        self.__insta_df["NEW_UNFOLLOW"] = new_unfollow + (length["MAX"] - length["NEW_UNFOLLOW"]) * [np.nan]
        self.__insta_df["UNFOLLOW"] = unfollow + (length["MAX"] - length["UNFOLLOW"]) * [np.nan]
        self.__insta_df["FOLLOWERS"] = followers + (length["MAX"] - length["FOLLOWERS"]) * [np.nan]
        self.__insta_df["FOLLOWS"] = follows + (length["MAX"] - length["FOLLOWS"]) * [np.nan]

        if not self.__write_df(self.__path):
            print(f"ERROR: Writing File Failed - {self.__path}")
        else:
            print(f"Finished Successfully - {self.__path}")
        
        
class Driver:
    __driver : Edge
    __config : Config
    __insta_info : InstaInfo
    
    def __init__(
        self, 
        link: str,
        file_name :str,
        is_hidden: bool = True
        ) -> None:
        self.__link = link
        self.__setUserInfo(file_name)
        
        options = EdgeOptions()
        user_agent = "your-user-agent"
        options.add_argument(f"--user-agent={user_agent}")
        options.use_chromium = True
        if is_hidden:
            options.add_argument('headless')
        options.add_argument("disable-gpu")
        options.add_argument("--enable-chrome-browser-cloud-management")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.__driver = Edge(EdgeChromiumDriverManager().install(), options=options)

        dir = "cookies"
        self.__cookies_name = f"{dir}/{self.__config.username}.json"
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.__goWebSite()
        self.__insta_info = InstaInfo(self.__config.looking_username)

    def __setUserInfo(
        self, 
        file_name :str
        ) -> None:
        self.__config = Config(file_name)

    def __wait(
        self
        ) -> None:
        self.__driver.implicitly_wait(10)
        
    def __net_wait_random(
        self,
        max_wait_seconds :int = 2,
        min_wait_seconds :int = 0
        ) -> None:
        random_wait = random.uniform(min_wait_seconds, max_wait_seconds)
        time.sleep(random_wait)

    def __saveCookies(
        self
        ) -> None:
        cookies = self.__driver.get_cookies()
        with open(self.__cookies_name, 'w') as file:
            json.dump(cookies, file)
        print('New Cookies saved successfully')
    
    def __loadCookies(
        self
        ) -> None:
        if os.path.isfile(self.__cookies_name):
            with open(self.__cookies_name, 'r') as file:
                cookies = json.load(file)
            for cookie in cookies:
                self.__driver.add_cookie(cookie)
        else:
            print('No cookies file found')
        self.__driver.refresh() # Refresh Browser after login
        
    def __goWebSite(
        self
        ) -> None:
        self.__driver.get(self.__link)
        self.__net_wait_random(1,3)
        self.__loadCookies()

    def __login(
        self
        ) -> None:
        self.__wait()
        element_username = self.__driver.find_element("name", "username")
        self.__wait()
        element_password = self.__driver.find_element("name", "password")
        self.__wait()

        self.__net_wait_random(max_wait_seconds=1)
        element_username.send_keys(self.__config.username)
        self.__net_wait_random(max_wait_seconds=1)
        element_password.send_keys(self.__config.password)
        self.__driver.implicitly_wait(1)
        
        element_login = self.__driver.find_element("xpath", "/html/body/div[2]/div/div/div[2]/div/div/div[1]/section/main/article/div[2]/div[1]/div[2]/form/div/div[3]/button")
        self.__wait()
        self.__net_wait_random(max_wait_seconds=1)
        element_login.click()
        self.__wait()

    def __waiting_key(
        self
        ) -> None:
        # TODO: get key of 2 authenticator
        input("waiting input key: (enter any way)")
        
    def __profile(
        self
        ) -> None:
        self.__driver.get(f"{self.__link}/{self.__config.looking_username}")
        self.__wait()

    def __scrollDown(
        self
        ) -> None:
        self.__net_wait_random(2, 4)
        jsCode = """
        page = document.querySelector("._aano");
        page.scrollTo(0, page.scrollHeight);
        var last_height = page.scrollHeight;
        return last_height 
        """
        last_height = self.__driver.execute_script(jsCode)
        while True:
            new_height = last_height
            self.__net_wait_random(2, 3)
            self.__wait()
            last_height = self.__driver.execute_script(jsCode)
            if new_height == last_height:
                break
    
    def __getUsers(
        self, 
        id
        ) -> set[str]:
        self.__net_wait_random()
        follow_button = self.__driver.find_element("xpath", f"/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/ul/li[{id}]/a")
        follow_button.click()        
        self.__wait()
        self.__scrollDown()
        self.__wait()
        user_set = set()
        self.__net_wait_random()
        user_elements = self.__driver.find_elements_by_class_name("x1rg5ohu")
        for user in user_elements:
            if (not user.text.find(" ") == -1) or user.text == "":
                continue
            user_set.add(user.text.replace("\nDoğrulanmış",""))
        self.__net_wait_random()
        close_button = self.__driver.find_element("xpath", f"/html/body/div[6]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/button")
        close_button.click()                    
        print("getUsers")
        return user_set
        
    def __getFollows(
        self
        ) -> set[str]:
        follows_id = 3
        return self.__getUsers(follows_id)

    def __getFollowers(
        self
        ) -> set[str]:
        followers_id = 2
        return self.__getUsers(followers_id)
        
    def __compare(
        self
        ) -> None:
        self.__insta_info.set_data(self.__getFollowers(), self.__getFollows())
        self.__insta_info.compare_and_save()

    def run(
        self
        ) -> None:
        try:
            self.__login()
            self.__waiting_key()
        except:
            print("key not necessary")
        print("LOGIN")
        self.__net_wait_random()
        self.__saveCookies()
        self.__net_wait_random()
        self.__profile()
        print("PROFILE")
        self.__compare()

    def close(
        self
        ) -> None:
        self.__driver.close()
        


if __name__ == "__main__":
    file_name = "config/config_file.ini"
    insta_link = "https://www.instagram.com"
    
    webScraper = Driver(insta_link, file_name)
    webScraper.run()
    webScraper.close()
    