# %%
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag


# %%
def href_filter(href: str):
    return href.startswith(url + "/iserv/exercise/show/")


def tag_filter(tag: Tag):
    return (
        tag.name == "a" and href_filter(tag["href"]) and "AG 3D-Druck" not in tag.string
    )


#%%
client = requests.Session()
username = input("Username: ")
password = input("Password: ")
url = "https://whg-duew.de"

# %%
login_url = url + "/iserv/app/login"
login_info = {"_username": username, "_password": password}
page_login = client.post(login_url, data=login_info)
if page_login.url.startswith(login_url):
    print("Something went wrong.")
    raise Exception
else:
    print("Logged in")

# %%
page_exercise = client.get(url + "/iserv/exercise?filter[status]=all")


# %%
soup_page_exercise = BeautifulSoup(page_exercise.text, "html.parser")
filtered_exercises = soup_page_exercise.find_all(tag_filter)

# %%
