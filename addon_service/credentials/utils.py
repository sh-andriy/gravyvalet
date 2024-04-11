from addon_toolkit import credentials


def format_credentials_for_waterbutler(creds_data):
    match type(creds_data):
        case credentials.AccessTokenCredentials:
            return {"token": creds_data.access_token}
        case _:
            return creds_data.asdict()
