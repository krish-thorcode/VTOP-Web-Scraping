import os, datetime, re, exam_schedule, zipfile, platform

def inject_download_button():
    js = '''
        document.querySelector('.form-group.text-center:nth-child(3)').innerHTML = '<div class="col-md-12 col-md-offset-0.5">
                                        <a style="padding:3px 16px;font-size:13px;" class="btn btn-primary" id="back" type="button" onclick="javascript:processbackToFilterCourse();">Go Back</a>
                                        <a style="padding:3px 16px;font-size:13px;" class="btn btn-primary" href="/vtop/academics/common/coursePlanReport/">Download Course Plan</a>
                                    <a style="padding:3px 16px;font-size:13px;" class="btn btn-primary" href="/vtop/academics/common/coursePlanReport/" id = "downloader">Download Selected Materials</a></div>'
        '''
    browser.execute_script(js)

def find_dir_name():
    date_re_str = r'(\d{2})-([A-Za-z]{3})-(\d{4})'
    date_re = re.compile(date_re_str)
    mo = date_re.search(lecture_date)
    lecture_date = datetime.datetime(mo(3),mo(2),mo(1))

    if exam_schedule.exam_schedule['CAT-1_end'] >= lecture_date:
        return 'CAT-1'
    elif exam_schedule.exam_schedule['CAT-1_end'] < lecture_date and exam_schedule.exam_schedule['CAT-2_end'] >= lecture_date:
        return 'CAT-2'
    else:
        return 'FAT'

def download_files(dir_name, download_links):
    system = platform.system()
    if system == 'Windows':
        os.mkdir('C:\\VIT_downloads')
        os.chdir('C:\\VIT_downloads')
    if system == 'Linux':
        os.mkdir(os.environ['HOME'] + '/VIT_downloads')
        os.chdir(os.environ['HOME'] + '/VIT_downloads')
    course_material_zip = zipfile.ZipFile((browser.find_element_by_css_selector('#CoursePageLectureDetail > div > div.panel-body > div:nth-child(1) > div > table > tbody > tr:nth-child(2) > td:nth-child(2)')).text, 'w')
    os.mkdir(dir_name)
    os.chdir(dir_name)

    counter = ''
    counter_append = 0

#Download and save files
    for k, v in download_links.items(): # v is a list

        file_name = k + counter
        files_in_dir = os.listdir()
        if file_name in files_in_dir:
            counter_append += 1
            file_name = file_name + '_' + counter_append

def download_course_materials():
    inject_download_button()
    rows_in_ref_material_table = browser.find_elements_by_css_selector('#CoursePageLectureDetail > div > div.panel-body > div:nth-child(3) > div:nth-child(2) > div > table > tbody > tr')

    now = datetime.datetime.now()
    today_date = datetime.datetime(now.year, now.month, now.day)
    date_re_str = r'(\d{2})-([A-Za-z]{3})-(\d{4})'
    date_re = re.compile(date_re_str)

#Finding the most recent exam that got finished
    if exam_schedule.exam_schedule['CAT-1_end'] < today_date:
        exam_done = 'CAT-1' # ie, download after lecture dates that fall in CAT-1 period, or do not download CAT-1 files
    if exam_schedule.exam_schedule['CAT-2_end'] < today_date:
        exam_done = 'CAT_2' # downlaod after lecture dates that fall in CAT-1 and CAT-2 period

    exam_done_end_date = exam_schedule.exam_schedule[exam_done+'_end']
    initial_row_num = len(rows_in_ref_material_table)

# Remove those rows whose lecture_date < end date of exam that has alrady been conducted
    for i in range(1, initial_row_num):
        cells = rows_in_ref_material_table[i].find_elements_by_css_selector('td')
        lecture_date = cells[1].text
        mo = date_re.search(lecture_date)
        lecture_date = datetime.datetime(mo(3),mo(2),mo(1))

        if exam_done_end_date > lecture_date:
            rows_in_ref_material_table.remove(rows_in_ref_material_table[i])

# Accumulate the download links for the reference materials
    download_links = {}
    for i in range(1, len(rows_in_ref_material_table)):
        try:
            cells = rows_in_ref_material_table[i].find_elements_by_css_selector('td')
            anchor_tags = cells[len(cells)-1].find_elements_by_css_selector('p a')
            if exam_done == 'CAT-1':
                dir_name = 'CAT-2'
            elif exam_done == 'CAT-2':
                dir_name = 'FAT'

            key = cells[3].text
            download_links[key] = []

            for anchor_tag in anchor_tags:
                download_link = 'https://vtopbeta.vit.ac.in' + anchor_tag.get_attribute('href')
                download_links[key].append(download_link)
        except:
            pass
    download_files(dir_name, download_links)

def find_download_element():
    try:
        course_plan_download_elem = browser.find_element_by_css_selector('a[href="/vtop/academics/common/coursePlanReport/"]')
        title = browser.find_element_by_css_selector('#page-wrapper > div > section.content-header > h1')
        downloader_thread = threading.Thread(target = download_course_materials)
        downloader_thread.start()
        downloader_thread.join()
    except:
        pass