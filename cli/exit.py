import typer

existing_usernames = ["rick", "morty", "sixtus"]


def maybe_create_user(username: str):
    if username in existing_usernames:
        print("The user already exists")
        raise typer.Exit()
    elif username == "root":
        print("The root user is reserved")
        raise typer.Abort()
    else:
        print(f"User created: {username}")


def send_new_user_notification(username: str):
    # Somehow send a notification here for the new user, maybe an email
    print(f"Notification sent for new user: {username}")


def main(username: str):
    maybe_create_user(username=username)
    send_new_user_notification(username=username)


if __name__ == "__main__":
    typer.run(main)
