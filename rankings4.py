from selenium import webdriver
from bs4 import BeautifulSoup as bs
import os
from tkinter import *

_dict = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'A': 10, 'B': 11, 'C': 12}


class Window:

    def __init__(self, text):
        self.window = Tk()
        self.label = Label(self.window, width=75, height=10)
        self.label.pack()
        self.label['text'] = text
        self.window.update()

    def quit(self):
        self.window.destroy()


class Mainwindow(Window):

    def __init__(self, text, path_to_result):
        Window.__init__(self, text)
        self.button = Button(self.window, text='Output Folder', fg='white', bg='blue',
                             command=lambda: self.openoutput(path_to_result))
        self.button.pack()
        self.window.mainloop()

    def openoutput(self, path_to_result):
        os.startfile(path_to_result)
        self.window.quit()


class Ranking:

    def __init__(self):
        self.data = {}

    def update(self, number, students_dict, total_sems, path_to_result):
        for roll_number, values in students_dict.items():
            if roll_number in self.data:
                self.data[roll_number][1] = str(float(self.data[roll_number][1])+float(values[1]))
                self.data[roll_number][2] += 1
            else:
                self.data[roll_number] = values
        if number == total_sems:
            for roll_number, values in self.data.items():
                self.data[roll_number][1] = str(round(float(values[1])/values[2], 3))
            proper_rankings('Average', self.data, path_to_result)


def proper_rankings(number, students_dict, path_to_result):
    """

    :param number: Semester number
    :param students_dict: contains details of students of section 2 like roll number,name,cgpa.
    :param path_to_result: Path to where the ranking files are placed
    :return:
            This function writes the details of students of section 2 in a file sorted by their cgpa

    """
    if not os.path.exists(path_to_result):
        os.makedirs(path_to_result)
    path_to_files = os.path.join(path_to_result, 'sem'+str(number)+'.txt')
    string = 'Rank' + 2 * ' ' + 'Roll-Number' + 22 * ' ' + 'Name' + 21 * ' ' + 'SGPA\n'
    students_dict = [(key, value) for key, value in students_dict.items()]
    students_dict.sort(key=lambda points: points[1][1], reverse=True)
    for rank, (roll_number, _list) in enumerate(students_dict, 1):
        string += '{:^5s} {:11s} {:^45s} {}\n'.format(str(rank), roll_number, _list[0], _list[1])
    with open(path_to_files, 'w') as file:
        file.write(string)


def valid_number(index, number):
    """
    :param index: Index is 0 for students whose roll number starts in  15 series and Index is 1 for students whose roll
                  number starts in 16 series
    :param number: Roll number of the student
    :return:
    1)This function is used to check if the roll number is present in the 2nd section if yes it returns 1
    2)If we still did not reach to 2nd section from roll number :- 1 it returns 0 telling our program to continue execution
    3)otherwise if it had exceeded the 2nd section roll number it returns -1 to make our program break from checking
    remaining results

    """
    number = number[-2:]
    roll_number = _dict[number[0]] * 10 + int(number[1])
    if not index:
        if roll_number < 59:
            return 0
        elif roll_number > 116:
            return -1
    elif index:
        if roll_number < 16:
            return 0
        elif roll_number > 35:
            return -1
    return 1


def main(path_to_result):
    rank = Ranking()
    links = ['http://gvpce.ac.in/results/B.Tech%20I%20Semester%20Regular%20(R-2015)_December%202015/btechsearch.asp',
             'http://gvpce.ac.in/results/B.Tech%20II%20Semester%20(Regular)%20(R-2015)_May%202016%20('
             'For%202015%20Admitted%20Batch)/btechsearch.asp',
             'http://gvpce.ac.in/results/B.Tech%20III%20Semester%20('
             'R-2015)%20Regular%20Results-October-2016/btechsearch.asp',
             'http://gvpce.ac.in/results/B.Tech%20IV%20Sem%20Regular%20%20(R-2015)%20('
             'For%202015%20%20Batch)%20Result_April,%202017/btechsearch.asp',
             'http://gvpce.ac.in/results/B.Tech%20V%20Sem%20Regular%20(R-2015)%20('
             'For%202015%20batch)%20Result_October-%202017/btechsearch.asp']
    total_sems = len(links)
    for number, link in enumerate(links, 1):
        text = 'Calculating ' + str(number) + ' Semester Results Please Wait...'
        window = Window(text)
        numbers = ['15131A05']
        if number > 2:
            numbers = ['15131A05', '16135A05']
        students = {}
        for index, _number in enumerate(numbers):
            # Path to the chromedriver.exe which the selenium package will be using
            browser = webdriver.Chrome("chromedriver.exe")
            browser.get(link)
            browser.set_window_position(-2000, 0)
            browser.find_element_by_name('u_input').send_keys(_number)
            browser.find_element_by_xpath('/html/body/form/div/table/tbody/tr/td/table/tbody/tr/td/p/input[2]').click()
            page_source = browser.page_source
            browser.quit()
            soup = bs(page_source, 'lxml')
            tables = soup.findChildren('table')
            if index == 0:
                class_tables = tables[50:115:]
            else:
                class_tables = tables[14:33:]
            for table in class_tables:
                real_values = []
                rows = table.findChildren('tr')
                row_list = [1, -2]
                roll_number = rows[0].findChildren('td')[1].string
                result = valid_number(index, roll_number)
                if result == 0:
                    continue
                elif result == -1:
                    break
                for _index in row_list:
                    value = rows[_index].findChildren('td')[1].string
                    if value is None:
                        value = '0.000'
                    real_values.append(value)
                real_values.append(1)
                students[roll_number] = real_values
        rank.update(number, students, total_sems, path_to_result)
        proper_rankings(number, students, path_to_result)
        window.quit()


if __name__ == '__main__':
    path_to_desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop\Rankings')
    main(path_to_desktop)
    result_window = Mainwindow('All Results Successfully fetched', path_to_desktop)
