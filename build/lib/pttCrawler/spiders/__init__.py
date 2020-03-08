# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

from scrapy.utils.log import configure_logging  
from pttCrawler import settings
import logging

configure_logging(install_root_handler=False) 
logging.basicConfig ( 
    filename = 'logging.txt', 
    format = '%(levelname)s: %(message)s', 
    level = logging.INFO)


## If need to send email to notify user.
# from scrapy.mail import MailSender
# mailer = MailSender.from_settings(settings.mail_settings)