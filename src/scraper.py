# %%
import asyncio
from asyncio.tasks import create_task
import getpass
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
from bs4.element import SoupStrainer, Tag

import utils

# %%
class Scraper:
    ONLY_TABLE = SoupStrainer("table")
    ONLY_MAIN_CONTENT = SoupStrainer("div", {"class": "page-content inset"})
    ONLY_SETTINGS = SoupStrainer("form", attrs={"name": "user_settings"})

    original_settings = {}

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        self._args = args
        self._kwargs = kwargs
        return self

    def __await__(self):
        yield from self._scraper_init(*self._args, **self._kwargs).__await__()
        return self

    async def _scraper_init(
        self,
        client: httpx.AsyncClient = None,
        url: str = None,
        username: str = None,
        password: str = None,
    ) -> None:
        self.url = url if url is not None else "https://whg-duew.de"
        self.client = (
            client
            if client is not None
            else httpx.AsyncClient(
                base_url=self.url, headers={"user-agent": "IServ-exercise-scraper/1.0"}
            )
        )
        logged_in = False
        while not logged_in:
            self.username = username if username is not None else input("Username: ")
            self.password = password if password is not None else getpass.getpass()
            logged_in = await self.login()
            if not logged_in:
                print("Passwort oder Benutzername flasch.")
        print("Erfolgreich eingeloggt!")

    async def login(self) -> bool:
        """
        Log the user in.
        Returns:
            True if login succesful
            False if login failed
        Raises ConnectionError when some error occured
        """
        login_path = "/iserv/app/login"
        login_info = {"_username": self.username, "_password": self.password}
        page_login = await self.client.post(login_path, data=login_info)
        if page_login.url.path.startswith(login_path):
            return False
        elif page_login.status_code != 200 and page_login.status_code != 302:
            await self.close()
            raise ConnectionError("Could not connect to server.")
        else:
            return True

    def href_filter(self, href: str):
        return href.startswith(self.url + "/iserv/exercise/show/")

    def tag_filter(self, tag: Tag) -> bool:
        return (
            tag.name == "a"
            and self.href_filter(tag["href"])
            and "AG 3D-Druck" not in tag.string
        )

    async def change_language(self):
        """
        Change language of user to german to guarantee correct parsing.
        """
        settings_page = await self.client.get("/iserv/profile/settings")
        soup_settings_page = BeautifulSoup(
            settings_page.text, "html.parser", parse_only=self.ONLY_SETTINGS
        )
        data = {
            e["name"]: e.get("value", "")
            for e in soup_settings_page.find_all("input", {"name": True})
        }
        data.update(
            {
                e["name"]: e.find("option", selected=True).get("value", "")
                for e in soup_settings_page.find_all("select", {"name": True})
            }
        )
        self.original_settings = data.copy()
        data["user_settings[lang]"] = "de_DE"
        await self.client.post("/iserv/profile/settings", data=data)

    async def reset_language(self):
        await self.client.post("/iserv/profile/settings", data=self.original_settings)

    def convert_list_to_str(self, list: list):
        return "".join(map(str, list)).strip().strip("\n")

    async def extract_feedback(self, soup_page: BeautifulSoup):
        """
        extract_feedback extracts the feedback from an exercise page

        Args:
            soup_page (BeautifulSoup): parsed exercise page

        Returns:
            dict: extracted data
        """
        feedback = soup_page.find("div", string="Rückmeldungen")
        feedback_files = []
        if feedback:
            feedback_text_title = feedback.find_next("td", string="Rückmeldungstext")
            if feedback_text_title:
                feedback_text = self.convert_list_to_str(
                    feedback_text_title.parent.find_next(
                        "div", class_="text-break-word"
                    ).contents
                )
            else:
                feedback_text = "Kein Rückmeldungstext"

            feedback_files_title = feedback.find_next(
                "td", string="Rückmeldungs Dateien"
            )
            if feedback_files_title:
                feedback_files = list(
                    map(
                        lambda tag: tag["href"],
                        feedback_files_title.parent.parent.find_all(
                            "a", attrs={"target": "_blank", "class": "text-break-word"}
                        ),
                    )
                )
        else:
            feedback_text = "Keine Rückmeldung"

        data = {
            "Rückmeldungstext": feedback_text,
            "Rückmeldungsdateien": feedback_files,
        }

        return data

    async def extract_submission(self, soup_page: BeautifulSoup):
        """
        extract_submission extracts the submission data from an exercise

        Args:
            soup_page (BeautifulSoup): parsed exercise page

        Returns:
            dict: extracted data
        """
        submission_text_parent = soup_page.find(
            "form", attrs={"name": "submission"}
        ).find("h5", string="Deine Textabgabe")
        if submission_text_parent:
            submission_text = self.convert_list_to_str(
                submission_text_parent.find_next_sibling(
                    "div", class_="text-break-word"
                ).contents
            )
        else:
            submission_text = "Kein Text abgegeben"

        submission_files_parent = soup_page.find("div", class_="panel-body pb-0")
        if submission_files_parent:
            if submission_files_parent.find("h5", string="Ihre abgegebenen Dateien"):
                submission_files = list(
                    map(
                        lambda tag: tag["href"],
                        submission_files_parent.find_all(
                            "a", attrs={"target": "_blank"}
                        ),
                    )
                )
        else:
            submission_files = []

        data = {
            "Abgabetext": submission_text,
            "Abgabedateien": submission_files,
        }
        return data

    async def extract_main_info(self, soup_page: BeautifulSoup):
        """
        extract_main_info extracts the main information from an exercise

        Args:
            soup_page (BeautifulSoup): parsed exercise page

        Returns:
            dict: extracted data
        """
        exercise_creator = (
            soup_page.find("th", string="Erstellt von:")
            .find_next_sibling("td")
            .contents[0]
            .string
        )
        exercise_description = self.convert_list_to_str(
            soup_page.find("div", string="Beschreibung:")
            .find_next_sibling("div")
            .contents
        )
        data = {
            "Lehrer": exercise_creator,
            "Beschreibung": exercise_description,
        }
        return data

    async def __parse_exercise_page(self, link: str):
        """
        __parse_exercise_page parse an exercise page to extract additional information

        Args:
            link (str): link to the exercise page

        Returns:
            dict: extracted data
        """
        exercise_page = await self.client.get(link)
        soup_exercise_page = BeautifulSoup(
            exercise_page.text, "html.parser", parse_only=self.ONLY_MAIN_CONTENT
        )

        data = await self.extract_main_info(soup_exercise_page)

        # Get feedback data
        feedback_data = await self.extract_feedback(soup_exercise_page)

        # Get submission data
        submission_data = await self.extract_submission(soup_exercise_page)

        return {**data, **submission_data, **feedback_data}

    async def get_exercise_data(self, tag: Tag) -> dict:
        """
        get_exercise_data extracts all data for a specific exercise

        Args:
            tag (Tag): The a tag for a specific exercise from the exercise overview

        Returns:
            dict: all gathered data
        """
        link = tag["href"]
        parse_task = asyncio.create_task(self.__parse_exercise_page(link))
        exercise_name = tag.string
        exercise_info = list(tag.parent.next_siblings)
        start_date = datetime.strptime(exercise_info[0]["data-sort"], "%Y%m%d")
        end_date = datetime.strptime(exercise_info[1]["data-sort"], "%Y%m%d%H%M%S")
        exercise_tags = exercise_info[2].string
        exercise_data = {
            "Aufgabe": exercise_name,
            "Startdatum": start_date.strftime("%d.%m.%Y %H:%M"),
            "Enddatum": end_date.strftime("%d.%m.%Y %H:%M"),
            "Link": link,
            "Tags": exercise_tags,
        }

        parsed_data = await parse_task
        exercise_data.update(parsed_data)
        return exercise_data

    async def run(self):
        """
        Run the scraper and return the data.
        """
        await self.change_language()
        page_exercises = await self.client.get("/iserv/exercise?filter[status]=all")
        soup_page_exercises = BeautifulSoup(
            page_exercises.text, "html.parser", parse_only=self.ONLY_TABLE
        )
        filtered_exercises = soup_page_exercises.find_all(self.tag_filter)
        tasks = [self.get_exercise_data(exercise) for exercise in filtered_exercises]
        data = await asyncio.gather(*tasks)
        return data

    async def close(self):
        """
        Close connection and revert any setting changes.
        """
        await self.reset_language()
        await self.client.aclose()


# %%
async def main():
    scraper = await Scraper()
    try:
        data = await scraper.run()
        with open("data.csv", "w", encoding="utf-8", newline="") as f:
            utils.create_csv(f, data)
    finally:
        await scraper.close()


# %%

if __name__ == "__main__":
    asyncio.run(main())
