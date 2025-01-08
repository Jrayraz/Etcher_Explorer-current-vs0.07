from backstage.handler.link_handler import LinkHandler
from backstage.handler.unlink_handler import UnlinkHandler
from backstage.handler.relink_handler import RelinkHandler
from backstage.handler.target_handler import TargetHandler
from backstage.handler.recent_handler import RecentHandler
from backstage.cli.init import InitHandler
from backstage.cli.run import RunHandler
from backstage.cli.build import BuildHandler
from backstage.cli.release import ReleaseHandler
from backstage.handler.hub_handler import HubHandler
from backstage.cli.version import VersionHandler
from backstage import pymisc, get_app_pkg
import os


HANDLERS = {"build": BuildHandler,
            "hub": HubHandler, "init": InitHandler,
            "link": LinkHandler, "release": ReleaseHandler,
            "recent": RecentHandler, "relink": RelinkHandler,
            "run": RunHandler, "target": TargetHandler,
            "unlink": UnlinkHandler, "version": VersionHandler}


def command(line=None, target=None):  # TODO: make it returns a boolean
    """
    Param:
        - line is a string or a list. Example "link /home/project" or ["link", "/home/proj"]
        - target is a path string
    """
    args = None
    if not line:
        return
    if isinstance(line, str):
        args = pymisc.parse_cmd(line)
    else:
        args = line
    app_pkg = get_app_pkg(target)
    if not target:
        target = os.getcwd()
    operation = args[0]
    args = args[1:]
    if operation == "help":
        _show_help(args)
        return
    try:
        HANDLERS[operation](target, app_pkg, *args)
    except KeyError:
        print("Unknown operation")
    except Exception as e:
        raise e
        print("error: ", e)
        print("Oops an error occurred")


def _show_help(args):
    if not args:
        print("Type 'help <operation>' to access the doc.")
        print("Available operations: ")
        for key in HANDLERS.keys():
            print(" - {}".format(key))
        return
    if len(args) > 1:
        print("Incorrect usage of the help command.")
        return
    operation = args[0]
    try:
        print(HANDLERS[operation].__doc__)
    except KeyError:
        print("Unknown operation")
    except Exception:
        print("Oops an error occurred")
