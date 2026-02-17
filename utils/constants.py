import pathlib

def get_uri(file_name):
    return pathlib.Path(f"pages/{file_name}").absolute().as_uri()

# Page URLs
PAGES = {
    "V1": get_uri("login-v1.html"),
    "V2": get_uri("login-v2.html"),
    "V3": get_uri("login-v3.html"),
}

class Selectors:
    LOGIN_BUTTON = "#login-submit"
    USERNAME_FIELD = "#username"
    PASSWORD_FIELD = "#password"
    MESSAGE_TEXT = "#message"