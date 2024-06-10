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
    # init with chromedriver
    def __init__(self):
        service = Service()
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=770,820")
        options.add_argument("--window-position=0,0")
        options.add_argument("--log-level=3")
        self.driver = webdriver.Chrome(service=service, options=options)

    # close driver
    def close(self):
        self.driver.close()

    # update url of driver
    def get(self, url):
        self.driver.get(url)

    # update url according to size, then scrape and return hints
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
        # get hints for columns
        for group in cols_hints:
            hint = []
            cells = group.select(".selectable")
            for cell in cells:
                hint.append(int(cell.text))
            cols.append(hint)
        # get hints for rows
        for group in rows_hints:
            hint = []
            cells = group.select(".selectable")
            for cell in cells:
                hint.append(int(cell.text))
            rows.append(hint)
        return rows, cols
        
    # fill the grid on the site according to the solved cells
    def fill_nonogram(self, solved):
        # get cells
        cells = self.driver.find_elements(By.CSS_SELECTOR, ".row .cell.selectable")
        # loop solved cells along with corresponding cells on site
        for i, row in enumerate(solved):
            for j, value in enumerate(row):
                index = i * len(row) + j
                cell = cells[index]
                class_name = cell.get_attribute("class")
                # if the cell should be empty and it is filled, make it empty
                if value == 0 and "cell-on" in class_name:
                    self.driver.execute_script(f"arguments[0].setAttribute('class', 'cell selectable cell-off'); Game.currentState.cellStatus[{i}][{j}] = 0;", cell)
                # if the cell should be filled and it is empty, make it filled
                elif value == 1 and "cell-off" in class_name:
                    self.driver.execute_script(f"arguments[0].setAttribute('class', 'cell selectable cell-on'); Game.currentState.cellStatus[{i}][{j}] = 1;", cell)


# call prolog file to solve
def solve_nonogram(rows, cols):
    prolog = Prolog()
    prolog.consult("nono.pl")   
    #handling no solution nonograms
    try:
        solved = list(prolog.query(f"nono([{rows}, {cols}], Grid)"))[0]['Grid']
    except IndexError: 
        print("No solution")
        solved = []
    return solved


def main():
    driver = None
    while True:
        command = input("Type 'start', 'example', or 'quit': ").lower()
        # open/update driver to scrape a puzzle
        if command == "start":
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
                    command = input("Type 'fill' or 'return': ").lower()
                    if command == "fill":
                        driver.fill_nonogram(solved)
                        break
                else:
                    command = input("Type 'solve' or 'return': ").lower()
                    if command == "solve":
                        solved = solve_nonogram(rows, cols)
                        is_solved = True
                if command == "return":
                    break
                if command not in ["fill", "solve"]:
                    print("Invalid command.")
        # choose from examples
        elif command == "example":
            while True:
                example = input("Choose an example # (1-...) or 'return': ").lower()
                if example == "1":
                    solve_nonogram([[2], [4], [6], [4, 3], [5, 4], [2, 3, 2], [3, 5], [5], [3], [2], [2], [6]],
                                  [[3], [5], [3, 2, 1], [5, 1, 1], [12], [3, 7], [4, 1, 1, 1], [3, 1, 1], [4], [2]])
                # TODO: any specific ones we want to check, e.g. multi-solutioned, no solution
                elif example == "2":
                    #simple multi solution
                    solve_nonogram([[1],[1]], [[1],[1]])
                elif example == "3":
                    #more complex multi solution
                    solve_nonogram([[4],[3],[2,1],[1,3],[1,1],[3],[2]], 
                                   [[4],[3],[2,1],[1,3],[1,1],[3],[2]])
                elif example == "4":
                    #no solution, prolog.query(f"nono([{rows}, {cols}], Grid)") returns [] so this causes an error in the function
                    solve_nonogram([[2],[2]], [[2],[1]])
                elif example == "return":
                    break
                else:
                    print("Invalid example.")
        # close the program
        elif command == "quit":
            if driver:
                driver.close()
            print("Exiting the program.")
            break
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()