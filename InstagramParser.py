import csv
import json
from pathlib import Path

from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from instagrapi.types import User

from PostsData import PostsData
from ShortData import ShortData


class InstagramParser:
    def __init__(self, profile_url: str, login: str, password: str):
        self.__cl = Client()
        self.__cl.delay_range = [1, 3]
        self.__login = login
        self.__password = password
        self.__profile_url: str = profile_url
        self.__short_data: ShortData | None = None
        self.__posts_data: list[PostsData] | None = None

    def login_first_time(self):
        """
        Функция для первого логина. Создает сессию в файле для дальнейшей облегченной авторизации
        """
        self.__cl.login(self.__login, self.__password)
        self.__cl.dump_settings(Path("session.json"))  # TODO

    def login(self):
        session = self.__cl.load_settings(Path("session.json"))
        login_via_session = False
        login_via_pw = False

        if session:
            try:
                self.__cl.set_settings(session)
                self.__cl.login(self.__login, self.__password)

                # check if session is valid
                try:
                    self.__cl.get_timeline_feed()
                except LoginRequired:
                    print("Session is invalid, need to login via login and password")

                    old_session = self.__cl.get_settings()

                    # use the same device uuids across logins
                    self.__cl.set_settings({})
                    self.__cl.set_uuids(old_session["uuids"])

                    self.__cl.login(self.__login, self.__password)
                login_via_session = True
            except Exception as e:
                print("Couldn't login user using session information: %s" % e)

        if not login_via_session:
            try:
                print("Attempting to login via login and password. login: %s" % self.__login)
                if self.__cl.login(self.__login, self.__password):
                    login_via_pw = True
            except Exception as e:
                print("Couldn't login user using login and password: %s" % e)

        if not login_via_pw and not login_via_session:
            raise Exception("Couldn't login user with either password or session")

    def get_user_name(self):
        return self.__profile_url.rstrip("/").split("/")[-1]

    @property
    def profile_url(self):
        return self.__profile_url

    @profile_url.setter
    def profile_url(self, profile_url: str):
        self.__profile_url = profile_url

    def parse_short_data(self):
        user_info: User = self.__cl.user_info_by_username(self.get_user_name())
        self.__short_data = ShortData(followers=user_info.follower_count, posts=user_info.media_count)

    def parse_posts_data(self, amount: int = 30):
        user_id = self.__cl.user_id_from_username(self.get_user_name())
        posts_info = self.__cl.user_medias(user_id, amount)
        self.__posts_data = [
            PostsData(
                post.caption_text,
                post.like_count,
                post.comment_count,
                post.taken_at
            )
            for post in posts_info
        ]

    def get_short_data(self):
        return json.dumps(self.__short_data.__dict__, indent=4)

    def write_to_csv(self):
        if not self.__posts_data:
            print("Posts list is empty")
            return
        headers = [header for header in self.__posts_data[0].__dict__.keys()]
        with open('done.csv', mode='w', encoding='utf-8') as file:
            file_writer = csv.DictWriter(file, delimiter=';', lineterminator='\r', fieldnames=headers)
            file_writer.writeheader()
            file_writer.writerows([row.__dict__ for row in self.__posts_data])
