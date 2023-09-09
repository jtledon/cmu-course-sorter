use scraper::Html;

struct Course {
    name: String,

    number: String,
    department: u8,
    level: u8,

    units: u8,

    professor: String,
    fce: Option<f32>
}

fn get_course_list() -> () {
    ()
}

fn get_fce_rating() -> () {
    ()
}

fn filter_courses(list: Vec<Course>) -> () {
    let filtered = list.iter()
                        .filter(|course| course.units == 12)
                        .filter(|course| course.department == 15)
                        .filter(|course| course.level == 8);
    ()
}

fn main() -> () {
    let courses_website_link = "https://enr-apps.as.cmu.edu/assets/SOC/sched_layout_fall.htm";
    let course_html_string = reqwest::blocking::get(courses_website_link).unwrap()
        .text().unwrap();
    let course_html_parsed = Html::parse_document(&course_html_string);
    println!("{:?}", course_html_parsed);

    // println!("{course.fce}\t{course.name}\t{course.number}");
    ()
}
