from firebase_admin import auth


def get_user(access_token):
    try:
        return auth.verify_id_token(access_token)
    except:
        return None


def delete_user(uid):
    try:
        auth.delete_user(uid)
        return 0
    except:
        return 1
