import argparse
import logging
from contextlib import contextmanager
import datetime
from os import remove
from os.path import isfile
from time import sleep

import telegram
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


@contextmanager
def get_selenium_driver(selenium_command_executor, failure_screenshot=None, success_screenshot=None):
    if failure_screenshot and isfile(failure_screenshot):
        remove(failure_screenshot)
    if success_screenshot and isfile(success_screenshot):
        remove(success_screenshot)

    driver = webdriver.Remote(command_executor=selenium_command_executor,
                              desired_capabilities=DesiredCapabilities.FIREFOX)
    try:
        yield driver
        if success_screenshot:
            S = lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
            driver.set_window_size(S('Width'), S('Height'))
            driver.find_element_by_tag_name('body').screenshot(success_screenshot)
    except:
        if failure_screenshot:
            S = lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
            driver.set_window_size(S('Width'), S('Height'))
            driver.find_element_by_tag_name('body').screenshot(failure_screenshot)
        raise
    finally:
        driver.delete_all_cookies()
        driver.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Looks for available appointments in TLSContact.')
    parser.add_argument('--tls-application-reference', type=str, help='TLSContact application reference', required=True)
    parser.add_argument('--login', type=str, help='TLSContact login', required=True)
    parser.add_argument('--password', type=str, help='TLSContact password', required=True)
    parser.add_argument('--telegram-bot-token', type=str, help='Telegram bot`s token', required=True)
    parser.add_argument('--telegram-chat-id', type=int,
                        help='Telegram chat id to send notifications to (you can use @userinfobot to get your id)',
                        required=True)
    parser.add_argument('--search-before', type=str,
                        help='Notify when appointment is available before this date, e.g. 2019-10-20',
                        required=True)
    parser.add_argument('--delay', type=int,
                        help='Delay in seconds before retries (recommended value is 5400 seconds or 1.5 hours)',
                        default=5400)
    parser.add_argument('--selenium-executor', type=str,
                        help='Selenium command executor url, e.g. http://selenium:4444/wd/hub',
                        default='http://selenium:4444/wd/hub')
    parser.add_argument('--once', help='Run only once', action='store_true', default=False)
    args = parser.parse_args()

    bot = telegram.Bot(args.telegram_bot_token)

    logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    while True:
        if datetime.date.today().strftime('%Y-%m-%d') >= args.search_before:
            logging.error('Search-date must be in the future')
            break

        try:
            logging.info('Starting...')
            with get_selenium_driver(args.selenium_executor, './static/tls_contact_error.png',
                                     './static/tls_contact_success.png') as driver:
                driver.get('https://fr.tlscontact.com/gb/LON/login.php')
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'email')))
                driver.get('https://fr.tlscontact.com/gb/LON/login.php')
                email = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'email')))
                email.send_keys(args.login)
                driver.find_element_by_id('pwd').send_keys(args.password)
                btn = driver.find_element_by_xpath('//input[@type="button"]')
                btn.click()
                WebDriverWait(driver, 15).until(EC.staleness_of(btn))

                has_error = False

                try:
                    error = driver.find_element_by_xpath('//div[@class="main_message main_message_"]')
                    error_text = error.text.strip()
                    if error_text:
                        logging.error('Got error - ' + error_text)
                        bot.send_message(chat_id=args.telegram_chat_id, text='Got an error! %s' % error_text)
                    else:
                        logging.error('Unexpected error occurred')
                    has_error = True
                except NoSuchElementException:
                    pass

                if not has_error:
                    S = lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
                    driver.set_window_size(S('Width'), S('Height'))
                    driver.find_element_by_tag_name('body').screenshot('./static/after_login.png')
                    WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located(
                                    (By.XPATH, '//*[text()="%s"]' % args.tls_application_reference)))
                    first_appointment = driver.find_element_by_xpath(
                            '//div[@class="inner_timeslot"][a[@class="appt-table-btn dispo"]]/span[@class="appt-table-d"]')
                    first_date = re.sub(r'^.*?(\w+\s+\d+).*$', r'\1', first_appointment.text, 0, re.DOTALL)
                    date = datetime.datetime.strptime(str(datetime.date.today().year) + ' ' + first_date, '%Y %B %d').date()

                    if date < datetime.date.today():
                        date = datetime.datetime.strptime(str(datetime.date.today().year + 1) + ' ' + first_date, '%Y %B %d').date()

                    logging.info('Got date ' + date.strftime('%Y-%m-%d'))

                    if date < datetime.datetime.strptime(args.search_before, '%Y-%m-%d').date():
                        bot.send_message(chat_id=args.telegram_chat_id, text='New date found! %s' % date.strftime('%Y-%m-%d'))
                        bot.send_message(chat_id=args.telegram_chat_id, text='Current cookies: %s' % driver.get_cookies())
                    else:
                        bot.send_message(chat_id=args.telegram_chat_id,
                                         text='No new dates, earliest available is %s' % date.strftime('%Y-%m-%d'))
        except KeyboardInterrupt:
            logging.info('Terminating...')
            break
        except Exception as e:
            logging.exception('Got error')
            bot.send_message(chat_id=args.telegram_chat_id, text='Got an exception! %s' % e)
        finally:
            logging.info('Done')
            if args.once:
                break
            sleep(args.delay)
