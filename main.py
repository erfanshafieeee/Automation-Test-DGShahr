import os
import sys
from enum import Enum
from typing import Dict, List, Callable, Any
from dataclasses import dataclass


@dataclass
class TestConfig:
    message: str
    dispatch: Callable[[], Any]


class MenuType(Enum):
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
            MenuType.MAIN: [
                MenuItem("init", "\n=== Test Execution Menu ==="),
                MenuItem("API", "1. API Test"),
                MenuItem("SELENIUM", "2. Selenium Test"), 
                MenuItem("EXIT", "3. Exit"),
                MenuItem("END", "========================")
            ],
            MenuType.API: [
                MenuItem("init", "\n=== API Test Menu ==="),
                MenuItem("USER_LOGIN", "1. Run User Login Test (Required First)"),
                MenuItem("LOAN_TEST", "2. Run Loan Flow API Test"),
                MenuItem("ASSURANCE_TEST", "3. Run Assurance Flow API Test"),
                MenuItem("EXIT_API", "4. Exit"),
                MenuItem("END", "========================")
            ],
            MenuType.SELENIUM: [
                MenuItem("init", "\n=== Selenium Test Menu ==="),
                MenuItem("LOAN_SEL", "1. Run Loan Flow Selenium Test"),
                MenuItem("ASSURANCE_SEL", "2. Run Assurance Flow Selenium Test"),
                MenuItem("EXIT", "3. Exit"),
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
                dispatch=lambda: os.system("pytest test_lend_loan_flow_from_zero.py")
            ),
            "assurance_flow_py": TestConfig(
                message="\nRunning Assurance Flow Test...",
                dispatch=lambda: os.system("pytest test_lend_assurance_flow_from_zero.py")
            ),
            "loan_flow_sel": TestConfig(
                message="\nRunning Loan Flow Test...",
                dispatch=lambda: os.system("python sel_lend_loan_flow_from_zero.py")
            ),
            "assurance_flow_sel": TestConfig(
                message="\nRunning Assurance Flow Test...",
                dispatch=lambda: os.system("python sel_lend_assurance_flow_from_zero.py")
            )
        }

    def run_test(self, test_name: str) -> None:
        if test_name in self.tests:
            test = self.tests[test_name]
            print(test.message)
            test.dispatch()
        else:
            print(f"Test {test_name} not found")


class Menu:
    def __init__(self):
        self.menu_config = MenuConfig()
        self.test_runner = TestRunner()

    def display_menu(self, menu_type: MenuType) -> str:
        menu_items = self.menu_config.get_menu_items(menu_type)
        for item in menu_items:
            print(*list(item.values()))
        return input(f"\nEnter your choice (1-{len(menu_items)- 2}): ")

    def handle_api_menu(self) -> None:
        choice = self.display_menu(MenuType.API)
        if choice == '1':
            self.test_runner.run_test("user_login_py")
        elif choice == '2':
            self.test_runner.run_test("loan_flow_py")
        elif choice == '3':
            self.test_runner.run_test("assurance_flow_py")
        elif choice == '4':
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

    def run(self) -> None:
        while True:
            choice = self.display_menu(MenuType.MAIN)
            if choice == '1':
                self.handle_api_menu()
            elif choice == '2':
                self.handle_selenium_menu()
            elif choice == '3':
                print("\nExiting program...")
                sys.exit(0)
            else:
                print("\nInvalid choice! Please try again.")


def main():
    menu = Menu()
    menu.run()


if __name__ == "__main__":
    main()
