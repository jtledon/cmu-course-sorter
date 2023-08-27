import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool

import re, math
import argparse, json

from pprint import pprint

# TODO:
#   Take into account location filter
#   Filter out summer classes when looking for fce average weight

parser = argparse.ArgumentParser(
                    prog='cmu-course-sorter',
                    description='Find CMU classes that fit your criteria, sorted by FCE'
                    )
parser.add_argument("-u", "--units",
                    type=int,
                    nargs="+", action="extend",
                    required=False #, default=[range(60+1)]
                    )
parser.add_argument("-d", "--department",
                    type=int, required=False,
                    nargs="+", action="extend"
                    )
parser.add_argument("-l", "--level",
                    type=int, required=False,
                    nargs="+", action="extend"
                    )
parser.add_argument("-s", "--semester",
                    type=str, required=False,
                    choices=["fall", "spring"], default="spring"
                    )
parser.add_argument("-L", "--location",
                    type=str, required=False,
                    )
parser.add_argument("--sorter",
                    type=str, required=False,
                    choices=["fce", "rating"], default="fce"
                    )
args = parser.parse_args()

class CourseInfo:
    def __init__(self, name, number, units, professor, location):
        self.name = name

        self.number = number
        self.department = self.GetDepartmentFromCourseNumber(number)
        self.level = self.GetLevelFromCourseNumber(number)

        self.units = units
        self.professor = professor
        self.location = location
        self.fce = None

    def __repr__(self):
        return f"{{ CourseNumber({self.number}) Units({self.units}) FCE({self.fce}) }}"
    
    # @classmethod
    @staticmethod
    def GetDepartmentFromCourseNumber(course_number):
        return int(course_number[0:1+1]) 

    @staticmethod
    def GetLevelFromCourseNumber(course_number):
        return int(course_number[2]) 

    def SetFCE(self, fce):
        self.fce = fce
        return

    def GetFCE(self):
        return self.fce


def FetchCourseList(location):
    # response = requests.get(location)
    # only need to run once to get the file which I will continue to read from
    # with open(location, "a") as f:
    #     f.write(response.text)

    with open(location, "r") as f:
        response = f.read()

    return response

def ParseCourseNumberTags(response):
    # when Im just reading from the file, I don't need to extract the content
    # parsed = BeautifulSoup(response.content, "html5lib") # pip install html5lib
    parsed = BeautifulSoup(response, "html5lib") # pip install html5lib
    course_numbers = parsed.find_all("td", string=re.compile(r"\d{5}"))
    return course_numbers

def ParseCourseNumbers(course_number_tags):
    courses = set()
    for course_number in course_number_tags:#[0:5]:
        tag = course_number
        course = list()
        while tag != None:
            course.append(tag.find(string=True))
            tag = tag.next_sibling

        try:
            units = int(float(course[2]))
        except:
            units = math.inf

        if (len(course) <= 9):
            continue

        courses.add(
                CourseInfo(
                    course[1], # name
                    course[0], # number
                    units, # units
                    course[9], # prof
                    course[8], # location
                ))
    # pprint(courses)
    return courses

def FilterCourses(courses):
    if (args.units != None):
        courses = filter(lambda course: course.units in args.units, courses)
    if (args.department != None):
        courses = filter(lambda course: course.department in args.department, courses)
    if (args.level != None):
        courses = filter(lambda course: course.level in args.level, courses)
    return courses

def GetCourseFCEAverage(fce_json):
    fce_sum = 0
    index = 0
    for index, entry in enumerate(fce_json):
        if entry["semester"] == "fall" or entry["semester"] == "spring":
            fce_sum += entry["hrsPerWeek"]
    return fce_sum / (index + 1)

def GetFceInfo(course):
    course_info_url = "https://course.apis.scottylabs.org/courses/courseID"
    fce_info_url = "https://course.apis.scottylabs.org/fces/courseID"

    # info = requests.get(f"{course_info_url}/{course.number}")
    fce = requests.get(f"{fce_info_url}/{course.number}")
    fce_json = json.loads(fce.text)

    course.SetFCE(GetCourseFCEAverage(fce_json))
    return course

def main():
    print(args)

    courses_website_link = "coures_website_response.html"
    # courses_website_link = "https://enr-apps.as.cmu.edu/assets/SOC/sched_layout_fall.htm"
    response = FetchCourseList(courses_website_link)
    course_number_tags = ParseCourseNumberTags(response)
    courses = ParseCourseNumbers(course_number_tags)

    filtered_courses = list(FilterCourses(courses))

    for course in filtered_courses:
        GetFceInfo(course)
    # pprint(filtered_courses)

    sorted_courses = sorted(filtered_courses, key=lambda course: course.GetFCE())
    pprint(sorted_courses)

    return

if __name__ == "__main__":
    main()
