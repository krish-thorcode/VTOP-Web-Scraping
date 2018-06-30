import os, datetime, re, exam_schedule, platform, shutil, time

# def inject_download_button(browser):
#     js = '''
#         document.querySelector('.form-group.text-center:nth-child(3)').innerHTML = '<div class="col-md-12 col-md-offset-0.5">' +
#                                         '<a style="padding:3px 16px;font-size:13px;" class="btn btn-primary" id="back" type="button" onclick="javascript:processbackToFilterCourse();">Go Back</a>' +
#                                         '<a style="padding:3px 16px;font-size:13px;" class="btn btn-primary" href="/vtop/academics/common/coursePlanReport/">Download Course Plan</a>' +
#                                     '<a style="padding:3px 16px;font-size:13px;" class="btn btn-primary" href="/vtop/academics/common/coursePlanReport/" id = "downloader">Download Materials</a></div>';
#         '''
#     browser.execute_script(js)

def find_dir_name():
    date_re_str = r'(\d{2})-([A-Za-z]{3})-(\d{4})'
    date_re = re.compile(date_re_str)
    mo = date_re.search(lecture_date)
    lecture_date = datetime.datetime(int(mo.group(3)),int(exam_schedule.monthname_monthnum[mo.group(2)]),int(mo.group(1)))

    if exam_schedule.exam_schedule['CAT-1_end'] >= lecture_date:
        return 'CAT-1'
    elif exam_schedule.exam_schedule['CAT-1_end'] < lecture_date and exam_schedule.exam_schedule['CAT-2_end'] >= lecture_date:
        return 'CAT-2'
    else:
        return 'FAT'

def find_download_dir():
    if platform.system() == 'Windows':
        download_dir = 'C:\\VTOP_Course_Materials'
    elif platform.system() == 'Linux':
        download_dir = os.environ['HOME'] + '/VTOP_Course_Materials'

    return download_dir

def download_files(browser, dir_name, download_links):
    root_dir_name = browser.find_element_by_css_selector('#CoursePageLectureDetail > div > div.panel-body > div:nth-child(1) > div > table > tbody > tr:nth-child(2) > td:nth-child(2)').text

    download_dir = find_download_dir()

    os.chdir(download_dir)
    if not os.path.isdir(root_dir_name):
        os.mkdir(root_dir_name)
    if not os.path.isdir('temp'):
        os.mkdir('temp')

    os.chdir(root_dir_name)
    os.mkdir(dir_name)
    os.chdir(os.path.join(download_dir, 'temp'))

#Download and save and rename the file in temp directory
    for k, v in download_links.items(): # v is a list
        counter_append = 0
        if len(v) > 1:
            for link in v:
                counter_append += 1
                intuitive_file_name = k + '_' + str(counter_append)
                # browser.switch_to_window(browser.window_handles[0])
                print(' many files..link: ' + link)
                browser.get(link)
                time.sleep(2)
                # browser.switch_to_window(browser.window_handles[1])
                while True:
                    # print(os.listdir())
                    # print(os.getcwd())
                    # time.sleep(2)
                    download_file_name = (os.listdir())[0]
                    filename, extension = os.path.splitext(download_file_name) # if download is done before this line is executed, then extension will be ppt or pdf, else it will be crdownload
                    # download_filename, download_ext = os.path.splitext(filename) # if download was done, download_ext will be empty str, else it will be pdf or ppt
                    print(extension)
                    if extension != '.crdownload': # and not download_ext: # download is complete
                        shutil.move(filename+extension, intuitive_file_name)
                        shutil.move(intuitive_file_name, os.path.join(download_dir, root_dir_name, dir_name))
                        break

                    else:
                        continue

        else:
            counter = 1
            for link in v:
                intuitive_file_name = k
                if intuitive_file_name == '':
                    intuitive_file_name = 'file' + str(counter)
                    counter += 1
                # browser.switch_to_window(browser.window_handles[0])
                print(' single files..link: ' + link)
                browser.get(link)
                time.sleep(2)
                # browser.switch_to_window(browser.window_handles[1])
                while True:
                    print(os.listdir())
                    # print(os.getcwd())
                    # time.sleep(2)
                    download_file_name = (os.listdir())[0]
                    filename, extension = os.path.splitext(download_file_name) # if download is done before this line is executed, then extension will be ppt or pdf, else it will be crdownload
                    # download_filename, download_ext = os.path.splitext(filename) # if download was done, download_ext will be empty str, else it will be pdf or ppt
                    # print('filename: '+filename+' extension: '+extension+' download_file_name: '+download_file_name+' download_ext: '+download_ext)
                    print(extension)
                    if extension != '.crdownload':# and (download_ext == 'pdf' or 'ppt' in download_ext or 'doc' in download_ext): # download is complete
                        shutil.move(filename+extension, intuitive_file_name)
                        shutil.move(intuitive_file_name, os.path.join(download_dir, root_dir_name, dir_name))
                        print('moved')
                        break

                    else:
                        print('incomplete dwnld')
                        continue

