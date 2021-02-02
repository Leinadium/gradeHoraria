from selenium import webdriver
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
from os import path, rename, listdir, remove, devnull
from time import sleep
import json
import csv

SELENIUM_SOURCE = 'firefox'

SRCPATH = path.dirname(path.realpath(__file__))

PATH_TO_CREDENTIALS = path.join(SRCPATH, 'credentials.json')
PATH_TO_DRIVER = path.join(SRCPATH, 'driver', 'geckodriver27.exe')
PATH_TO_DRIVER_PI = '/usr/bin/chromedriver'
PATH_TO_DATA_FOLDER = path.join(SRCPATH, 'data')
PATH_TO_DATA_CSV = path.join(PATH_TO_DATA_FOLDER, 'download.csv')
PATH_TO_DATA_JSON = path.join(PATH_TO_DATA_FOLDER, 'download.json')
PATH_TO_DATA_DESTINO = path.join(PATH_TO_DATA_FOLDER, 'destinos.json')

# if not path.exists(PATH_TO_DRIVER):
#     raise Exception("Driver not installed")


def _get_browser():
    """
    Opens a browser window to navigate
    :return: webdriver.Firefox object
    """
    # IF FIREFOX
    if SELENIUM_SOURCE == 'firefox':
        from selenium.webdriver.firefox.options import Options
        opt = Options()
        opt.headless = True  # Change for debbuging
        opt.set_preference("browser.download.folderList", 2)  # custom download folder
        opt.set_preference("browser.download.manager.showWhenStarting", False)  # disable showing when downloading
        opt.set_preference("browser.download.dir", PATH_TO_DATA_FOLDER)
        opt.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
        browser = webdriver.Firefox(options=opt, executable_path=PATH_TO_DRIVER, service_log_path=devnull)

    # IF CHROME
    elif SELENIUM_SOURCE == 'chrome':
        from selenium.webdriver.chrome.options import Options
        opt = Options()
        opt.headless = True  # Change for debbuging
        opt.add_experimental_option("prefs", {
            "download.default_directory": PATH_TO_DATA_FOLDER,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        browser = webdriver.Chrome(executable_path=PATH_TO_DRIVER_PI,options=opt, service_log_path=devnull)

    else:
        raise Exception("Unknown source for selenium webdriver")

    return browser


def _clear_previous_file():
    """
    Clear all the other files in data
    """
    files = listdir(PATH_TO_DATA_FOLDER)
    for f in files:
        remove(path.join(PATH_TO_DATA_FOLDER, f))

    return


def _rename_downloaded_file():
    """
    Renames the data downloaded to 'download.csv'
    If there is more than one file, it aborts
    """
    files = listdir(PATH_TO_DATA_FOLDER)
    for f in files:
        if f.endswith('.csv'):
            file = path.join(PATH_TO_DATA_FOLDER, f)  # absolute path to file
            rename(file, PATH_TO_DATA_CSV)  # rename to download.csv
            break
    return


def _read_all_courses():
    """
    Reads all the courses availables at puc-rio.br/microhorario
    :return: a list of Courses objects
    """

    print("  Opening browser")
    b = _get_browser()

    print("  Getting puc-rio.br/microhorario")
    b.get('https://www.puc-rio.br/microhorario')

    # sometimes there is a popup, we need to accept before continuing
    try:
        popup_box = b.find_element_by_xpath('/html/body/div[2]/div[3]/div/button')
        if popup_box is not None:
            popup_box.click()

    except Exception as e:
        pass

    print("  Searching all courses and waiting")
    # searching any course
    buscar_box = b.find_element_by_xpath('//*[@id="btnBuscar"]')
    buscar_box.click()

    sleep(3)  # wait to load the page

    print("  Downloading the data")
    # download tab
    download_tab = b.find_element_by_xpath('//*[@id="lblBaixarInfo"]')
    download_tab.click()
    format_selection = Select(b.find_element_by_xpath('//*[@id="ddlExtensao"]'))
    format_selection.select_by_visible_text('Texto (.csv)')
    download_box = b.find_element_by_xpath('//*[@id="btnDownload"]')
    download_box.click()

    print("  Waiting for the download to finish")
    sleep(10)

    print("  Renaming downloaded file")
    _rename_downloaded_file()

    print("  Getting destinos")
    destino_box = Select(b.find_element_by_xpath('//*[@id="ddlBloqueio"]'))
    all_destinos = destino_box.options

    print("  Saving destinos")
    dict_destinos = dict()
    for d in all_destinos:
        d = d.text
        if '-' in d:  # finding the correct ones
            code, name = d.split(' - ')
            code = code.strip()
            name = name.strip()
            dict_destinos[code] = name

    with open(PATH_TO_DATA_DESTINO, 'w+') as f:
        json.dump(dict_destinos, f, indent=2, ensure_ascii=False)

    print("  Closing browser")
    b.close()  # exits the browser
    b.quit()

    return


def _fix_data():
    """
    Fix the downloaded .csv file
    The file is in UTF-16, but doesnt have the BOM (U+FFFE) bytes
    This function puts the BOM bytes into the file
    """
    BOM = b'\xff\xfe'

    with open(PATH_TO_DATA_CSV, 'rb') as f:
        all_bytes = f.read()
        if all_bytes.startswith(BOM):
            return  # the file already has BOM

    with open(PATH_TO_DATA_CSV, 'wb') as f:
        f.write(BOM + all_bytes)

    return


def _convert_data_json():
    """
    Convert the .csv data into a .json
    """

    # default fieldnames
    fieldnames = ['class_code', 'className', 'professor', 'credits', 'classroom_code', 'destiny', 'slots_left', 'shift',
                  'time_room', 'online_hours', 'SHF', 'pre', 'dept']

    ret = list()
    with open(PATH_TO_DATA_CSV, 'r', encoding='utf-16') as f:
        csvfile = csv.DictReader(f, fieldnames=fieldnames, delimiter=';')

        for i in range(4):  # ignores the first 3 lines
            next(csvfile)

        for row in csvfile:
            ret.append(row)

    with open(PATH_TO_DATA_JSON, 'w+', encoding='utf8') as f:
        json.dump(ret, f, indent=2, ensure_ascii=False)

    return


def run():
    """
    Run the scraper
    """

    print("Cleaning previous data")
    _clear_previous_file()

    print("Reading all courses")
    _read_all_courses()

    print("Fixing the data")
    _fix_data()

    print("Converting")
    _convert_data_json()

    print("Exiting the scraper")
    return


if __name__ == '__main__':
    run()
