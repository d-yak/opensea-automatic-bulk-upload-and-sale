#!/usr/bin/python
# app/services/wallets/metamask.py


"""
@author: Maxime Dréan.

Github: https://github.com/maximedrn
Telegram: https://t.me/maximedrn

Copyright © 2022 Maxime Dréan. All rights reserved.
Any distribution, modification or commercial use is strictly prohibited.
"""


# Selenium module imports: pip install selenium
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as WDW
from selenium.common.exceptions import TimeoutException as TE

# Python internal imports.
from ...utils.colors import GREEN, RED, RESET


class MetaMask:

    def __init__(self, web: object, wallet: object) -> None:
        self.fails = 0  # Counter of fails during wallet connection.
        # Get the instance of the needed classes.
        self.web = web  # From the Webdriver class.
        self.wallet = wallet  # From the Wallet class.

    def login(self) -> bool:
        """Login to the MetaMask extension."""
        try:  # Try to login to the MetaMask extension.
            print('Login to MetaMask.', end=' ')
            self.web.window_handles(0)  # Switch to the MetaMask extension tab.
            self.web.driver.refresh()  # Reload the page to prevent a blank page.
            # Click on the "Start" button.
            self.web.clickable('//*[@class="welcome-page"]/button')
            # Click on the "Import wallet" button.
            self.web.clickable('//*[contains(@class, "btn-primary")][position()=1]')
            # Click on the "I agree" button.
            self.web.clickable('//footer/button[2]')
            # Input the recovery phrase.
            self.web.send_keys('//input[position()=1]', self.wallet.recovery_phrase)
            # Input a new password or the same password of your account.
            self.web.send_keys('//*[@id="password"]', self.wallet.password)
            self.web.send_keys('//*[@id="confirm-password"]', self.wallet.password)
            # Click on the "I have read and agree to the..." checkbox.
            self.web.clickable('(//*[@role="checkbox"])[2]')
            # Click on the "Import" button.
            self.web.clickable('//*[contains(@class, "btn-primary")][position()=1]')
            # Wait until the login worked and click on the "All done" button.
            self.web.visible('//*[contains(@class, "emoji")][position()=1]')
            self.web.clickable('//*[contains(@class, "btn-primary")][position()=1]')
            if self.wallet.private_key != '':  # Change account.
                self.web.clickable('//button[@data-testid="popover-close"]')
                self.web.clickable('//*[@class="account-menu__icon"][position()=1]')
                self.web.clickable('//*[contains(@class, "account-menu__item--'
                              'clickable")][position()=2]')
                self.web.send_keys('//*[@id="private-key-box"]', self.wallet.private_key)
                self.web.clickable('//*[contains(@class, "btn-secondary")]'
                              '[position()=1]')
            print(f'{GREEN}Logged to MetaMask.{RESET}')
            self.wallet.success = True
        except Exception:  # Failed - a web element is not accessible.
            self.fails += 1  # Increment the counter.
            if self.fails < 2:  # Retry login to the MetaMask.
                print(f'{RED}Login to MetaMask failed. Retrying.{RESET}')
                self.login()
            else:  # Failed twice - the wallet is not accessible.
                print(f'{RED}Login to MetaMask failed. Restarting.{RESET}')
                self.web.quit()  # Stop the webdriver.
                self.wallet.success = False

    def sign(self, contract: bool = True, page: int = 2) -> None:
        """Sign the MetaMask contract to login to OpenSea."""
        windows = self.web.driver.window_handles  # Opened windows.
        for _ in range(page):  # "Next" and "Connect" buttons.
            self.web.window_handles(2)  # Switch to the MetaMask pop up tab.
            self.web.clickable('//*[contains(@class, "btn-primary")]')
        if contract:
            WDW(self.web.driver, 10).until(  # Wait for the new MetaMask tab.
                lambda _: windows != self.web.driver.window_handles)
            self.contract()  # Sign the contract.

    def contract(self, new_contract: bool = False) -> None:
        """Sign a MetaMask contract to upload or confirm sale."""
        self.web.window_handles(2)  # Switch to the MetaMask pop up tab.
        if self.web.window == 1 and new_contract:  # GeckoDriver.
            self.web.clickable('(//div[contains(@class, "signature") and '
                          'contains(@class, "scroll")])[position()=1]')
        elif self.web.window == 0 and new_contract:
            self.web.driver.execute_script(  # Scroll down.
                'window.scrollTo(0, document.body.scrollHeight);')
        # Click on the "Sign" button - Make a contract link.
        self.web.clickable('(//div[contains(@class, "signature") and conta'
                      'ins(@class, "footer")])[position()=1]/button[2]')
        try:  # Wait until the MetaMask pop up is closed.
            WDW(self.web.driver, 10).until(EC.number_of_windows_to_be(2))
        except TE:
            self.contract()  # Sign the contract a second time.
        self.web.window_handles(1)  # Switch back to the OpenSea tab.

    def close(self) -> None:
        """Close the MetaMask popup."""
        if len(self.web.driver.window_handles) > 2:
            try:
                self.web.window_handles(2)  # Switch to the MetaMask popup.
                self.web.driver.close()  # Close the popup extension.
                self.web.window_handles(1)  # Switch back to OpenSea.
            except Exception:
                pass  # Ignore the exception.
