from common.enum import EnumValue


class AuthenticateType(EnumValue):
    login_with_password = "login_with_password"
    validate_security_question = "validate_security_question"
    activate_and_authenticate = "activate_and_authenticate"
    refresh_token = "refresh_token"
    login_with_otp = "login_with_otp"
    validate_otp = "validate_otp"
