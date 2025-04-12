import os
import sys
from enum import Enum
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from functions import set_as_new_assurance_user, set_as_new_loan_user
import time


@dataclass
class TestConfig:
    message: str
    dispatch: Callable[[], Any]


class MenuType(Enum):
    USER_TYPE = "USER_TYPE"
    MAIN = "MAIN"
    API = "API"
    SELENIUM = "SELENIUM"


class MenuItem:
    def __init__(self, key: str, display_text: str):
        self.key = key
        self.display_text = display_text

    def to_dict(self) -> Dict[str, str]:
        return {self.key: self.display_text}


class MenuConfig:
    def __init__(self):
        self.menus: Dict[MenuType, List[MenuItem]] = {
            MenuType.USER_TYPE: [
                MenuItem("init", "\n=== User Type Selection ==="),
                MenuItem("NEW_USER", "1. New User Test"),
                MenuItem("EXISTING_USER", "2. Existing User Test"),
                MenuItem("END", "========================")
            ],
            MenuType.MAIN: [
                MenuItem("init", "\n=== Test Execution Menu ==="),
                MenuItem("API", "1. API Test"),
                MenuItem("SELENIUM", "2. Selenium Test"),
                MenuItem("BACK", "3. Back"),
                MenuItem("EXIT", "4. Exit"),
                MenuItem("END", "========================")
            ],
            MenuType.API: [
                MenuItem("init", "\n=== API Test Menu ==="),
                MenuItem("LOAN_TEST", "1. Run Loan Flow API Test"),
                MenuItem("ASSURANCE_TEST", "2. Run Assurance Flow API Test"),
                MenuItem("BACK_API", "3. Back"),
                MenuItem("END", "========================")
            ],
            MenuType.SELENIUM: [
                MenuItem("init", "\n=== Selenium Test Menu ==="),
                MenuItem("LOAN_SEL", "1. Run Loan Flow Selenium Test"),
                MenuItem("ASSURANCE_SEL",
                         "2. Run Assurance Flow Selenium Test"),
                MenuItem("BACK_SEL", "3. Back"),
                MenuItem("END", "========================")
            ]
        }

    def get_menu_items(self, menu_type: MenuType) -> List[Dict[str, str]]:
        return [item.to_dict() for item in self.menus[menu_type]]


class TestRunner:
    def __init__(self):
        self.tests: Dict[str, TestConfig] = {
            "user_login_py": TestConfig(
                message="\nRunning User Login Test...",
                dispatch=lambda: os.system("pytest test_lend_user_login.py -s")
            ),
            "loan_flow_py": TestConfig(
                message="\nRunning Loan Flow Test...",
                dispatch=lambda: os.system(
                    "pytest test_lend_loan_flow_from_zero.py")
            ),
            "assurance_flow_py": TestConfig(
                message="\nRunning Assurance Flow Test...",
                dispatch=lambda: os.system(
                    "pytest test_lend_assurance_flow_from_zero.py")
            ),
            "loan_flow_sel": TestConfig(
                message="\nRunning Loan Flow Test...",
                dispatch=lambda: os.system(
                    "python sel_lend_loan_flow_from_zero.py")
            ),
            "assurance_flow_sel": TestConfig(
                message="\nRunning Assurance Flow Test...",
                dispatch=lambda: os.system(
                    "python sel_lend_assurance_flow_from_zero.py")
            ),
            "new_user_setup": TestConfig(
                message="\nSetting up new user...",
                dispatch=lambda: self.setup_new_user()
            )
        }

    def run_test(self, test_name: str) -> None:
        if test_name in self.tests:
            test = self.tests[test_name]
            print(test.message)
            test.dispatch()
        else:
            print(f"Test {test_name} not found")

    def setup_new_user(self) -> None:
        set_as_new_loan_user()
        set_as_new_assurance_user()


class Menu:
    def __init__(self):
        self.menu_config = MenuConfig()
        self.test_runner = TestRunner()
        self.is_new_user = False

    def display_menu(self, menu_type: MenuType) -> str:
        menu_items = self.menu_config.get_menu_items(menu_type)
        for item in menu_items:
            print(*list(item.values()))
        return input(f"\nEnter your choice (1-{len(menu_items)- 2}): ")

    def handle_api_menu(self) -> None:
        # First run user login test
        self.test_runner.run_test("user_login_py")

        choice = self.display_menu(MenuType.API)
        if choice == '1':
            self.test_runner.run_test("loan_flow_py")
        elif choice == '2':
            self.test_runner.run_test("assurance_flow_py")
        elif choice == '3':
            print("\nReturning to main menu...")
        else:
            print("\nInvalid choice! Please try again.")

    def handle_selenium_menu(self) -> None:
        choice = self.display_menu(MenuType.SELENIUM)
        if choice == '1':
            self.test_runner.run_test("loan_flow_sel")
        elif choice == '2':
            self.test_runner.run_test("assurance_flow_sel")
        elif choice == '3':
            print("\nReturning to main menu...")
        else:
            print("\nInvalid choice! Please try again.")

    def handle_user_type_menu(self) -> None:
        user_type_choice = self.display_menu(MenuType.USER_TYPE)
        while user_type_choice not in ('1', '2'):
            print("\nInvalid choice! Please try again.")
            user_type_choice = self.display_menu(MenuType.USER_TYPE)

        if user_type_choice == '1':
            self.is_new_user = True
            self.test_runner.run_test("new_user_setup")
        elif user_type_choice == '2':
            self.is_new_user = False

    def run(self) -> None:
        self.handle_user_type_menu()
        choice = self.display_menu(MenuType.MAIN)
        while choice != '4':
            if choice == '1':
                self.handle_api_menu()
            elif choice == '2':
                self.handle_selenium_menu()
            elif choice == '3':
                self.handle_user_type_menu()
            else:
                print("\nInvalid choice! Please try again.")
            choice = self.display_menu(MenuType.MAIN)

        print("\n Exit Program ...")
        sys.exit(0)


def main():
    menu = Menu()
    menu.run()


if __name__ == "__main__":
    main()
