import json
import logging
from time import sleep
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction

logger = logging.getLogger(__name__)
import kanboard

from requests.auth import HTTPBasicAuth
from requests import get as g
from requests import post as p

class Kanboard(Extension):

    def __init__(self):
        super(Kanboard, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):

        items = []

        query = event.get_argument() or ""
        split_query = query.partition(" ")

        keyword = split_query[0]
        data = split_query[2]

        if keyword != "add":

            items.append(ExtensionResultItem(icon='images/icon.png',
                                                name='Please use the keyword "add"',
                                                description='Example: add %s' % data,
                                                highlightable=False,
                                                on_enter=DoNothingAction()))

            return RenderResultListAction(items)

        else:
            items.append(ExtensionResultItem(icon='images/icon.png',
                                            name="Press enter to add: %s" % (data),
                                            highlightable=False,
                                            on_enter=ExtensionCustomAction(data, keep_app_open=True)))

            return RenderResultListAction(items)

class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):

        items = []

        data = event.get_data()
        setting_url = extension.preferences['setting_url']
        setting_user = extension.preferences['setting_user']
        setting_pass = extension.preferences['setting_pass']
        setting_project = extension.preferences['project_id']

        url = setting_url + "/jsonrpc.php"

        payload = "{\"jsonrpc\": \"2.0\", \"method\": \"createTask\", \"id\": 1, \"params\": {\"title\": \"" + data + "\", \"project_id\": " + setting_project + "}}"

        r = p(url, data=payload, auth=HTTPBasicAuth(setting_user, setting_pass))

        # response = r.json()

        if r.status_code == 200:
            items.append(ExtensionResultItem(icon='images/icon.png',
                                                            name="Added %s" % data,
                                                            highlightable=False,
                                                            on_enter=HideWindowAction()))
            return RenderResultListAction(items)
        else:
            items.append(ExtensionResultItem(icon='images/icon.png',
                                                            name="Error connecting to API.",
                                                            highlightable=False,
                                                            on_enter=HideWindowAction()))
            return RenderResultListAction(items)

if __name__ == '__main__':
    Kanboard().run()
