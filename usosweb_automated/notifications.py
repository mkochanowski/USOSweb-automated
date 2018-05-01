import sys
import json
import os.path
import logging
import yagmail
from jinja2 import Environment, FileSystemLoader

logging = logging.getLogger(__name__)


class Dispatcher:
    def __init__(self, channels: str, enable: bool,
                 config_file: str) -> None:
        self.channels: list = channels.split(" ")
        self.enable: bool = enable
        self.config = self._load_config(config_file)

    def send(self, data: dict) -> bool:
        logging.info("Preparing dispatcher")
        for channel in self.channels:
            self.send_single(channel, data)

        return True

    def send_single(self, channel: str, data: dict) -> bool:
        if self.enable:
            stream = getattr(sys.modules[__name__], channel)(
                data=data, config=self.config[channel])
            logging.info(f"Sending notifications via {channel}")
            return stream.render_and_send()

        return False

    def _load_config(self, filename: str) -> dict:
        data = {}

        if os.path.isfile(filename):
            try:
                with open(filename, 'r') as working_file:
                    data = json.load(working_file)
                    logging.info(f"'{filename}' - json fetched "
                                 + "correctly")
            except IOError:
                logging.exception(f"Config file '{filename}' could "
                                  + "not be opened")

        return data


class Notification:
    def __init__(self, data: dict, config: dict = {}) -> None:
        self.data: dict = data
        self.config: dict = config
        self._rendered_template: str = None

    def template_output(self) -> str:
        return self._rendered_template

    def send(self) -> bool:
        if self._rendered_template:
            return self._send()
        return False

    def render_and_send(self) -> bool:
        logging.info("Rendering the notifiation's template")
        self._render()
        logging.info("Sending")
        return self.send()

    def _send(self) -> bool:
        return False

    def _render(self) -> None:
        pass


class Email(Notification):
    def _send(self) -> bool:
        with yagmail.SMTP(self.config["mail_sender"],
                          oauth2_file="oauth2_creds.json") as yag:
            status = yag.send(
                self.config["mail_recipient"],
                self.config["mail_subject"],
                self._rendered_template)
        
        logging.info(f"Sending mail status: {status}")
        
        return True #FIXME

    def _render(self) -> None:
        env = Environment(
            loader=FileSystemLoader('templates/notifications'), 
            lstrip_blocks=True,
            trim_blocks=True)
        template = env.get_template('Email.html')

        self._rendered_template = template.render(data=self.data)


class SMS(Notification):
    def _send(self) -> bool:
        return False

    def _render(self) -> None:
        pass


class WebPush(Notification):
    def _send(self) -> bool:
        return False

    def _render(self) -> None:
        pass
