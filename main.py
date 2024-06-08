from pyswip import Prolog
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

class Driver():
    def __init__(self):
        service = Service()
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=770,820")
        options.add_argument("--window-position=0,0")
        options.add_argument("--log-level=3")
        self.driver = webdriver.Chrome(service=service, options=options)

    def close(self):
        self.driver.close()

    def get(self, url):
        self.driver.get(url)

    def scrape_nonogram(self, size):
        if size == "5":
            url = "https://www.puzzle-nonograms.com/"
        elif size == "10":
            url = "https://www.puzzle-nonograms.com/?size=1"
        elif size == "15":
            url = "https://www.puzzle-nonograms.com/?size=2"
        elif size == "20":
            url = "https://www.puzzle-nonograms.com/?size=3"
        elif size == "25":
            url = "https://www.puzzle-nonograms.com/?size=4"
        elif size == "30":
            url = "https://www.puzzle-nonograms.com/?size=6"
        elif size == "50":
            url = "https://www.puzzle-nonograms.com/?size=7"
        self.driver.get(url)
        print("Getting puzzle representation...")
        time.sleep(1)
        self.driver.execute_script("arguments[0].scrollIntoView();", self.driver.find_element(By.ID, "puzzleContainerRalativeDiv"))
        # had to use BS because selenium had some loading issue where it wasn't getting last rows
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        cols_hints = soup.select("#taskTop .task-group")
        rows_hints = soup.select("#taskLeft .task-group")
        rows = []
        cols = []
        for group in cols_hints:
            hint = []
            cells = group.select(".selectable")
            for cell in cells:
                hint.append(int(cell.text))
            cols.append(hint)
        for group in rows_hints:
            hint = []
            cells = group.select(".selectable")
            for cell in cells:
                hint.append(int(cell.text))
            rows.append(hint)
        return rows, cols
        
    def fill_nonogram(self, solved):
        cells = self.driver.find_elements(By.CSS_SELECTOR, ".row .cell.selectable")
        # print(len(cells))
        for i, row in enumerate(solved):
            for j, value in enumerate(row):
                index = i * len(row) + j
                cell = cells[index]
                # self.driver.execute_script(f"Game.currentState.cellStatus[{i}][{j}] = 1;")
                if value == 0 or "cell-on" in cell.get_attribute("class"):
                    pass
                else:
                    self.driver.execute_script(f"arguments[0].setAttribute('class', 'cell selectable cell-on')", cell)
                    self.driver.execute_script(f"Game.currentState.cellStatus[{i}][{j}] = 1;")

# # Click on the element using JavaScript
#                 self.driver.execute_script("arguments[0].click();", cell)


def solve_nonogram(rows, cols):
    prolog = Prolog()
    prolog.consult("nono.pl")
    solved = list(prolog.query(f"nono([{rows}, {cols}], Grid)"))[0]['Grid']
    return solved


def main():
    driver = None
    while True:
        command = input("Type 'start', 'example', or 'quit': ")
        if command.lower() == "start":
            if not driver:
                driver = Driver()
                driver.get("https://www.puzzle-nonograms.com/")
                time.sleep(1)
            while True:
                size = input("Choose a puzzle size ('5', '10', '15', '20', '25', '30', '50'): ")
                if size in ["5", "10", "15", "20", "25", "30", "50"]:
                    break
                else:
                    print("Invalid puzzle size.")
            rows, cols = driver.scrape_nonogram(size)
            is_solved = False
            while True:
                if is_solved:
                    command = input("Type 'solve', 'fill', or 'return': ")
                else:
                    command = input("Type 'solve' or 'return': ")
                if command.lower() == "solve":
                    solved = solve_nonogram(rows, cols)
                    is_solved = True
                elif command.lower() == "fill":
                    driver.fill_nonogram(solved)
                elif command.lower() == "return":
                    break
        elif command.lower() == "example":
            while True:
                example = input("Choose an example # (1-...) or 'return': ")
                if example == "1":
                    solve_nonogram([[2], [4], [6], [4, 3], [5, 4], [2, 3, 2], [3, 5], [5], [3], [2], [2], [6]],
                                  [[3], [5], [3, 2, 1], [5, 1, 1], [12], [3, 7], [4, 1, 1, 1], [3, 1, 1], [4], [2]])
                # TODO: any specific ones we want to check, e.g. multi-solutioned, no solution
                elif example == "2":
                    pass
                elif example == "return":
                    break
                else:
                    print("Invalid example.")
                
        elif command.lower() == "quit":
            if driver:
                driver.close()
            print("Exiting the program.")
            break
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()