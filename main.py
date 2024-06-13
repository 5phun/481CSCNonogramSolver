from pyswip import Prolog
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from multiprocessing import Pool
from collections import defaultdict


NUM_TESTS = 500


class Driver():
    # init with chromedriver
    def __init__(self, mode = None):
        service = Service()
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=770,820")
        options.add_argument("--window-position=0,0")
        options.add_argument("--log-level=3")
        # if testing, use headless mode
        if mode == "test":
            options.add_argument("--headless")
        self.driver = webdriver.Chrome(service=service, options=options)

    # close driver
    def close(self):
        self.driver.close()

    # update url of driver
    def get(self, url):
        self.driver.get(url)

    # update url according to size, then scrape and return hints
    def scrape_nonogram(self, size, mode = None):
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
        if mode == None:
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
        # if testing, get the puzzle id as well
        if mode == "test":
            id = soup.select_one("#puzzleID").text
            return rows, cols, id
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


# calls prolog file to solve, used for singular examples
def solve_nonogram(rows, cols):
    prolog = Prolog()
    prolog.consult("nono.pl")
    solved = list(prolog.query(f"nono([{rows}, {cols}], Grid)"))
    if solved == []:
        print("No solution found.")
        return None
    return solved[0]['Grid']

# scrapes and call prolog file to solve and time, used for collecting times for test
def time_puzzle(size):
    fail_count = 0
    success_count = 0
    times = defaultdict(lambda: None)
    # open a new driver
    driver = Driver(mode="test")
    try:
        while success_count < NUM_TESTS:
            # scrape rows, cols, and id
            rows, cols, id = driver.scrape_nonogram(size, mode="test")
            # check if already tested this puzzle
            if times[id] is not None:
                continue
            # use prolog to solve and time 
            prolog = Prolog()
            prolog.consult("nono.pl")
            solved = list(prolog.query(f"nono_timed([{rows}, {cols}], Time, Grid)"))
            # increment fail count if ever fails, should never happen
            if solved == []:
                fail_count += 1
            else:
                time = solved[0]['Time']
                solved = solved[0]['Grid']
            # if solved, add to times
            if solved is not None:
                times[id] = time
                success_count += 1
                print(f"{id} ({size}x{size} solved in: {time}")
        if fail_count != 0:
            print("Failed:", fail_count, "times")
        # change to list of tuples (fix for pickling error)
        return [(key, value) for key, value in times.items()]
    # close the driver
    finally:
        driver.close()


