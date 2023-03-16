import math

def get_room_id(user_1, user_2):
    if math.isnan(user_1) or math.isnan(user_2) or user_1 == user_2:
        return None
    min_user_id = user_2 if user_1 > user_2 else user_1
    max_user_id = user_1 if user_1 > user_2 else user_2
    return f"{min_user_id}:{max_user_id}"