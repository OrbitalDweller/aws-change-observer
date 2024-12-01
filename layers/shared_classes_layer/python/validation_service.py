import re #regex library 

class ValidationService:
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validates an email address using a regular expression.

        :param email: Email address to validate.
        :return: True if the email is valid, False otherwise.
        """
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$' #regex for email (chars@chars.chars)
        return bool(re.match(email_pattern, email))
