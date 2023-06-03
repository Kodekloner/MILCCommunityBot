import pandas as pd
import os
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.errorhandler import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

from config.db import sqlite_conn

from time import sleep


class Scrapetwitter(webdriver.Chrome):
    def __init__(self, driver_path=r"C:\SeleniumDrivers", teardown=False):
        self.driver_path = driver_path
        self.teardown = teardown
        os.environ['PATH'] += self.driver_path
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('detach', True)
        self.url = "https://twitter.com/i/flow/login"
        super(Scrapetwitter, self).__init__(options=options)
        self.maximize_window()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    def login(self):
        self.get(self.url)

        # Setup the log in
        wait = WebDriverWait(self, 30)
        wait.until(EC.presence_of_element_located((By.XPATH,"//input[@name='text']")))
        username = self.find_element(By.XPATH,"//input[@name='text']")
        username.send_keys("iamericalily")
        next_button = self.find_element(By.XPATH,"//span[contains(text(),'Next')]")
        next_button.click()

        wait = WebDriverWait(self, 30)
        wait.until(EC.presence_of_element_located((By.XPATH,"//input[@name='password']")))
        password = self.find_element(By.XPATH,"//input[@name='password']")
        password.send_keys('10032006')
        log_in = self.find_element(By.XPATH,"//span[contains(text(),'Log in')]")
        log_in.click()

        try:
            wait = WebDriverWait(self, 5)
            wait.until(EC.visibility_of_element_located((By.XPATH,"//span[contains(text(),'Skip for now')]")))
            skip_for_now = self.find_elements(By.XPATH,"//span[contains(text(),'Skip for now')]")
            skip_for_now.click()
        except TimeoutException:
            print("No Element. Skipping...")

    def competition_search(self, time):
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM TwitterSearch")

        result = cursor.fetchone()

        if result:
            # Search item and fetch it
            subject = f"({result['word']} lang:en  since:{time})"
            # Continue processing with the fetched result

            wait = WebDriverWait(self, 60)
            wait.until(EC.presence_of_element_located((By.XPATH,"//input[@data-testid='SearchBox_Search_Input']")))
            search_box = self.find_element(By.XPATH,"//input[@data-testid='SearchBox_Search_Input']")
            search_box.send_keys(subject)
            search_box.send_keys(Keys.ENTER)

            wait = WebDriverWait(self, 30)
            wait.until(EC.presence_of_element_located((By.XPATH,"//span[contains(text(),'Latest')]")))
            latest = self.find_element(By.XPATH,"//span[contains(text(),'Latest')]")
            latest.click()
        else:
            print("Search error")

    def search(self):
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM TwitterSearch")

        result = cursor.fetchone()

        if result:
            # Search item and fetch it
            subject = f"({result['word']} lang:en  since:{result['time']})"
            # Continue processing with the fetched result

            wait = WebDriverWait(self, 60)
            wait.until(EC.presence_of_element_located((By.XPATH,"//input[@data-testid='SearchBox_Search_Input']")))
            search_box = self.find_element(By.XPATH,"//input[@data-testid='SearchBox_Search_Input']")
            search_box.send_keys(subject)
            search_box.send_keys(Keys.ENTER)

            wait = WebDriverWait(self, 30)
            wait.until(EC.presence_of_element_located((By.XPATH,"//span[contains(text(),'Latest')]")))
            latest = self.find_element(By.XPATH,"//span[contains(text(),'Latest')]")
            latest.click()
        else:
            print("Search error")

    def get_tweets(self):

        tweets = []
        # videos = []
        images = []

        wait = WebDriverWait(self, 60)
        wait.until(EC.visibility_of_element_located((By.XPATH,"//article[@data-testid='tweet']")))
        articles = self.find_elements(By.XPATH,"//article[@data-testid='tweet']")

        modal_element = articles[-1]

        for article in articles:
            try:
                try:
                    timestamp = article.find_element(By.XPATH, ".//time")
                except NoSuchElementException:
                    continue

                wait = WebDriverWait(article, 60)
                wait.until(EC.visibility_of_element_located((By.XPATH,".//div[@data-testid='tweetText']")))
                tweet = article.find_element(By.XPATH,".//div[@data-testid='tweetText']").text
                tweets.append(tweet)

                # try:
                #     video = article.find_element(By.XPATH,".//video[@preload='none']")
                #     video = video.get_attribute('src')
                #     videos.append(video)
                # except NoSuchElementException:
                #     video = ""
                #     videos.append(video)

                try:
                    img = article.find_element(By.XPATH,".//img[@alt='Image']").get_attribute("src")
                    images.append(img)
                except NoSuchElementException:
                    img = ""
                    images.append(img)

            except StaleElementReferenceException:
                continue

        counter = 0
        height = self.execute_script("return arguments[0].scrollHeight;", modal_element)
        while True:
            if counter > 10 :
                break
            self.execute_script("arguments[0].scrollIntoView(true);", modal_element)
            wait = WebDriverWait(self, 60)
            wait.until(EC.visibility_of_element_located((By.XPATH,"//article[@data-testid='tweet']")))
            sleep(2)
            articles = self.find_elements(By.XPATH,"//article[@data-testid='tweet']")
            modal_element = articles[-1]
            new_height = self.execute_script("return arguments[0].scrollHeight;", modal_element)
            if height == new_height:
                break
            height = new_height
            counter += 1

            for article in articles:
                try:
                    try:
                        timestamp = article.find_element(By.XPATH, ".//time")
                    except NoSuchElementException:
                        continue

                    wait = WebDriverWait(article, 60)
                    wait.until(EC.visibility_of_element_located((By.XPATH,".//div[@data-testid='tweetText']")))
                    tweet = article.find_element(By.XPATH,".//div[@data-testid='tweetText']").text
                    tweets.append(tweet)

                    # try:
                    #     video = article.find_element(By.XPATH,".//video[@preload='none']")
                    #     video = video.get_attribute('src')
                    #     videos.append(video)
                    # except NoSuchElementException:
                    #     video = ""
                    #     videos.append(video)

                    try:
                        img = article.find_element(By.XPATH,".//img[@alt='Image']").get_attribute("src")
                        images.append(img)
                    except NoSuchElementException:
                        img = ""
                        images.append(img)

                except StaleElementReferenceException:
                    continue

        unique_tweets = []
        cursor = sqlite_conn.cursor()

        for i in range(len(tweets)):
            if tweets[i] not in unique_tweets:
                cursor.execute(
                    """INSERT INTO tweets (tweets, images, sent) VALUES (?, ?, ?)""",
                    (
                        tweets[i],
                        # videos[i],
                        images[i],
                        False,
                    ),
                )
                unique_tweets.append(tweets[i])
            else:
                continue

        # Update the timestamp to the current time
        current_time = datetime.now()
        formatted_time = current_time.strftime('%Y-%m-%d')

        # Update the 'sent' value to True
        cursor.execute("UPDATE TwitterSearch SET time=? WHERE id=?", (formatted_time, 1))

        # Commit the changes
        sqlite_conn.commit()

        # Close the database connection
        sqlite_conn.close()

        self.quit()

    def user_replies(self):

        user_tags = []
        processed_indices = set()
        try:
            wait = WebDriverWait(self, 60)
            wait.until(EC.visibility_of_element_located((By.XPATH,"//article[@data-testid='tweet']")))
            outside_articles = self.find_elements(By.XPATH,"//article[@data-testid='tweet']")

            print(f"first lenth before loop = {len(outside_articles)} \n")

            for i in range(len(outside_articles)):
                try:
                    print(f"index: {i}")
                    wait = WebDriverWait(self, 10)
                    wait.until(EC.visibility_of_element_located((By.XPATH, "//article[@data-testid='tweet']")))

                    articles = self.find_elements(By.XPATH, "//article[@data-testid='tweet']")

                    no_articles = len(articles)
                    print(f"no_articles: {no_articles}")

                    if i >= no_articles:
                        break

                    tweet = articles[i].find_element(By.XPATH,".//div[@data-testid='tweetText']").text

                    if tweet in processed_indices:
                        continue

                    processed_indices.add(tweet)

                    wait = WebDriverWait(articles[i], 10)
                    wait.until(EC.visibility_of_element_located((By.XPATH, ".//div[@data-testid='User-Name']")))
                    tweet_user_name = articles[i].find_element(By.XPATH, ".//div[@data-testid='User-Name']").text
                    lines = tweet_user_name.split("\n")
                    tweet_user_name = " ".join(lines[:2]).strip()

                    try:
                        show_thread = articles[i].find_element(By.XPATH, ".//a[time]")
                        self.execute_script("arguments[0].scrollIntoView(true);", show_thread)
                        self.execute_script("arguments[0].click();", show_thread)
                    except NoSuchElementException:
                        continue

                    wait = WebDriverWait(self, 10)
                    wait.until(EC.visibility_of_element_located((By.XPATH," //article[@data-testid='tweet']")))
                    replies = self.find_elements(By.XPATH, "//article[@data-testid='tweet']")

                    for reply in replies:
                        wait = WebDriverWait(reply, 10)
                        wait.until(EC.visibility_of_element_located((By.XPATH, ".//div[@data-testid='User-Name']")))
                        user_tag = reply.find_element(By.XPATH, ".//div[@data-testid='User-Name']").text
                        lines = user_tag.split("\n")
                        user_tag = " ".join(lines[:2]).strip()
                        if user_tag == tweet_user_name:
                            continue
                        print(user_tag)
                        user_tags.append(user_tag)

                    counter = 0
                    height = self.execute_script("return document.documentElement.scrollHeight")
                    while True:
                        if counter > 10 :
                            back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-back']")
                            back.click()
                            sleep(1)
                            break
                        self.execute_script("window.scrollTo(0,document.documentElement.scrollHeight)")
                        sleep(1)
                        new_height = self.execute_script("return document.documentElement.scrollHeight")
                        if height == new_height:
                            try:
                                show_more_replies = self.find_element(By.XPATH, "//span[normalize-space()='Show more replies']")
                                self.execute_script("arguments[0].scrollIntoView(true);", show_more_replies)
                                self.execute_script("arguments[0].click();", show_more_replies)
                            except NoSuchElementException:
                                back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-back']")
                                back.click()
                                sleep(1)
                                break
                        height = new_height
                        counter += 1

                        wait = WebDriverWait(self, 10)
                        wait.until(EC.visibility_of_element_located((By.XPATH,"//article[@data-testid='tweet']")))
                        replies = self.find_elements(By.XPATH,"//article[@data-testid='tweet']")

                        for reply in replies:
                            wait = WebDriverWait(reply, 10)
                            wait.until(EC.visibility_of_element_located((By.XPATH,".//div[@data-testid='User-Name']")))
                            user_tag = reply.find_element(By.XPATH,".//div[@data-testid='User-Name']").text
                            lines = user_tag.split("\n")
                            user_tag = " ".join(lines[:2]).strip()
                            if user_tag == tweet_user_name:
                                continue
                            print(user_tag)
                            user_tags.append(user_tag)
                except NoSuchElementException:
                    continue

            wait = WebDriverWait(self, 10)
            wait.until(EC.visibility_of_element_located((By.XPATH,"//article[@data-testid='tweet']")))
            outside_articles = self.find_elements(By.XPATH,"//article[@data-testid='tweet']")
            modal_element = outside_articles[-1]

            articles_counter = 0
            articles_height = self.execute_script("return arguments[0].scrollHeight;", modal_element)
            print(f"articles_height: {articles_height}")
            broken = False
            while True:
                if articles_counter > 20 :
                    break
                if broken == True:
                    wait = WebDriverWait(self, 10)
                    wait.until(EC.visibility_of_element_located((By.XPATH,"//article[@data-testid='tweet']")))
                    outside_articles = self.find_elements(By.XPATH,"//article[@data-testid='tweet']")
                    modal_element = outside_articles[-1]
                    articles_height = self.execute_script("return arguments[0].scrollHeight;", modal_element)
                    self.execute_script("arguments[0].scrollIntoView(true);", modal_element)
                else:
                    self.execute_script("arguments[0].scrollIntoView(true);", modal_element)

                wait = WebDriverWait(self, 10)
                wait.until(EC.visibility_of_element_located((By.XPATH,"//article[@data-testid='tweet']")))
                sleep(2)
                outside_articles = self.find_elements(By.XPATH,"//article[@data-testid='tweet']")
                modal_element = outside_articles[-1]
                articles_new_height = self.execute_script("return arguments[0].scrollHeight;", modal_element)
                print(f"articles_height: {articles_height}")
                print(f"articles_new_height: {articles_new_height}")
                if articles_height == articles_new_height:
                    break

                articles_height = articles_new_height
                articles_counter += 1

                print(f"first lenth after scroll, before loop = {len(outside_articles)} \n")
                for j in range(len(outside_articles)):
                    try:
                        print(f"index: {j}")
                        wait = WebDriverWait(self, 10)
                        wait.until(EC.visibility_of_element_located((By.XPATH, "//article[@data-testid='tweet']")))

                        articles = self.find_elements(By.XPATH, "//article[@data-testid='tweet']")

                        no_articles = len(articles)
                        print("------------------------------\n " + str(len(articles)) + " inside articles \n------------------------------")

                        if j >= no_articles:
                            broken = True
                            break

                        tweet = articles[j].find_element(By.XPATH,".//div[@data-testid='tweetText']").text

                        if tweet in processed_indices:
                            continue

                        processed_indices.add(tweet)

                        wait = WebDriverWait(articles[j], 10)
                        wait.until(EC.visibility_of_element_located((By.XPATH, ".//div[@data-testid='User-Name']")))
                        tweet_user_name = articles[j].find_element(By.XPATH, ".//div[@data-testid='User-Name']").text
                        lines = tweet_user_name.split("\n")
                        tweet_user_name = " ".join(lines[:2]).strip()

                        try:
                            show_thread = articles[j].find_element(By.XPATH, ".//a[time]")
                            self.execute_script("arguments[0].scrollIntoView(true);", show_thread)
                            self.execute_script("arguments[0].click();", show_thread)
                        except NoSuchElementException:
                            continue

                        wait = WebDriverWait(self, 10)
                        wait.until(EC.visibility_of_element_located((By.XPATH, "//article[@data-testid='tweet']")))
                        replies = self.find_elements(By.XPATH, "//article[@data-testid='tweet']")

                        for reply in replies:
                            wait = WebDriverWait(reply, 10)
                            wait.until(EC.visibility_of_element_located((By.XPATH,".//div[@data-testid='User-Name']")))
                            user_tag = reply.find_element(By.XPATH,".//div[@data-testid='User-Name']").text
                            lines = user_tag.split("\n")
                            user_tag = " ".join(lines[:2]).strip()
                            if user_tag == tweet_user_name:
                                continue
                            print(user_tag)
                            user_tags.append(user_tag)

                        counter = 0
                        height = self.execute_script("return document.documentElement.scrollHeight")
                        while True:
                            if counter > 10 :
                                back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-back']")
                                back.click()
                                sleep(2)
                                break
                            self.execute_script("window.scrollTo(0,document.documentElement.scrollHeight)")
                            sleep(2)
                            new_height = self.execute_script("return document.documentElement.scrollHeight")
                            if height == new_height:
                                try:
                                    show_more_replies = self.find_element(By.XPATH, "//span[normalize-space()='Show more replies']")
                                    self.execute_script("arguments[0].scrollIntoView(true);", show_more_replies)
                                    self.execute_script("arguments[0].click();", show_more_replies)
                                except NoSuchElementException:
                                    back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-back']")
                                    back.click()
                                    sleep(2)
                                    break
                            height = new_height
                            counter += 1

                            wait = WebDriverWait(self, 10)
                            wait.until(EC.visibility_of_element_located((By.XPATH,"//article[@data-testid='tweet']")))
                            replies = self.find_elements(By.XPATH,"//article[@data-testid='tweet']")

                            print("------------------------------\n" + str(len(replies)) + "tweet was successfully scraped \n------------------------------")
                            for reply in replies:
                                wait = WebDriverWait(reply, 10)
                                wait.until(EC.visibility_of_element_located((By.XPATH,".//div[@data-testid='User-Name']")))
                                user_tag = reply.find_element(By.XPATH,".//div[@data-testid='User-Name']").text
                                lines = user_tag.split("\n")
                                user_tag = " ".join(lines[:2]).strip()
                                if user_tag == tweet_user_name:
                                    continue
                                print(user_tag)
                                user_tags.append(user_tag)
                    except NoSuchElementException:
                        continue

            user_replies_counts = {}
            for username in user_tags:
                if username in user_replies_counts:
                    user_replies_counts[username] += 1
                else:
                    user_replies_counts[username] = 1

            return user_replies_counts
        except TimeoutException:
            return None

        self.quit()

    def user_retweets(self):

        user_tags = []
        retweets_processed_indices = set()
        try:
            wait = WebDriverWait(self, 60)
            wait.until(EC.visibility_of_element_located((By.XPATH,"//article[@data-testid='tweet']")))
            outside_articles = self.find_elements(By.XPATH,"//article[@data-testid='tweet']")

            print(f"first lenth before loop = {len(outside_articles)} \n")

            for i in range(len(outside_articles)):
                try:
                    wait = WebDriverWait(self, 10)
                    wait.until(EC.visibility_of_element_located((By.XPATH, "//article[@data-testid='tweet']")))

                    articles = self.find_elements(By.XPATH, "//article[@data-testid='tweet']")

                    no_articles = len(articles)

                    print(f"inside loop lenght = {no_articles} \n")
                    print(f"index = {i}\n")

                    if i >= no_articles:
                        break

                    tweet = articles[i].find_element(By.XPATH,".//div[@data-testid='tweetText']").text

                    if tweet in retweets_processed_indices:
                        continue

                    retweets_processed_indices.add(tweet)

                    try:
                        show_thread = articles[i].find_element(By.XPATH, ".//a[time]")
                        # self.execute_script("arguments[0].scrollIntoView(true);", show_thread)
                        self.execute_script("arguments[0].click();", show_thread)
                    except NoSuchElementException:
                        continue

                    try:
                        wait = WebDriverWait(self, 2)
                        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'Retweet')]")))
                        retweet_btn = self.find_element(By.XPATH, "//*[contains(text(),'Retweet')]")
                        self.execute_script("arguments[0].scrollIntoView(true);", retweet_btn)
                        self.execute_script("arguments[0].click();", retweet_btn)
                        # retweet_btn.click()
                    except TimeoutException:
                        try:
                            wait = WebDriverWait(self, 2)
                            wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'Retweets')]")))
                            retweets_btn = self.find_element(By.XPATH, "//*[contains(text(),'Retweets')]")
                            self.execute_script("arguments[0].scrollIntoView(true);", retweets_btn)
                            self.execute_script("arguments[0].click();", retweets_btn)
                            # retweets_btn.click()
                        except TimeoutException:
                            back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-back']")
                            back.click()
                            sleep(1)
                            continue

                    wait = WebDriverWait(self, 10)
                    wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@data-viewportview='true']")))
                    viewportview = self.find_element(By.XPATH, "//div[@data-viewportview='true']")

                    try:
                        wait = WebDriverWait(viewportview, 10)
                        wait.until(EC.visibility_of_element_located((By.XPATH, ".//div[@data-testid='UserCell']")))
                        retweets = viewportview.find_elements(By.XPATH, ".//div[@data-testid='UserCell']")
                    except TimeoutException:
                        back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-close']")
                        back.click()
                        sleep(1)
                        back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-back']")
                        back.click()
                        sleep(2)
                        continue

                    modal_element = retweets[-1]

                    for retweet in retweets:
                        # wait = WebDriverWait(retweet, 10)
                        # wait.until(EC.visibility_of_element_located((By.XPATH, ".//div[@class='css-1dbjc4n r-1wbh5a2 r-dnmrzs r-1ny4l3l']")))
                        user_tag = retweet.find_element(By.XPATH, ".//div[@class='css-1dbjc4n r-1wbh5a2 r-dnmrzs r-1ny4l3l']").text
                        print("------------------------------\n" + user_tag + " tweet was successfully scraped \n------------------------------")
                        user_tags.append(user_tag)

                    counter = 0
                    height = self.execute_script("return arguments[0].scrollHeight;", modal_element)
                    while True:
                        if counter > 20 :
                            back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-close']")
                            back.click()
                            sleep(1)
                            back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-back']")
                            back.click()
                            sleep(2)
                            break
                        self.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", modal_element)
                        sleep(3)
                        new_height = self.execute_script("return arguments[0].scrollHeight;", modal_element)
                        if height == new_height:
                            back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-close']")
                            back.click()
                            sleep(1)
                            back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-back']")
                            back.click()
                            sleep(2)
                            break
                        height = new_height
                        counter += 1
                        viewportview = self.find_element(By.XPATH, "//div[@data-viewportview='true']")
                        retweets = viewportview.find_elements(By.XPATH, ".//div[@data-testid='UserCell']")
                        for retweet in retweets:
                            # wait = WebDriverWait(retweet, 10)
                            # wait.until(EC.visibility_of_element_located((By.XPATH, ".//div[@class='css-1dbjc4n r-1wbh5a2 r-dnmrzs r-1ny4l3l']")))
                            user_tag = retweet.find_element(By.XPATH, ".//div[@class='css-1dbjc4n r-1wbh5a2 r-dnmrzs r-1ny4l3l']").text
                            print("------------------------------\n" + user_tag + " tweet was successfully scraped \n------------------------------")
                            user_tags.append(user_tag)
                except NoSuchElementException:
                    continue

            wait = WebDriverWait(self, 10)
            wait.until(EC.visibility_of_element_located((By.XPATH,"//article[@data-testid='tweet']")))
            outside_articles = self.find_elements(By.XPATH,"//article[@data-testid='tweet']")
            last = outside_articles[-1]

            articles_counter = 0
            articles_height = self.execute_script("return arguments[0].scrollHeight;", last)
            print(f"articles_height = {articles_height}")
            broken = False
            while True:
                if articles_counter > 10 :
                    break

                if broken == True:
                    wait = WebDriverWait(self, 10)
                    wait.until(EC.visibility_of_element_located((By.XPATH,"//article[@data-testid='tweet']")))
                    outside_articles = self.find_elements(By.XPATH,"//article[@data-testid='tweet']")
                    last = outside_articles[-1]
                    articles_height = self.execute_script("return arguments[0].scrollHeight;", last)
                    self.execute_script("arguments[0].scrollIntoView(true);", last)
                else:
                    self.execute_script("arguments[0].scrollIntoView(true);", last)

                wait = WebDriverWait(self, 10)
                wait.until(EC.visibility_of_element_located((By.XPATH,"//article[@data-testid='tweet']")))
                sleep(2)
                outside_articles = self.find_elements(By.XPATH,"//article[@data-testid='tweet']")
                modal_element = outside_articles[-1]
                articles_new_height = self.execute_script("return arguments[0].scrollHeight;", modal_element)
                print(f"articles_height: {articles_height}")
                print(f"articles_new_height: {articles_new_height}")

                if articles_height == articles_new_height:
                    break

                articles_height = articles_new_height
                articles_counter += 1

                print(f"first lenth before loop = {len(outside_articles)} \n")

                for i in range(len(outside_articles)):
                    try:
                        wait = WebDriverWait(self, 10)
                        wait.until(EC.visibility_of_element_located((By.XPATH, "//article[@data-testid='tweet']")))

                        articles = self.find_elements(By.XPATH, "//article[@data-testid='tweet']")

                        no_articles = len(articles)

                        print(f"inside loop lenght = {no_articles} \n")
                        print(f"index = {i}\n")

                        if i >= no_articles:
                            broken = True
                            break

                        tweet = articles[i].find_element(By.XPATH,".//div[@data-testid='tweetText']").text

                        if tweet in retweets_processed_indices:
                            continue

                        retweets_processed_indices.add(tweet)

                        try:
                            show_thread = articles[i].find_element(By.XPATH, ".//a[time]")
                            # self.execute_script("arguments[0].scrollIntoView(true);", show_thread)
                            self.execute_script("arguments[0].click();", show_thread)
                        except NoSuchElementException:
                            continue

                        try:
                            wait = WebDriverWait(self, 2)
                            wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'Retweet')]")))
                            retweet_btn = self.find_element(By.XPATH, "//*[contains(text(),'Retweet')]")
                            self.execute_script("arguments[0].scrollIntoView(true);", retweet_btn)
                            self.execute_script("arguments[0].click();", retweet_btn)
                            # retweet_btn.click()
                        except TimeoutException:
                            try:
                                wait = WebDriverWait(self, 2)
                                wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'Retweets')]")))
                                retweets_btn = self.find_element(By.XPATH, "//*[contains(text(),'Retweets')]")
                                self.execute_script("arguments[0].scrollIntoView(true);", retweets_btn)
                                self.execute_script("arguments[0].click();", retweets_btn)
                                # retweets_btn.click()
                            except TimeoutException:
                                back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-back']")
                                back.click()
                                sleep(1)
                                continue

                        wait = WebDriverWait(self, 10)
                        wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@data-viewportview='true']")))
                        viewportview = self.find_element(By.XPATH, "//div[@data-viewportview='true']")

                        try:
                            wait = WebDriverWait(viewportview, 10)
                            wait.until(EC.visibility_of_element_located((By.XPATH, ".//div[@data-testid='UserCell']")))
                            retweets = viewportview.find_elements(By.XPATH, ".//div[@data-testid='UserCell']")
                        except TimeoutException:
                            back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-close']")
                            back.click()
                            sleep(1)
                            back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-back']")
                            back.click()
                            sleep(2)
                            continue

                        modal_element = retweets[-1]

                        for retweet in retweets:
                            # wait = WebDriverWait(retweet, 10)
                            # wait.until(EC.visibility_of_element_located((By.XPATH, ".//div[@class='css-1dbjc4n r-1wbh5a2 r-dnmrzs r-1ny4l3l']")))
                            user_tag = retweet.find_element(By.XPATH, ".//div[@class='css-1dbjc4n r-1wbh5a2 r-dnmrzs r-1ny4l3l']").text
                            print("------------------------------\n" + user_tag + " tweet was successfully scraped \n------------------------------")
                            user_tags.append(user_tag)

                        counter = 0
                        height = self.execute_script("return arguments[0].scrollHeight;", modal_element)
                        while True:
                            if counter > 20 :
                                back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-close']")
                                back.click()
                                sleep(1)
                                back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-back']")
                                back.click()
                                sleep(2)
                                break
                            self.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", modal_element)
                            sleep(3)
                            new_height = self.execute_script("return arguments[0].scrollHeight;", modal_element)
                            if height == new_height:
                                back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-close']")
                                back.click()
                                sleep(1)
                                back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-back']")
                                back.click()
                                sleep(2)
                                break
                            height = new_height
                            counter += 1
                            viewportview = self.find_element(By.XPATH, "//div[@data-viewportview='true']")
                            retweets = viewportview.find_elements(By.XPATH, ".//div[@data-testid='UserCell']")
                            for retweet in retweets:
                                # wait = WebDriverWait(retweet, 10)
                                # wait.until(EC.visibility_of_element_located((By.XPATH, ".//div[@class='css-1dbjc4n r-1wbh5a2 r-dnmrzs r-1ny4l3l']")))
                                user_tag = retweet.find_element(By.XPATH, ".//div[@class='css-1dbjc4n r-1wbh5a2 r-dnmrzs r-1ny4l3l']").text
                                print("------------------------------\n" + user_tag + " tweet was successfully scraped \n------------------------------")
                                user_tags.append(user_tag)
                    except NoSuchElementException:
                        continue

                broken = True

            user_retweets_counts = {}
            for username in user_tags:
                if username in user_retweets_counts:
                    user_retweets_counts[username] += 1
                else:
                    user_retweets_counts[username] = 1

            return user_retweets_counts

        except TimeoutException:
            return None

        self.quit()

        self.quit()

    def user_likes(self):

        user_tags = []
        likes_processed_indices = set()
        try:
            wait = WebDriverWait(self, 60)
            wait.until(EC.visibility_of_element_located((By.XPATH,"//article[@data-testid='tweet']")))
            outside_articles = self.find_elements(By.XPATH,"//article[@data-testid='tweet']")

            print(f"first lenth before loop = {len(outside_articles)} \n")

            for i in range(len(outside_articles)):
                try:
                    wait = WebDriverWait(self, 10)
                    wait.until(EC.visibility_of_element_located((By.XPATH, "//article[@data-testid='tweet']")))

                    articles = self.find_elements(By.XPATH, "//article[@data-testid='tweet']")

                    no_articles = len(articles)

                    print(f"inside loop lenght = {no_articles} \n")
                    print(f"index = {i}\n")

                    if i >= no_articles:
                        break

                    tweet = articles[i].find_element(By.XPATH,".//div[@data-testid='tweetText']").text

                    if tweet in likes_processed_indices:
                        continue

                    likes_processed_indices.add(tweet)

                    try:
                        show_thread = articles[i].find_element(By.XPATH, ".//a[time]")
                        # self.execute_script("arguments[0].scrollIntoView(true);", show_thread)
                        self.execute_script("arguments[0].click();", show_thread)
                    except NoSuchElementException:
                        continue

                    try:
                        wait = WebDriverWait(self, 2)
                        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'Like')]")))
                        like_btn = self.find_element(By.XPATH, "//*[contains(text(),'Like')]")
                        self.execute_script("arguments[0].click();", like_btn)
                        # retweet_btn.click()
                    except TimeoutException:
                        try:
                            wait = WebDriverWait(self, 2)
                            wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'Likes')]")))
                            likes_btn = self.find_element(By.XPATH, "//*[contains(text(),'Likes')]")
                            self.execute_script("arguments[0].click();", likes_btn)
                            # retweets_btn.click()
                        except TimeoutException:
                            back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-back']")
                            back.click()
                            sleep(1)
                            continue

                    wait = WebDriverWait(self, 10)
                    wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@data-viewportview='true']")))
                    viewportview = self.find_element(By.XPATH, "//div[@data-viewportview='true']")

                    try:
                        wait = WebDriverWait(viewportview, 10)
                        wait.until(EC.visibility_of_element_located((By.XPATH, ".//div[@data-testid='UserCell']")))
                        users_likes = viewportview.find_elements(By.XPATH, ".//div[@data-testid='UserCell']")
                    except TimeoutException:
                        back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-close']")
                        back.click()
                        sleep(1)
                        back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-back']")
                        back.click()
                        sleep(2)
                        continue

                    modal_element = users_likes[-1]

                    for users_like in users_likes:
                        # wait = WebDriverWait(retweet, 10)
                        # wait.until(EC.visibility_of_element_located((By.XPATH, ".//div[@class='css-1dbjc4n r-1wbh5a2 r-dnmrzs r-1ny4l3l']")))
                        user_tag = users_like.find_element(By.XPATH, ".//div[@class='css-1dbjc4n r-1wbh5a2 r-dnmrzs r-1ny4l3l']").text
                        print("------------------------------\n" + user_tag + " tweet was successfully scraped \n------------------------------")
                        user_tags.append(user_tag)

                    counter = 0
                    height = self.execute_script("return arguments[0].scrollHeight;", modal_element)
                    print(f"height {height}")
                    while True:
                        if counter > 20 :
                            back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-close']")
                            back.click()
                            sleep(1)
                            back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-back']")
                            back.click()
                            sleep(2)
                            break
                        self.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", modal_element)
                        sleep(3)
                        viewportview = self.find_element(By.XPATH, "//div[@data-viewportview='true']")
                        users_likes = viewportview.find_elements(By.XPATH, ".//div[@data-testid='UserCell']")
                        modal_element = users_likes[-1]
                        new_height = self.execute_script("return arguments[0].scrollHeight;", modal_element)
                        print(f"new height {new_height}")
                        if height == new_height:
                            back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-close']")
                            back.click()
                            sleep(1)
                            back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-back']")
                            back.click()
                            sleep(2)
                            break
                        height = new_height
                        counter += 1
                        for users_like in users_likes:
                            # wait = WebDriverWait(retweet, 10)
                            # wait.until(EC.visibility_of_element_located((By.XPATH, ".//div[@class='css-1dbjc4n r-1wbh5a2 r-dnmrzs r-1ny4l3l']")))
                            user_tag = users_like.find_element(By.XPATH, ".//div[@class='css-1dbjc4n r-1wbh5a2 r-dnmrzs r-1ny4l3l']").text
                            print("------------------------------\n" + user_tag + " tweet was successfully scraped \n------------------------------")
                            user_tags.append(user_tag)
                except NoSuchElementException:
                    continue

            wait = WebDriverWait(self, 10)
            wait.until(EC.visibility_of_element_located((By.XPATH,"//article[@data-testid='tweet']")))
            outside_articles = self.find_elements(By.XPATH,"//article[@data-testid='tweet']")
            last = outside_articles[-1]

            articles_counter = 0
            articles_height = self.execute_script("return arguments[0].scrollHeight;", last)
            broken = False
            print(f"articles_height = {articles_height}")
            while True:
                if articles_counter > 10 :
                    break

                if broken == True:
                    wait = WebDriverWait(self, 10)
                    wait.until(EC.visibility_of_element_located((By.XPATH,"//article[@data-testid='tweet']")))
                    outside_articles = self.find_elements(By.XPATH,"//article[@data-testid='tweet']")
                    last = outside_articles[-1]
                    articles_height = self.execute_script("return arguments[0].scrollHeight;", last)
                    self.execute_script("arguments[0].scrollIntoView(true);", last)
                else:
                    self.execute_script("arguments[0].scrollIntoView(true);", last)

                wait = WebDriverWait(self, 10)
                wait.until(EC.visibility_of_element_located((By.XPATH,"//article[@data-testid='tweet']")))
                sleep(2)
                outside_articles = self.find_elements(By.XPATH,"//article[@data-testid='tweet']")
                last = outside_articles[-1]
                articles_new_height = self.execute_script("return arguments[0].scrollHeight;", last)
                print(f"articles_height: {articles_height}")
                print(f"articles_new_height: {articles_new_height}")

                if articles_height == articles_new_height:
                    break

                articles_height = articles_new_height
                articles_counter += 1

                print(f"first lenth before loop = {len(outside_articles)} \n")

                for i in range(len(outside_articles)):
                    try:
                        wait = WebDriverWait(self, 10)
                        wait.until(EC.visibility_of_element_located((By.XPATH, "//article[@data-testid='tweet']")))

                        articles = self.find_elements(By.XPATH, "//article[@data-testid='tweet']")

                        no_articles = len(articles)

                        print(f"inside loop lenght = {no_articles} \n")
                        print(f"index = {i}\n")

                        if i >= no_articles:
                            Broken = True
                            break

                        tweet = articles[i].find_element(By.XPATH,".//div[@data-testid='tweetText']").text

                        if tweet in likes_processed_indices:
                            continue

                        likes_processed_indices.add(tweet)

                        try:
                            show_thread = articles[i].find_element(By.XPATH, ".//a[time]")
                            self.execute_script("arguments[0].click();", show_thread)
                        except NoSuchElementException:
                            continue

                        try:
                            wait = WebDriverWait(self, 2)
                            wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'Like')]")))
                            like_btn = self.find_element(By.XPATH, "//*[contains(text(),'Like')]")
                            self.execute_script("arguments[0].click();", like_btn)
                        except TimeoutException:
                            try:
                                wait = WebDriverWait(self, 2)
                                wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'Likes')]")))
                                likes_btn = self.find_element(By.XPATH, "//*[contains(text(),'Likes')]")
                                self.execute_script("arguments[0].click();", likes_btn)
                            except TimeoutException:
                                back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-back']")
                                back.click()
                                sleep(1)
                                continue

                        wait = WebDriverWait(self, 10)
                        wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@data-viewportview='true']")))
                        viewportview = self.find_element(By.XPATH, "//div[@data-viewportview='true']")

                        try:
                            wait = WebDriverWait(viewportview, 10)
                            wait.until(EC.visibility_of_element_located((By.XPATH, ".//div[@data-testid='UserCell']")))
                            users_likes = viewportview.find_elements(By.XPATH, ".//div[@data-testid='UserCell']")
                        except TimeoutException:
                            back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-close']")
                            back.click()
                            sleep(1)
                            back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-back']")
                            back.click()
                            sleep(2)
                            continue

                        modal_element = users_likes[-1]

                        for users_like in users_likes:
                            user_tag = users_like.find_element(By.XPATH, ".//div[@class='css-1dbjc4n r-1wbh5a2 r-dnmrzs r-1ny4l3l']").text
                            print("------------------------------\n" + user_tag + " tweet was successfully scraped \n------------------------------")
                            user_tags.append(user_tag)

                        counter = 0
                        height = self.execute_script("return arguments[0].scrollHeight;", modal_element)
                        print(f"height {height}")
                        while True:
                            if counter > 20 :
                                back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-close']")
                                back.click()
                                sleep(1)
                                back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-back']")
                                back.click()
                                sleep(2)
                                break
                            self.execute_script("arguments[0].scrollIntoView(true);", modal_element)
                            sleep(3)
                            viewportview = self.find_element(By.XPATH, "//div[@data-viewportview='true']")
                            users_likes = viewportview.find_elements(By.XPATH, ".//div[@data-testid='UserCell']")
                            modal_element = users_likes[-1]
                            new_height = self.execute_script("return arguments[0].scrollHeight;", modal_element)
                            print(f"new height {new_height}")
                            if height == new_height:
                                back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-close']")
                                back.click()
                                sleep(1)
                                back = self.find_element(By.XPATH, "//div[@data-testid='app-bar-back']")
                                back.click()
                                sleep(2)
                                break
                            height = new_height
                            counter += 1
                            for users_like in users_likes:
                                user_tag = users_like.find_element(By.XPATH, ".//div[@class='css-1dbjc4n r-1wbh5a2 r-dnmrzs r-1ny4l3l']").text
                                print("------------------------------\n" + user_tag + " tweet was successfully scraped \n------------------------------")
                                user_tags.append(user_tag)
                    except NoSuchElementException:
                        continue

                broken = True

            user_likes_counts = {}
            for username in user_tags:
                if username in user_likes_counts:
                    user_likes_counts[username] += 1
                else:
                    user_likes_counts[username] = 1

            return user_likes_counts
        except TimeoutException:
            return None

        self.quit()
