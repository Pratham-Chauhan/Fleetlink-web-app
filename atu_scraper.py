from datetime import datetime
import re
import platform
from time import sleep
import random
import pandas as pd
from playwright.sync_api import Locator, sync_playwright
import os
import sys
import logging
import threading


class ATUScraper:
    def __init__(self, data, timestamp):
        self.data = data
        self.timestamp = timestamp
        self.page = None
        self.thread_id = threading.get_ident()

        self.logger = self.setup_logger()
        self.input_file = "./fleetlink_id_mapping.xlsx"

        self.BROWSER_TYPE = 'Camoufox'
        self.HEADLESS = True

    def setup_logger(self):
        os.makedirs("logs", exist_ok=True)
        os.makedirs("screenshots", exist_ok=True)

        # thread_id = threading.get_ident()
        log_file = f"logs/run-{self.timestamp}.log"

        logger = logging.getLogger(f'scraper-{self.thread_id}')
        logger.setLevel(logging.INFO)

        if logger.hasHandlers():
            logger.handlers.clear()

        file_handler = logging.FileHandler(log_file)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def launch_driver(self, browser_type, headless):
        if browser_type == 'Camoufox':
            try:
                from camoufox.sync_api import Camoufox
                from camoufox import DefaultAddons
            except ImportError:
                self.logger.warning("Camoufox library is not installed. Please ensure it is installed before running this code.")

            browser = Camoufox(exclude_addons=[DefaultAddons.UBO], humanize=True, headless=headless).start()
            page = browser.new_page()

        elif browser_type == 'Opera':
            playwright = sync_playwright().start()
            opera_path = self.find_opera_path()

            if not opera_path:
                self.logger.warning(f"Opera path not found, Fallback to Chromium")
                browser_type = 'Chromium'
                browser = playwright.chromium.launch(
                    headless=headless, args=['--disable-blink-features=AutomationControlled'])
            else:
                browser = playwright.chromium.launch(headless=headless, executable_path=opera_path, args=[
                    '--disable-blink-features=AutomationControlled', '--enable-vpn'])

            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0'
            )
            context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            page = context.new_page()

        self.logger.info('Browser Type: %s', browser_type)
        return page


    def find_opera_path(self):
        system = platform.system()
        possible_paths = []

        if system == 'Windows':
            possible_paths = [
                r"C:\Users\{}\AppData\Local\Programs\Opera\opera.exe".format(os.getenv('USERNAME')),
                r"C:\Program Files\Opera\opera.exe",
                r"C:\Program Files (x86)\Opera\opera.exe",
            ]
        elif system == 'Linux':
            possible_paths = [
                "/usr/bin/opera",
                "/usr/local/bin/opera",
                "/snap/bin/opera",  # If installed via Snap
            ]

        for path in possible_paths:
            if os.path.exists(path):
                self.logger.info(f"Opera path found: {path}")
                return path

        self.logger.warning("Opera path not found")
        return None

    def wait_random(self, min_sec=1, max_sec=3):
        sleep(random.uniform(min_sec, max_sec))

    def click_any_bt(self, elem: Locator):
        for _ in range(3):
            try:
                sleep(random.uniform(1, 3))
                elem.wait_for(state='visible', timeout=5000)
                elem.click()
                self.logger.info('Clicked: %s', elem)
                sleep(random.uniform(1, 3))
                return
            except:
                self.logger.warning('Failed to click bt. Retrying... %s', elem)

    def clean_text(self, text):
        text = re.sub(r'[,.]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text

    def fill_input_dropdown(self, select, target):
        selector_options = select.locator('option').all_text_contents()
        self.logger.info(selector_options)

        try:
            index = selector_options.index(target)
        except ValueError:
            self.logger.warning("Option not found: %s", target)
            sys.exit()

        selector_target = selector_options[index]
        self.logger.info(selector_target)
        select.select_option(selector_target)
        self.wait_random(2, 6)


    def branch_selection_part(self):
        self.wait_random(2, 5)
        try:
            self.click_any_bt(self.page.locator("button:has-text('Alle akzeptieren')").first)
            self.logger.info("Cookies accepted")
        except:
            self.logger.warning("No cookies found")

        self.logger.info("\n###### Branch Selection ######\n")
        location_input = self.page.locator("#locationSearchInput").first
        location_input.click()
        self.page.keyboard.press('Control+a')

        for char in self.data['pin_code']:
            self.page.keyboard.type(char)
            sleep(random.uniform(0.1, 0.5))

        self.logger.info('Waiting for branch entries to load...')
        branch_loaded = False

        for i in range(3):
            self.page.keyboard.press('Enter')
            try:
                self.page.locator('.branch-list-entry').first.wait_for(state='visible', timeout=30000)
                self.logger.info('Branch entries loaded successfully!')
                branch_loaded = True
                sleep(0.5)
                break
            except TimeoutError:
                self.logger.warning('Branch entries did not loaded. Retrying...')

        if not branch_loaded:
            self.logger.warning('Exiting the Script...')
            sys.exit()

        self.click_any_bt(self.page.locator('.branch-list-entry').first)

    def service_selection_part(self):
        self.logger.info("\n###### Service Selection ######\n")
        self.wait_random(3, 6)
        self.click_any_bt(self.page.locator('.more-entries').first)
        vehicle_details_filled = False

        def choose_service_group(service_G_name):
            nonlocal vehicle_details_filled

            services_group_list = self.page.locator('.service-name.group').all()
            services_group_name = self.page.locator('.service-name.group').all_text_contents()
            self.logger.info(services_group_name)
            self.logger.info(f'Choosing service group: {service_G_name}')

            try:
                n = services_group_name.index(service_G_name)
            except:
                self.logger.error(f"Service name not found: {service_G_name}")
                sys.exit()

            services_group_list[n].click()
            self.wait_random(2, 5)

        def fill_vehicle_details():
            nonlocal vehicle_details_filled
            self.logger.info('\nService page type 1')
            self.wait_random(2, 3)

            input_field = self.page.locator("select").all()
            manufacturer = input_field[0]
            model = input_field[1]
            year = input_field[2]

            self.fill_input_dropdown(manufacturer, self.data["target_manufacturer"])
            self.fill_input_dropdown(model, self.data["target_model"])
            self.fill_input_dropdown(year, self.data["target_year"])

            self.click_any_bt(self.page.get_by_text("Speichern und weiter").first)
            self.wait_random(3, 6)
            vehicle_details_filled = True

        target_service_group = self.data["target_service_group"][0]
        choose_service_group(target_service_group)

        if target_service_group in ['Ölwechsel', 'Inspektion', 'Achsvermessung', 'Bremsen', 'Fahrwerk', 'Zahnriemen']:
            fill_vehicle_details()

        def choose_service_name(s_name, qty=1):
            services_page = self.page.locator('.service-list').all()
            self.logger.info(len(services_page))
            self.logger.info('Service page type 2')

            try:
                service_list = services_page[-1].locator('h3.service-name').all()
                s_list = services_page[-1].locator('h3.service-name').all_text_contents()
                self.logger.info(s_list)
                self.logger.info(f'Choosing service: {s_name}')

                for n, s in enumerate(s_list):
                    if self.clean_text(s) == self.clean_text(s_name):
                        self.logger.info(f"Selecting: {n}, {s}")
                        break
                else:
                    n = 0
                    self.logger.warning(f"Name not found, Selecting first service...")

                service_list[n].click()
            except:
                self.logger.error("Service name not found")

            try:
                quantity = self.page.locator('select[name="service-amount"]').first
                quantity.wait_for(state='visible', timeout=5000)
                quantity.select_option(qty)
                self.logger.info(f'Quantity changed to {qty}')
            except:
                self.logger.warning('Quantity field not found')
                pass

            self.click_any_bt(self.page.locator('.btn.btn-primary.btn-addService').first)
            self.wait_random(2, 5)

        # Case 1: Service Group - HU/AU
        if target_service_group == 'HU/AU':
            if self.data['engine'] == "electric":
                choose_service_name("HU für E-Fahrzeuge")
            
            elif self.data['engine'] == 'fuel':
                choose_service_name("HU/AU")
    
        else:
            choose_service_name(self.data['service_name'][0], self.data['quantity_amount'])

        if len(self.data['service_name']) > 1:
            for i in range(1, len(self.data['target_service_group'])):
                self.click_any_bt(self.page.get_by_text("Service hinzufügen").first)
                choose_service_group(self.data['target_service_group'][i])

                if self.data['target_service_group'][i] in ['Ölwechsel', 'Inspektion', 'Achsvermessung', 'Bremsen', 'Fahrwerk', 'Zahnriemen']:
                    if not vehicle_details_filled:
                        self.logger.info('Need to fill vehicle details first')
                        fill_vehicle_details()

                choose_service_name(self.data['service_name'][i], self.data['quantity_amount'])

        self.click_any_bt(self.page.locator('.btn.btn-primary.next').first)

    def appointment_selection_part(self):
        self.logger.info("\n###### Appointment Section ######\n")
        self.wait_random(4, 6)

        def fill_date_dropdown(select, target):
            selector_options = select.locator('option').all_text_contents()
            self.logger.info(selector_options)

            for opt in selector_options:
                if target in opt:
                    self.logger.info("Option found %s", opt)
                    index = selector_options.index(opt)
                    break
            else:
                index = 1
                self.logger.warning("Option not found %s", target)
                self.logger.warning('Choosing first option instead, %s', selector_options[index])

            selector_target = selector_options[index]
            self.logger.info(selector_target)
            select.select_option(selector_target)
            self.wait_random(5, 10)

        date_selection = self.page.locator('select[aria-label="Tagauswahl"]').first
        try:
            fill_date_dropdown(date_selection, self.data["target_date"])
        except:
            self.logger.warning('Date Selection Error, keeping the default date')

        self.click_any_bt(self.page.locator(".btn.btn-primary.btn-big").first)

    def your_data_section(self):
        self.logger.info("\n###### Your Data Section ######\n")
        self.wait_random(2, 4)

        for id_, value in self.data['your_data'].items():
            self.logger.info('Filling %s', id_)
            location_input = self.page.locator(f"#{id_}").first
            location_input.click()
            self.page.keyboard.press('Control+a')

            for char in value:
                self.page.keyboard.type(char)
                sleep(random.uniform(0.1, 0.4))

    def find_fleetlink_services(self):
        df = pd.read_excel(self.input_file)
        df.dropna(subset=["FleetLink ID"], inplace=True)
        fleetlink_found = False

        self.logger.info(f"FleetLink ID : {self.data['id_target']}")

        for id_ in self.data["id_target"]:
            for index, row in df.iterrows():
                fleetlink_id = row["FleetLink ID"]
                if fleetlink_id:
                    if isinstance(fleetlink_id, str):
                        fleetlink_id = [int(_.replace('?', '')) for _ in fleetlink_id.split("|")]
                    elif isinstance(fleetlink_id, int):
                        fleetlink_id = [fleetlink_id]

                if id_ in fleetlink_id:
                    self.data['target_service_group'].append(row["Service Gruppe"].strip())
                    self.data['service_name'].append(row["ATU Service"].strip())

                    self.logger.info(
                        f"Row {index+2:<4} | Service Gruppe: {row['Service Gruppe']:<20} | ATU Service: {row['ATU Service']}")
                    fleetlink_found = True

        if not fleetlink_found:
            self.logger.error("Service not found for FleetLink ID: %s", self.data["id_target"])
            sys.exit(1)

    def run(self):
        
        self.logger.info("Scraper started with data: %s", self.data)
        self.find_fleetlink_services()
        self.logger.info("Starting ATU automation...")


        self.page = self.launch_driver(self.BROWSER_TYPE, self.HEADLESS)
        self.page.goto("https://www.atu.de/terminvereinbarung/", timeout=60000)
        self.logger.info("Page loaded successfully")

        self.branch_selection_part()
        self.service_selection_part()
        self.appointment_selection_part()
        self.your_data_section()

        # Full-page screenshot
        self.page.screenshot(path=f"screenshots/{self.timestamp}.png", full_page=True)
    
        self.logger.info('Script completed.')
        self.page.close()


if __name__ == "__main__":
    test_data = {
        "pin_code": "64347",
        "id_target": [26],
        "target_service_group": [],
        "service_name": [],
        "target_manufacturer": "FORD",
        "target_model": "KA",
        "target_year": "2011",
        "quantity_amount": "1",
        "target_date": "12.06.2025",
        "engine": "electric", # electric/fuel

        "your_data": {
            "firstName": "Dominik",
            "lastName": "Skakuj",
            "email": "dominik.skakuj1234@gmail.com",
            "mobile": "11111111111",
            "Erreichbarkeit": "",
            "licensePlate": "Da HI 2001",
            "HSN": "",
            "TSN": "",
            "mileage": "",
            "Radeinlagerungsnummer": "",
            "Firmenname": "",
            "Kundennummer": "",
            "Anmerkung": ""
        },
    }

    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    scraper = ATUScraper(test_data, timestamp)
    scraper.run()


