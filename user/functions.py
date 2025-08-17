import secrets
import string


def generate_password(length: int = 10, nb_digits: int = 3) -> str:
    """
    Generate a random password following best practices.

    By default, the password will satisfy the following criteria:
    - At least 10 characters long,
    - At least one lowercase letter,
    - At least one uppercase letter,
    - At least three digits.
    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    char_set = string.ascii_letters + string.digits
    while True:
        password = "".join(secrets.choice(char_set) for i in range(length))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and sum(c.isdigit() for c in password) >= nb_digits
        ):
            break
    return password
