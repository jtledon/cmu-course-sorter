# CMU Course Sorter
This is a command line tool made in Rust which sorts available cmu courses based on FCE or course rating

You can filter the courses based on 
* department
* units
* course level (undergrad/grad)
* semester and year

The default arguments are
* The upcoming semester
* all departments
* all unit counts
* any level class

API design:
`cmu-fce [-u|--units] [-d|--departments] [-l|--level] [-s|--semester] [--sorter]`

Example calls:
`cmu-fce -u 12 -d 15,18,05 -l 6,7,8,9 --sorter fce`
