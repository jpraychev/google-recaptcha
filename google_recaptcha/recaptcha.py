from flask import request
from markupsafe import Markup
import requests
import os
from pathlib import Path

class ReCaptcha:
    """ Recaptcha class that could be integrated as a standalone library to any html form
    that should be protected using v3 of Google Recaptcha technology.

    app - Flask app that has to be passed to the class constructor
    site_key - site key that is used to generate user's token.
    site_secret - secret key that is being used to verify users requests

    If keys are not provided to the class the script will try to get them from environment variables

    Both keys are generated through https://www.google.com/recaptcha/admin
    """

    VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'
    LIB_LOCATION = Path(__file__).parent
    TEMPLATE_LOCATION = LIB_LOCATION.joinpath('templates/recaptcha.html')

    def __init__(
        self,
        app: str,
        site_key: str = None,
        site_secret: str = None
    ):
        app.context_processor(self.generate_code)
        self.site_key = os.getenv('RECAPTCHA_SITE_KEY') if site_key is None else site_key
        self.site_secret = os.getenv('RECAPTCHA_SECRET_KEY') if site_secret is None else site_secret


    def verify(self):
        """Verifies if the provider google recaptcha response is correct.
        The default threshold is 0.5

        Raises:
            Exception: If response status code is different that 200

        Returns:
            bool: Returns true or false if the requests has been verify by Google
            and has a score greatr than 0.5
        """
        data = {
            'secret': self.site_secret,
            'response' : request.form['g-recaptcha-response']
        }

        r = requests.post(self.VERIFY_URL, data=data)

        if r.status_code != 200:
            raise Exception('Invalid request')
        if not r.json()['success']:
            return False
        return True

    def generate_code(self) -> dict:
        """Generates a code snippet located in templates/recaptcha.html file
        that is used to verify users request

        Returns:
            dict: Returns recaptcha object that is dynamically included into specific view
        """
        with open(self.TEMPLATE_LOCATION) as f:
            data = f.read()
        
        return dict(recaptcha = Markup(self.parse_data(data)))

    def parse_data(self, data:str) -> str:
        """Parses the provided data by changing users provided site key

        Args:
            data (str): Data to be parsed

        Returns:
            str: Parsed data with new site key
        """
        return data.replace('__SITE_KEY', self.site_key)