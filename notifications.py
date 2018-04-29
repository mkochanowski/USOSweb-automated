import logging

logging = logging.getLogger(__name__)


class Notification:
    def __init__(self, data: object) -> None:
        self._rendered_template: str = None
        self.data: object = data

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
        return False

    def _render(self) -> None:
        template: str = ""
        self._rendered_template = template


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


class Dispatcher:
    def __init__(self, channels: str, enable: bool) -> None:
        self.channels: list = channels.split(" ")
        self.enable: bool = enable
        self.data: object = None #FIXME

    def send(self) -> bool:
        logging.info("Preparing dispatcher")
        for channel in self.channels:
            self.send_single(channel)

        return True

    def send_single(self, channel: str) -> bool:
        if self.enable:
            stream = eval(channel + "(data=self.data)")
            logging.info(f"Sending notifications via {channel}")
            return stream.render_and_send()

        return False
