import requests
import argparse, json, re

from pprint import pprint

# TODO:
#   Take into account location filter
#   Filter out summer classes when looking for fce average weight

parser = argparse.ArgumentParser(
                    prog='cmu-course-sorter',
                    description='Find CMU classes that fit your criteria, sorted by FCE. An example usage might look like the following: `python3 cmu-course-sorter.py -u 12 -d 15 18 -d 10 16  -l 6 7 8 9`'
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
parser.add_argument("-t", "--token",
                    type=str, required=False, # TODO: make required?
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

def FetchCourseList(location, local=False):
    local_file = "courses_website_response.html"
    if (local):
        with open(local_file, "r") as f:
            response = f.read()
        return response

    response = requests.get(location)
    with open(local_file, "w") as f:
        f.write(response.text)
    return response.text

def ParseOutCourseNumbers(response):
    course_number_regex = re.compile(r"\d{5}")
    nums = re.findall(course_number_regex, response)
    return nums

# Filter out all the classes that I can up front so I don't DoS the cmu-courses api
def FilterOutDepartmentAndLevel(course_nums):
    def IsInDept(course_num_str):
        return int(course_num_str[:2]) in args.department
    filter_depts = filter(IsInDept, course_nums)
    # print(list(filter_depts))

    def IsCorrectLevel(course_num_str):
        return int(course_num_str[3]) in args.level
    filter_level = filter(IsCorrectLevel, filter_depts)
    # print(list(filter_level))

    return list(filter_level)

def FilterOutUnits(course_jsons, units_dict):
    def IsProperNumUnits(course):
        print(course)
        print(units_dict)
        print(units_dict[course["courseID"]])
        return True
    return list(filter(IsProperNumUnits, course_jsons))


def GenerateApiRequestString(course_nums):
    req = ""
    for course_num in course_nums:
        req += f"&courseID={course_num}" # NOTE: might need to provide it in XX-XXX format at some point
    return req[1:] # cut off the & for the first course num

def RequestFceData(courses_arr):
    # course_info_url = "https://course.apis.scottylabs.org/courses/courseID"
    # fce_info_url = "https://course.apis.scottylabs.org/fces/courseID"
    fce_api_endpoint = "https://course-tools.apis.scottylabs.org/fces?"

    token_val = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBsaWNhdGlvbklkIjoiNjE4NmRlYTQwNWY2YzA0ZjI2OTg3OTgzIiwidXNlcklkIjoiNjI1YjZhYmIwODgxN2MwMDA4MzM5YTMxIiwiZW1haWwiOiJqbGVkb25AYW5kcmV3LmNtdS5lZHUiLCJpYXQiOjE3MDQ5NTg4NTEsImV4cCI6MTcwNjI1NDg1MX0.l5mtAFzS4NpaVYBZ5gYbDnwfAF3ia9oLw7Xr5m7Cj-c7FLhCdFI5ff9enoFhCMRjO7mHdMvE1Z6DVu6GfB9SlNUWDDBKIYg4QGfde3c6GZLUy83NZAYORmIUZbMqmyIdXLJlPMSfkd96btI2ZiY5Ru4GnYrAtKGvbbvWxoyPCPyah2E_LzD6c_PClA7Fvm7HImcpCmpAeWHQx0L80LG1t4oVyRwcT58gjJU2daHG960rIsKJeHdtWEplAwh3s1LrZ1LMCspIp536bJDtZ0Sx8veEoBDe9G7OF3HFRqjoMbgWn8gorRgkmsCwj8Qj88U_hXYT4b0q1c6MCDkvt3Xa6J9TC1vlkXfmihvG25KUEiEE7cFe9b1-kTjVHRLXOn2j05nnurCFKMKZ2W5yXcfPhJKQnMT0JizKsQgUAAMQxeg9IGI8TcumdHSzNRFX00ljL71c_gSqX9JK0B7sxyguDA5JdzqIEk5fRoklPx6ni4eC_b8-V2LjKffI6-n5xVQf6-tstj7Q3ejdb7Ka2xFKku0QgCk0xekOyGJ8MNo25R-d-YYyPt_RlUZ7hx_Xyp_WmZ9IEdla8z_sMXCnf-MViBZqPWFHwFO2s5XOmv16PkERcmB8MI4W-1ZoJdWZ7Aoz6YB5Bv6vkKTu-q8PIvp1sK7SZDygb8Yx-ib4lPjOKPc"
    raw_data = {"token": token_val}
    headers_dict = {"Content-Type": "application/json"}

    fce_json = []
    chunk_size = 20
    while courses_arr:
        chunk, courses_arr = courses_arr[:chunk_size], courses_arr[chunk_size:]

        chunk_courses_query_str = GenerateApiRequestString(chunk)
        link = fce_api_endpoint + chunk_courses_query_str
        print(link)

        chunk_fce_resp = requests.post(link, data=raw_data)
        chunk_fce_json = json.loads(chunk_fce_resp.text)
        # pprint(chunk_fce_json)
        fce_json += chunk_fce_json

    return fce_json

def RequestAllData():
    courses_info_endpoint = "https://course-tools.apis.scottylabs.org/courses/search?"

    levels = ""
    for level in sorted(args.level): levels += str(level)
    query_str = f"levels={levels}&unitsMin={min(args.units)}&unitsMax={max(args.units)}"
    link = courses_info_endpoint + query_str

    token_val = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBsaWNhdGlvbklkIjoiNjE4NmRlYTQwNWY2YzA0ZjI2OTg3OTgzIiwidXNlcklkIjoiNjI1YjZhYmIwODgxN2MwMDA4MzM5YTMxIiwiZW1haWwiOiJqbGVkb25AYW5kcmV3LmNtdS5lZHUiLCJpYXQiOjE3MDQ5NTg4NTEsImV4cCI6MTcwNjI1NDg1MX0.l5mtAFzS4NpaVYBZ5gYbDnwfAF3ia9oLw7Xr5m7Cj-c7FLhCdFI5ff9enoFhCMRjO7mHdMvE1Z6DVu6GfB9SlNUWDDBKIYg4QGfde3c6GZLUy83NZAYORmIUZbMqmyIdXLJlPMSfkd96btI2ZiY5Ru4GnYrAtKGvbbvWxoyPCPyah2E_LzD6c_PClA7Fvm7HImcpCmpAeWHQx0L80LG1t4oVyRwcT58gjJU2daHG960rIsKJeHdtWEplAwh3s1LrZ1LMCspIp536bJDtZ0Sx8veEoBDe9G7OF3HFRqjoMbgWn8gorRgkmsCwj8Qj88U_hXYT4b0q1c6MCDkvt3Xa6J9TC1vlkXfmihvG25KUEiEE7cFe9b1-kTjVHRLXOn2j05nnurCFKMKZ2W5yXcfPhJKQnMT0JizKsQgUAAMQxeg9IGI8TcumdHSzNRFX00ljL71c_gSqX9JK0B7sxyguDA5JdzqIEk5fRoklPx6ni4eC_b8-V2LjKffI6-n5xVQf6-tstj7Q3ejdb7Ka2xFKku0QgCk0xekOyGJ8MNo25R-d-YYyPt_RlUZ7hx_Xyp_WmZ9IEdla8z_sMXCnf-MViBZqPWFHwFO2s5XOmv16PkERcmB8MI4W-1ZoJdWZ7Aoz6YB5Bv6vkKTu-q8PIvp1sK7SZDygb8Yx-ib4lPjOKPc"
    raw_data = {"token": token_val}

    course_info = requests.post(link, data=raw_data)
    course_json = json.loads(course_info.text)
    # print(course_json["docs"])
    return course_json["docs"]

def MakeUnitsMap(course_info):
    units_dict = dict()
    for course in course_info:
        units_dict[course["courseID"]] = course["units"]
    # print(units_dict)
    return units_dict

def main():
    print(args)

    courses_website_link = "https://enr-apps.as.cmu.edu/assets/SOC/sched_layout_spring.htm"
    response = FetchCourseList(courses_website_link, local=False)

    course_nums = ParseOutCourseNumbers(response)
    filter_department_and_level = FilterOutDepartmentAndLevel(course_nums)
    course_fce_data = RequestFceData(filter_department_and_level)
    # course_info = RequestAllData()
    # units_dict = MakeUnitsMap(course_info)
    # filter_units = FilterOutUnits(course_fce_data, units_dict)

    sorted_courses = sorted(course_fce_data, key=lambda course: course['hrsPerWeek'])
    for course in sorted_courses:
        print(f"{course['courseID']} {round(course['hrsPerWeek'], 2):<5} {course['courseName']}")

    return

if __name__ == "__main__":
    main()
