from desktop_notifier.sync import DesktopNotifierSync

notifier = DesktopNotifierSync(app_name="JobScout")


def send_notification(title: str, message: str) -> None:
    """Show a desktop notification on Windows, macOS or Linux."""
    notifier.send(title=title, message=message)


if __name__ == "__main__":
    send_notification("New Job Found", "JobScout found a new job for you!")