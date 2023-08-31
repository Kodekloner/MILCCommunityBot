from typing import Union, List
from config.options import config
from functools import wraps

LIST_OF_ADMINS = config["TELEGRAM"]["ADMINS"]


def triggers(trigger_command: Union[str, List[str]]):
    """Trigger decorator for commands.

    :param trigger_command: The command trigger(s) for the command.
    :return: The decorated function.
    """

    if isinstance(trigger_command, str):
        trigger_command = [trigger_command]

    if not isinstance(trigger_command, list):
        raise TypeError(
            f"Triggers must be a string or a list of strings, not {type(trigger_command)}"
        )

    def wrapper(func):
        func.triggers = trigger_command
        return func

    return wrapper


def description(description_doc: str):
    """Description decorator for commands. Only HTML formatting is supported.

    :param description_doc: The description string for the command.
    :return: The decorated function.
    """

    def wrapper(func):
        func.description = description_doc
        return func

    return wrapper


def usage(usage_doc: str):
    """Usage decorator for commands. Only HTML formatting is supported.

    :param usage_doc: The usage string for the command.
    :return: The decorated function.
    """

    def wrapper(func):
        func.usage = usage_doc
        return func

    return wrapper


def example(example_doc: str):
    """Example decorator for commands. Only HTML formatting is supported.

    :param example_doc: The example string for the command.
    :return: The decorated function.
    """

    def wrapper(func):
        func.example = example_doc
        return func

    return wrapper


def api_key(name: str):
    """API key decorator for commands.

    :param name: The name of the API key required to use this function.
    :return: The decorated function.
    """

    def wrapper(func):
        func.api_key_name = name
        return func

    return wrapper


def deprecated(message: str):
    """Deprecated decorator for commands.

    :param message: The message to display when the command is used.
    :return: The decorated function.
    """

    def wrapper(func):
        func.deprecated = message
        return func

    return wrapper

def restricted(func):
    """This decorator allows you to restrict the access of a handler to
    only the user_ids specified in LIST_OF_ADMINS."""

    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if str(user_id) not in LIST_OF_ADMINS:
            print(f"Unauthorized access denied for {user_id}.")
            return
        return await func(update, context, *args, **kwargs)

    return wrapped

def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        async def command_func(update, context, *args, **kwargs):
            await context.bot.send_chat_action(
                chat_id=update.effective_message.chat_id, action=action
            )
            return await func(update, context, *args, **kwargs)

        return command_func

    return decorator
