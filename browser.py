import configparser
# from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from msedge.selenium_tools import Edge
from msedge.selenium_tools import EdgeOptions
import pickle
import time
import os

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

    def __init__(
        self,
        looking_username : str
        ) -> None:
        dir = "results"
        self.__path = f"{dir}/insta_{looking_username}.csv"
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.__columns = ["FOLLOWERS", "FOLLOWS", "UNFOLLOW", "NEW_FOLLOWERS", "NEW_FOLLOWS", "NEW_UNFOLLOW"]
        if not self.__read_df():
            self.__create_df()
            
    def __read_df(
        self
        ) -> bool:
        try:
            self.__insta_df = pd.read_csv(self.__path, sep=";", columns=self.__columns)
            self.__old_unfollow_set = set(self.__insta_df["UNFOLLOW"])
            self.__old_followers_set = set(self.__insta_df["FOLLOWERS"])
            self.__old_follows_set = set(self.__insta_df["FOLLOWS"])
            return True
        except:
            return False
        
    def __write_df(
        self
        ) -> bool:
        try:
            self.__insta_df.to_csv(self.__path, sep=";", columns=self.__columns, index=False)
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
        
        self.__insta_df["NEW_FOLLOWERS"] = new_followers + (length["MAX"] - length["NEW_FOLLOWERS"]) * [np.nan]
        self.__insta_df["NEW_FOLLOWS"] = new_follows + (length["MAX"] - length["NEW_FOLLOWS"]) * [np.nan]
        self.__insta_df["NEW_UNFOLLOW"] = new_unfollow + (length["MAX"] - length["NEW_UNFOLLOW"]) * [np.nan]
        self.__insta_df["UNFOLLOW"] = unfollow + (length["MAX"] - length["UNFOLLOW"]) * [np.nan]
        self.__insta_df["FOLLOWERS"] = followers + (length["MAX"] - length["FOLLOWERS"]) * [np.nan]
        self.__insta_df["FOLLOWS"] = follows + (length["MAX"] - length["FOLLOWS"]) * [np.nan]

        if not self.__write_df():
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
        file_name :str
        ) -> None:
        self.__link = link
        # self.options = webdriver.ChromeOptions()
        # self.options.add_argument('--headless')
        # self.options.add_argument('--disable-gpu')
        # self.__driver = webdriver.Chrome(chrome_options=self.options)
        self.__setUserInfo(file_name)
        options = EdgeOptions()
        options.add_argument("disable-gpu")
        user_agent = "your-user-agent"
        options.add_argument(f"--user-agent={user_agent}")
        self.__driver = Edge(EdgeChromiumDriverManager().install(), options=options)
        dir = "cookies"
        self.__cookies_name = f"{dir}/{self.__config.username}.pkl"
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.__goWebSite()
        self.__insta_info = InstaInfo(self.__config.looking_username)

    def __setUserInfo(
        self, 
        file_name :str
        ) -> None:
        self.__config = Config(file_name)

    def __goWebSite(
        self
        ) -> None:
        if os.path.isfile(self.__cookies_name):
            cookies = pickle.load(open(self.__cookies_name, "rb"))
            self.__driver.get(self.__link)
            for cookie in cookies:
                self.__driver.add_cookie(cookie)
        else:
            self.__driver.get(self.__link)

    def __login(
        self
        ) -> None:
        self.__driver.implicitly_wait(10)
        element_username = self.__driver.find_element("name", "username")
        self.__driver.implicitly_wait(10)
        element_password = self.__driver.find_element("name", "password")
        self.__driver.implicitly_wait(10)

        element_username.send_keys(self.__config.username)
        element_password.send_keys(self.__config.password)
        self.__driver.implicitly_wait(1)
        
        element_login = self.__driver.find_element("xpath", "/html/body/div[2]/div/div/div[2]/div/div/div[1]/section/main/article/div[2]/div[1]/div[2]/form/div/div[3]/button")
        self.__driver.implicitly_wait(10)
        element_login.click()
        self.__driver.implicitly_wait(10)

        pickle.dump(self.__driver.get_cookies(), open(self.__cookies_name, "wb"))
        print(self.__driver.get_cookies())
        
    def __waiting_key(
        self
        ) -> None:
        # TODO: get key of 2 authenticator
        input("waiting input key: (enter any way)")
        
    def __profile(
        self
        ) -> None:
        self.__driver.get(f"{self.__link}/{self.__config.looking_username}")
        self.__driver.implicitly_wait(10)

    def __scrollDown(
        self
        ) -> None:
        time.sleep(2)
        jsCode = """
        page = document.querySelector("._aano");
        page.scrollTo(0, page.scrollHeight);
        var last_height = page.scrollHeight;
        return last_height 
        """
        last_height = self.__driver.execute_script(jsCode)
        while True:
            new_height = last_height
            time.sleep(2)
            self.__driver.implicitly_wait(10)
            last_height = self.__driver.execute_script(jsCode)
            if new_height == last_height:
                break
    
    def __getUsers(
        self, 
        id
        ) -> set[str]:
        follow_button = self.__driver.find_element("xpath", f"/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/ul/li[{id}]/a")
        follow_button.click()        
        self.__driver.implicitly_wait(10)
        self.__scrollDown()
        self.__driver.implicitly_wait(10)
        user_set = set()
        user_elements = self.__driver.find_elements_by_class_name("x1rg5ohu")
        for user in user_elements:
            if (not user.text.find(" ") == -1) or user.text == "":
                continue
            user_set.add(user.text.replace("\nDoğrulanmış",""))
        close_button = self.__driver.find_element("xpath", f"/html/body/div[6]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/button")
        close_button.click()                    
        return user_set
        
    def __getFollows(
        self
        ) -> list[str]:
        follows_id = 3
        return self.__getUsers(follows_id)

    def __getFollowers(
        self
        ) -> list[str]:                           
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
        self.__login()
        self.__waiting_key()
        self.__profile()
        self.__compare()



if __name__ == "__main__":
    file_name = "config_file.ini"
    insta_link = "https://www.instagram.com"
    
    webScraper = Driver(insta_link, file_name)
    webScraper.run()
    
    