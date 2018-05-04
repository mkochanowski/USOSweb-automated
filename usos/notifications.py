import sys
import json
import os.path
import logging
import yagmail
from jinja2 import Environment, FileSystemLoader

logging = logging.getLogger(__name__)


class Dispatcher:
    """Allows for sending multiple messages via configured channels. 
    
    Creating a new dispatcher that operates on selected channels::

        from usos.notifications import Dispatcher

        my_dispatcher = Dispatcher(
            channels="Email SMS WebPush MessengerPigeon",
            enable=True,
            config_file="notifications.json")

    :param channels: names of the channels separated by a single space. 
    :param enable: whether to allow the dispatcher to send any 
        notifications.
    :param config_file: path to a file that contains channel-specific 
        variables such as API Keys or special parameters.
    """

    def __init__(self, channels: str, enable: bool,
                 config_file: str) -> None:
        self.channels = channels.split(" ")
        self.enable = enable
        self.config = self._load_config(config_file)

    def send(self, data: dict) -> bool:
        """Sends notifications via channels set in the initializer.

        :param data: the data that will be sent.
        :returns: ``True`` if every notification has been sent 
            successfuly on every channel.
        """
        logging.info("Preparing dispatcher")
        for channel in self.channels:
            self.send_single(channel, data)

        return True

    def send_single(self, channel: str, data: dict) -> bool:
        """Sends notifications via a single, given channel.

        :param channel: a name of the channel.
        :param data: data that will be used to render the templates.
        :returns: ``True`` if the notifications have been sent 
            successfuly on a given channel.
        """
        if self.enable:
            stream = getattr(sys.modules[__name__], channel)(
                data=data, config=self.config[channel])
            logging.info("Sending notifications via {}".format(channel))
            return stream.render_and_send()

        return False

    def _load_config(self, filename: str) -> dict:
        """Loads a configuration file containing channel-specific 
        variables.

        :param filename: name of the configuration file
        :returns: variables bound to a specific channel eg.
            { "channel_name" => [list_of_variables] }
        """
        data = {}

        if os.path.isfile(filename):
            try:
                with open(filename, 'r') as working_file:
                    data = json.load(working_file)
                    logging.info("'{}' - json fetched ".format(filename)
                                 + "correctly")
            except IOError:
                logging.exception("Config file '{}' ".format(filename)
                                  + "could not be opened")

        return data


class Notification:
    """Provides a common layer of abstraction for every existing channel.

    Use this class for inheritance while implementing custom streams::

        class PaperMail(Notification):
            def _render(self) -> None:
                letter: str = "Hey, {name}! "
                              + "{message} "
                              + "Take care, {author}."  
               
                letter = letter.format(
                    name=data["recipient"], 
                    message=data["message"],
                    author=data["sender"])
                
                self._rendered_template = letter

            def _send(self) -> bool:
                put_in_a_mailbox(self._rendered_template)
                return True

    Now it can be used as a channel named ``PaperMail``::

        dispatcher = Dispatcher(
            channels="PaperMail",
            enable=True,
            config_file="mailbox_coordinates.json")

        my_message = {
            "recipient": "Kate",
            "message": "I'm getting a divorce.",
            "sender": "Anthony"
        }

        dispatcher.send(my_message)
        
    Read more at: :ref:`CustomNotificationsStreams`.

    :param data: data that will be used in the rendering of the final 
        message. 
    :param config: variables that can be used for configuration purposes 
        such as API Keys or custom parameters.
    """

    def __init__(self, data: dict, config: dict = {}) -> None:
        self.data = data
        self.config = config
        self._rendered_template = ""

    def template_output(self) -> str:
        """Returns the output of a template for a channel.

        This method will return an empty string if you try to retrieve
        a template without rendering it first.

            >>> mail = PaperMail(my_message, {"DeliverOnTime": False})
            >>> mail.template_output()
            ''
            >>> mail.render()
            >>> mail.template_output()
            'Hey, Kate! I'm getting a divorce. Take care, Anthony.'

        :returns: a rendered template.
        """
        return self._rendered_template

    def render(self) -> str:
        """Renders the template that will be sent in a notification.

        For rendering the template, this method uses a private 
        :meth:`_render` method.

        :returns: a rendered template.
        """
        logging.info("Rendering the notifiation's template")
        self._render()
        return self.template_output()

    def send(self) -> bool:
        """Sends a notification if the rendered template isn't empty.

        For sending a notification, this method uses a private 
        :meth:`_send` method.

        :returns: ``True`` if a notification has been sent successfuly.
        """
        logging.info("Checking whether the template has been rendered")
        if self.template_output():
            logging.info("Sending")
            return self._send()
        else:
            logging.error("The rendered template was found empty")
        return False

    def render_and_send(self) -> bool:
        """Renders the template and then sends a notification.

        This method is an equivalent of calling :meth:`render` and 
        :meth:`send` separately.

        :returns: ``True`` if a notification has been sent successfuly.
        """
        self.render()
        return self.send()

    def _render(self) -> None:
        pass

    def _send(self) -> bool:
        return False


class Email(Notification):
    """Sends a notification via Email"""

    def _render(self) -> None:
        """Renders an Email template"""
        env = Environment(
            loader=FileSystemLoader('templates/notifications'),
            lstrip_blocks=True,
            trim_blocks=True)
        template = env.get_template('Email.html')

        self._rendered_template = template.render(data=self.data)

    def _send(self) -> bool:
        """Send an Email notification"""
        with yagmail.SMTP(self.config["mail_sender"],
                          oauth2_file="oauth2_creds.json") as yag:
            status = yag.send(
                self.config["mail_recipient"],
                self.config["mail_subject"],
                self._rendered_template)

        logging.info("Sending mail status: {}".format(status))

        return True  # FIXME


class SMS(Notification):
    """Sends a notification via SMS"""

    def _render(self) -> None:
        """Renders a text message"""
        pass

    def _send(self) -> bool:
        """Sends a text message"""
        return False


class WebPush(Notification):
    """Sends a notification via WebPush Notifications"""

    def _render(self) -> None:
        """Renders a WebPush notification template"""
        pass

    def _send(self) -> bool:
        """Sends a WebPush notification"""
        return False