def main():
    driver = None
    while True:
        command = input("Type 'start', 'example', 'test', or 'quit': ").lower()
        # open/update driver to scrape a puzzle
        if command == "start":
            if not driver:
                driver = Driver()
                driver.get("https://www.puzzle-nonograms.com/")
                time.sleep(1)
            while True:
                # choose a puzzle size
                size = input("Choose a puzzle size ('5', '10', '15', '20', '25', '30', or '50'): ")
                if size in ["5", "10", "15", "20", "25", "30", "50"]:
                    break
                else:
                    print("Invalid puzzle size.")
            rows, cols = driver.scrape_nonogram(size)
            print(rows)
            print(cols)
            is_solved = False
            while True:
                # choose to fill or return if solved
                if is_solved:
                    command = input("Type 'fill' or 'return': ").lower()
                    if command == "fill":
                        driver.fill_nonogram(solved)
                        break
                # choose to solve or return if not solved (just scraped)
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
                example = input("Choose an example # (1-6) or 'return': ").lower()
                # working
                if example == "1":
                    solve_nonogram([[2], [4], [6], [4, 3], [5, 4], [2, 3, 2], [3, 5], [5], [3], [2], [2], [6]],
                               [[3], [5], [3, 2, 1], [5, 1, 1], [12], [3, 7], [4, 1, 1, 1], [3, 1, 1], [4], [2]])
                # failing, bad first column
                elif example == "2":
                    solve_nonogram([[3], [4], [6], [4, 3], [5, 4], [2, 3, 2], [3, 5], [5], [3], [2], [2], [6]],
                               [[3], [5], [3, 2, 1], [5, 1, 1], [12], [3, 7], [4, 1, 1, 1], [3, 1, 1], [4], [2]])
                # multiple solutions
                elif example == "3":
                    solve_nonogram([[1], [1]], [[1], [1]])
                # more complex multiple solutions
                elif example == "4":
                    solve_nonogram([[4],[3],[2,1],[1,3],[1,1],[3],[2]], 
                                   [[4],[3],[2,1],[1,3],[1,1],[3],[2]])
                # TODO: any specific ones we want to check, e.g. multi-solutioned, no solution, larger
                elif example == "5":
                    # Sunflower
                    solve_nonogram([[],
                                    [2, 3],
                                    [1, 1, 1],
                                    [1, 1, 4],
                                    [8, 1],
                                    [5, 2, 2],
                                    [1, 2, 2, 1],
                                    [2, 1, 1, 1, 1, 1],
                                    [1, 1, 5],
                                    [1, 1, 1, 1, 3],
                                    [4, 2, 2, 1, 1],
                                    [3, 2, 2, 1],
                                    [1, 2, 2, 3],
                                    [2, 4, 1],
                                    [3, 1, 2, 2, 1],
                                    [1, 1, 3, 2],
                                    [2, 1, 2],
                                    [6],
                                    [1, 1, 2],
                                    [2, 2, 1],
                                    [2, 4],
                                    [2],
                                    [1],
                                    [2],
                                    [1]],
                                   [[2],
                                    [1],
                                    [1],
                                    [1],
                                    [2],
                                    [2],
                                    [3, 1],
                                    [4, 1, 1, 1],
                                    [3, 1, 2, 1],
                                    [1, 4, 2],
                                    [7, 1, 1],
                                    [5, 2, 2, 1],
                                    [1, 2, 2, 1, 5],
                                    [1, 1, 1, 1, 5, 2],
                                    [1, 1, 1, 2, 1, 1],
                                    [1, 1, 1, 1, 1, 1],
                                    [1, 1, 1, 1, 2, 2],
                                    [5, 2, 1, 2],
                                    [3, 2, 1],
                                    [1, 6, 1],
                                    [1, 2, 2],
                                    [1, 2, 1],
                                    [3, 1, 3],
                                    [1, 1],
                                    [2]])
                elif example == "6":
                    # Monkey
                    solve_nonogram([[9],
                                    [11],
                                    [3, 2],
                                    [2, 2, 1],
                                    [1, 5, 2, 2, 1],
                                    [1, 3, 1, 1, 2],
                                    [2, 4, 2],
                                    [6, 2, 3],
                                    [4, 3],
                                    [3, 2],
                                    [5, 1, 1],
                                    [5, 2, 2],
                                    [6, 2],
                                    [8, 2],
                                    [12]],
                                   [[3, 2],
                                    [1, 2, 3],
                                    [2, 2, 5],
                                    [11],
                                    [14],
                                    [15],
                                    [3, 1, 2, 5],
                                    [2, 2],
                                    [2, 2, 1],
                                    [2, 1, 1, 2, 1],
                                    [2, 1, 1, 1],
                                    [2, 2, 2],
                                    [2, 1, 2, 3],
                                    [3, 8],
                                    [9]])
                elif example == "return":
                    break
                else:
                    print("Invalid example.")
        # running time tests for puzzles of various sizes
        elif command == "test":
          sizes = ["5", "10", "15", "20", "25"]  # Define sizes to test
          pool = Pool(processes=len(sizes))
          async_results = [pool.apply_async(time_puzzle, args=(size,)) for size in sizes]
          pool.close()
          pool.join()
          with open("test_times", "w") as file:
              for async_result, size in zip(async_results, sizes):
                  times = async_result.get()
                  avg = sum([t[1] for t in times]) / len(times)
                  print(len(times))
                  file.write(f"{size} (average: {avg} seconds)\n{times} \n\n")

        # close the program
        elif command == "quit":
            # close all drivers
            if driver:
                driver.close()
            print("Exiting the program.")
            break
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()