def download_course_materials(browser):
    # inject_download_button(browser)
    rows_in_ref_material_table = browser.find_elements_by_css_selector('#CoursePageLectureDetail > div > div.panel-body > div:nth-child(3) > div:nth-child(2) > div > table > tbody > tr')

    now = datetime.datetime.now()
    today_date = datetime.datetime(now.year, now.month, now.day)
    date_re_str = r'(\d{2})-([A-Za-z]{3})-(\d{4})'
    date_re = re.compile(date_re_str)

#Finding the most recent exam that got finished
    today_date = datetime.datetime(2018,8,20)
    if exam_schedule.exam_schedule['CAT-1_end'] < today_date:
        exam_done = 'CAT-1' # ie, download after lecture dates that fall in CAT-1 period, or do not download CAT-1 files
        exam_done_end_date = exam_schedule.exam_schedule[exam_done +'_end']
    if exam_schedule.exam_schedule['CAT-2_end'] < today_date:
        exam_done = 'CAT-2' # downlaod after lecture dates that fall in CAT-1 and CAT-2 period
        exam_done_end_date = exam_schedule.exam_schedule[exam_done +'_end']

    initial_row_num = len(rows_in_ref_material_table)
    updated_row_num = initial_row_num
    # print('intial rows num: ' + str(initial_row_num))

# Remove those rows whose lecture_date < end date of exam that has alrady been conducted
    for i in range(1, initial_row_num):
        # print("i: " + str(i), "updated_row_num: " + str(updated_row_num))
        if i >= updated_row_num:
            break
        cells = rows_in_ref_material_table[i].find_elements_by_css_selector('td')
        lecture_date = cells[1].text
        mo = date_re.search(lecture_date)
        lecture_date = datetime.datetime(int(mo.group(3)),int(exam_schedule.monthname_monthnum[mo.group(2)]),int(mo.group(1)))

        if exam_done_end_date > lecture_date:
            rows_in_ref_material_table.remove(rows_in_ref_material_table[i])
            updated_row_num -= 1

# Accumulate the download links for the reference materials
    download_links = {}
    for i in range(1, len(rows_in_ref_material_table)):
        # try:
        cells = rows_in_ref_material_table[i].find_elements_by_css_selector('td')
        anchor_tags = cells[len(cells)-1].find_elements_by_css_selector('p a')

        if len(anchor_tags) == 0:
            continue

        if exam_done == 'CAT-1':
            dir_name = 'CAT-2'
        elif exam_done == 'CAT-2':
            dir_name = 'FAT'
        else:
            dir_name = 'CAT-1'

        key = cells[3].text
        download_links[key] = []
        for anchor_tag in anchor_tags:
            href = anchor_tag.get_attribute('href')
            # print(str(i) + href)
            download_link = href
            download_links[key].append(download_link)
        # except:
        #     print('exception ho gaya')
        #     pass
    # pprint.pprint(download_links)
    download_files(browser, dir_name, download_links)

# def find_download_element():
#     try:
#         course_plan_download_elem = browser.find_element_by_css_selector('a[href="/vtop/academics/common/coursePlanReport/"]')
#         print('False')
#         return False
#     except:
#         print('True')
#         return True
