from selenium.webdriver.common.by import By
import requests
import pandas as pd
import csv
from time import sleep


def get_audience_page(name, driver, url):
    '''Returns the url of the audience page'''

    driver.get(url)
    driver.find_element(By.CSS_SELECTOR, 'a[href="#panel_cast_miestnosti"]').click()
    input_tag = driver.find_element(By.XPATH, '//*[@id="showRooms"]')
    input_tag.send_keys(name)

    sleep(3)
    room = driver.find_element(By.XPATH, '//*[@id="list_rooms_box"]/ul/li/a')
    room.click()
    current_url = driver.current_url + '.csv'

    return current_url

def get_teacher_page(name, driver, url):
    '''Returns the url of the teacher page'''

    driver.get(url)
    driver.find_element(By.CSS_SELECTOR, 'a[href="#panel_cast_ucitelia"]').click()
    input_tag = driver.find_element(By.XPATH, '//*[@id="showTeachers"]')
    input_tag.send_keys(name)

    sleep(3)
    teacher = driver.find_element(By.XPATH, '//*[@id="list_teachers_box"]/ul/li/a')
    teacher.click()
    current_url = driver.current_url + '.csv'

    return current_url

def get_lessons(url):
    '''Returns the lessons of the teacher or audience stored in a html file'''

    r = requests.get(url)
    decoded_content = r.content.decode('utf-8')
    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    my_list = list(cr)
    df = pd.DataFrame(my_list[1:], columns=my_list[0]).set_index(['Deň'])

    # Drop a column with NaN values
    df = df.drop('Poznámka', axis=1)
    html = df.to_html()

    # Save the html file
    html_file = open('schedule.html', 'w')
    html_file.write(html)
    html_file.close()
    return open('schedule.html', 'rb')


def get_data(type, argument, driver, url, r):
    '''Returns the data from the cache or from the website'''

    key = f"{type}:{argument}"
    data = r.get(key)

    if data:
        print('Data from cache')
        return data.decode()
    else:
        if type == 'group':
            data = get_lessons(url)
            data = data.read().decode('utf-8')
        elif type == 'teacher':
            url = get_teacher_page(argument, driver, url)
            data = get_lessons(url)
            data = data.read().decode('utf-8')
        elif type == 'audience':
            url = get_audience_page(argument, driver, url)
            data = get_lessons(url)
            data = data.read().decode('utf-8')

        else:
            raise ValueError("Invalid type")

        # Store the data in the cache
        r.set(key, data)
        print('Data from website')
        return url 