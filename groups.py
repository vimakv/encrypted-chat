# =========================
# groups.py
# =========================

groups = {}


# CREATE GROUP
def create_group(group_name):

    if group_name not in groups:

        groups[group_name] = []

        return True

    return False


# ADD MEMBER
def add_member(group_name, username):

    if group_name in groups:

        if username not in groups[group_name]:

            groups[group_name].append(
                username
            )

            return True

    return False


# REMOVE MEMBER
def remove_member(group_name, username):

    if group_name in groups:

        if username in groups[group_name]:

            groups[group_name].remove(
                username
            )

            return True

    return False


# GET MEMBERS
def get_members(group_name):

    return groups.get(
        group_name,
        []
    )


# GET ALL GROUPS
def get_all_groups():

    return groups