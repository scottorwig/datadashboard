# TODO:
# State export:
# - generate "time of incident" during/out of school hours based on form incident_time
# - major behaviors are exported to state, minor are not

import csv
import datetime
import os
import string
import sys
import time
import decimal
import random
from decimal import *
from django import forms
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Template, Context
from django.template.loader import get_template
from django.forms.models import modelformset_factory
from operator import itemgetter
import xml.etree.ElementTree as ET
from django.core.servers.basehttp import FileWrapper
from models import *
from forms import *

today = datetime.datetime.today()
default_school_year = '2011-2012'

def get_today_string():
    today_datetime = datetime.datetime.today()
    today_string = today_datetime.strftime('%Y-%m-%d_%H%M')
    return today_string

def get_school_year_list():
    # todo: actually look this up in the data
    list_of_years = ['2010-2011','2011-2012']
    return list_of_years

incident_type_lookup = {
    'Homocide':'01',
    'Kidnapping':'02',
    'Sexual Assault':'03',
    'Robbery':'04',
    'Intimidation/Stalking ':'',
    'Physical Assault':'07',
    'Aggravated/Felonious Assault':'08',
    'Sexual Harassment':'09',
    'Handgun':'20',
    'Rifle/Shotgun':'21',
    'Other Firearms':'22',
    'Other Dangerous Weapons':'23',
    'Drugs/Narcotics':'30',
    'Drugs or narcotics distribution':'30',
    'Drugs or narcotics possession':'30',
    'Drugs or narcotics - under the influence':'30',
    'Use or Possession of Alcohol':'31',
    'Burglary':'40',
    'Larceny/Theft':'41',
    'Larceny or theft':'41',
    'False Alarm':'42',
    'Loitering':'43',
    'Bomb or Similar Threat':'44',
    'Truancy':'45',
    'Trespassing':'46',
    'Breaking and Entering':'47',
    'Extortion':'48',
    'Graffiti':'49',
    'Gambling':'50',
    'Refusal to Identify Self':'51',
    'Disrption of Education Process/Student Demonstration':'52',
    'Disruption of the educational process':'52',
    'Disruption (agitation)':'52',
    'Fraud or Bribery':'53',
    'Damage to Property':'54',
    'Arson':'55',
    'Other':'56',
    'Disability intimidation':'71',
    'Intimidation - Racial or ethnic':'72',
    'Intimidation - Religion':'70',
    'Intimidation - Sexual orientation':'73',
}

types_needing_location = ('01','03','07','08','20','21','22','23','44','45')
types_needing_time = ('01','03','07','08','20','21','22','23','44','45')

submittingEntityTypeCode = 'D'
submittingEntityCode = '81070'
operatingISDESANumber = '81'
buildingLookup = {'4':'05235','004':'05235', '100':'05235','200':'07190','300':'02186','400':'05166','500':'02187','600':'00308','700':'09148'}

whiteList = string.letters

def CharactersFromWhitelistOnly(impureString):
    stringToReturn = ''
    for suspectChar in impureString:
        if suspectChar in whiteList:
            stringToReturn += suspectChar
            return stringToReturn

def get_student_list_with_count(buildingNumber, schoolyear=default_school_year):
    # Django 1.1 includes aggregate query functions that will greatly improve this code
    # Being afraid to upgrade in place right now, I'm going to do this the ugly way
    # You may want to avert your eyes
    student_actions = DisciplineAction.objects.filter(school_id=buildingNumber).filter(school_year=schoolyear)
    student_list = []
    for action in student_actions:
        student_list.append(action.student)
    student_set = set(student_list)
    student_list_with_count = []
    for student in student_set:
        action_count = DisciplineAction.objects.filter(student=student).filter(school_year=schoolyear).count()
        student_list_with_count.append([student,action_count])
    student_list_with_count.sort(key=itemgetter(1), reverse=True)
    return student_list_with_count


def get_location_list_with_count(buildingNumber, schoolyear=default_school_year):
    # Django 1.1 includes aggregate query functions that will greatly improve this code
    # Being afraid to upgrade in place right now, I'm going to do this the ugly way
    # You may want to avert your eyes
    location_incidents = Incident.objects.filter(school_id=buildingNumber).filter(school_year=schoolyear)
    location_list = []
    for incident in location_incidents:
        location_list.append(incident.location)
    location_set = set(location_list)
    location_list_with_count = []
    for location in location_set:
        incident_count = Incident.objects.filter(school_id=buildingNumber).filter(location=location).filter(school_year=schoolyear).count()
        location_list_with_count.append([location,incident_count])
    location_list_with_count.sort(key=itemgetter(1), reverse=True)
    # OK, it's safe to look now
    return location_list_with_count


def list_of_consequences():
    ethnicityLookup = {'':'000010','W':'000010', 'WM':'000010', 'B':'001000', 'BM':'001000', 'I':'100000', 'IM':'100000', 'A':'010000','AM':'010000', 'H':'000001','HM':'000001', 'P':'000100', 'PM':'000100', 'F':'000100', 'FM':'000100',}
    start_time = time.time()
    actions = DisciplineAction.objects.filter(school_year = '2011-2012').order_by('student')
    list_of_consequences = []
    for action in actions:
        try:
            associated_incident = Incident.objects.get(mi_incident_id = action.mi_incident_id)
        except:
            debug_string = debug_string + 'Error finding Incident with mi_incident_id=' + action.mi_incident_id
            
        debug_string = ''
        student_full_string = action.student
        student_last_name, student_first_name, student_number, debug_string = split_student_from_dropdown(student_full_string, debug_string)
        
        try:
            current_student = Student.objects.get(StudentNumber=student_number)
        except:
            current_student = '' # make sure we don't end up with a leftover student from the last loop
            debug_string = debug_string + str(sys.exc_info()[0]) + 'for' + student_full_string + ' using the number -' + student_number + '-.'
        
        try:
            school_id = current_student.school_id
        except:
            school_id = ''
            debug_string = debug_string + 'Error finding school_id for ' + student_full_string + '. '
        
        try:
            special_ed_eligible = current_student.SpecialEdEligible
        except:
            special_ed_eligible = ''
            debug_string = debug_string + 'Error finding special_ed_eligible for ' + student_full_string + '. '
        
        try:
            uic = current_student.UIC
        except:
            uic = ''
            debug_string = debug_string + 'Error finding UIC for ' + student_full_string + '. '
        
        try:
            date_of_birth = current_student.date_of_birth
        except:
            date_of_birth = ''
            debug_string = debug_string + 'Error finding UIC for ' + student_full_string + '. '
            
        try:
            gender = current_student.gender
        except:
            gender = ''
            debug_string = debug_string + 'Error finding gender for ' + student_full_string + '. '
            
        try:
            ethnicity = ethnicityLookup[current_student.ethnicity]
        except:
            ethnicity = ''
            debug_string = debug_string + 'Error finding ethnicity for ' + student_full_string + '. '
        
        try:
            grade = current_student.grade.zfill(2)
        except:
            grade = ''
            debug_string = debug_string + 'Error finding gender for ' + student_full_string + '. '
            
        try:
            exit_status = current_student.exit_status
        except:
            exit_status = ''
            debug_string = debug_string + 'Error finding exit status for ' + student_full_string + '. '
            
        try:
            entry_date = current_student.entry_date
        except:
            entry_date = ''
            debug_string = debug_string + 'Error finding entry date for ' + student_full_string + '. '       
        
        try:
            address = current_student.address
        except:
            address = ''
            debug_string = debug_string + 'Error finding address for ' + student_full_string + '. '         
 
        try:
            city = current_student.city
        except:
            city = ''
            debug_string = debug_string + 'Error finding city for ' + student_full_string + '. '
            
        try:
            state = current_student.state
        except:
            state = ''
            debug_string = debug_string + 'Error finding state for ' + student_full_string + '. '  
            
        try:
            zip = current_student.zip
        except:
            zip = ''
            debug_string = debug_string + 'Error finding zip for ' + student_full_string + '. '   
        
        try:
            iss_start = action.iss_start_date.strftime('%Y-%m-%d')
        except:
            iss_start = ''
            debug_string = debug_string + 'Error getting iss_start for value' + str(action.iss_start_date)
        
        try:
            oss_start = action.oss_start_date.strftime('%Y-%m-%d')
        except:
            oss_start = ''
            debug_string = debug_string + 'Error getting oss_start for value' + str(action.oss_start_date)
        
        debug_string = debug_string + '-action.oss_start_date:' + str(action.oss_start_date) + ' with data type:' + str(type(action.oss_start_date))
        debug_string = debug_string + '-action.iss_start_date:' + str(action.iss_start_date) + ' with data type:' + str(type(action.iss_start_date))
        
        list_of_consequences.append(
            {
                'school_id': associated_incident.school_id,
                'mi_incident_id': associated_incident.mi_incident_id, 
                'referrer': associated_incident.referrer,
                'event_time': associated_incident.event_time,
                'event_date': associated_incident.event_date,
                'event_location': associated_incident.location,
                'mi_time_of_incident': associated_incident.mi_time_of_incident,
                'action_id': action.id,
                'problem_behavior_minor': action.problem_behaviors_minor,
                'problem_behavior_major': action.problem_behaviors_major,
                'student_full_string': student_full_string,
                'student_number': student_number,
                'student_first_name': student_first_name,
                'student_last_name': student_last_name,
                'school_id': school_id,
                'speical_ed_eligible': special_ed_eligible,
                'uic': uic, 
                'date_of_birth': date_of_birth,
                'gender': gender,
                'grade': grade,
                'ethnicity': ethnicity,
                'date_of_birth': date_of_birth,
                'exit_status': exit_status,
                'entry_date': entry_date,
                'address': address,
                'city': city,
                'state': state,
                'zip': zip,
                'iss_start': iss_start,
                'iss_end': action.iss_end_date,
                'iss_days': action.iss_number_days,
                'oss_start': oss_start,
                'oss_end': action.oss_end_date,
                'oss_days': action.oss_number_days,
                'debug_string': debug_string
            })
    time_passed = time.time() - start_time
    return list_of_consequences, time_passed

def split_student_from_dropdown(student_full_string,debug_string=''):
    split_student = student_full_string.split(',')
    student_last_name = split_student[0]
    try:
        split_second_part = split_student[1].split('-')
    except:
        split_second_part = ''
        student_first_name = ''
        debug_string = debug_string + '*error splitting ' + student_full_string
    try:
        student_first_name = string.strip(split_second_part[0])
    except:
        student_first_name = ''
        debug_string = debug_string + '*error splitting ' + student_full_string
    try:
        student_number_dirty = split_second_part[1]
        student_number = student_number_dirty.strip()
    except:
        student_number = ''
        debug_string = debug_string + '*error getting number from ' + student_full_string
    return student_last_name, student_first_name, student_number, debug_string

def calculate_action_length_for_reporting(consequence, debug_string=''):
    # figure out DisciplinaryConsequence values
    report_this_action = False
    if consequence['oss_days'] > .1:
        report_this_action = True
        disciplinary_action_code = '2' # 2 means OSS
        debug_string = debug_string + "-consequence['oss_start']:" + str(consequence['oss_start']) + '-datatype:' + str(type(consequence['oss_start']))
        try:
            start_of_action_date = str(consequence['oss_start'])
        except:
            start_of_action_date = ''
            report_this_action = False
        length_of_action_count = str(consequence['oss_days'])
    elif consequence['iss_days'] > .1:
        report_this_action = True
        disciplinary_action_code = '1' # 1 means ISS
        debug_string = debug_string + "-consequence['iss_start']:" + str(consequence['iss_start']) + '-datatype:' + str(type(consequence['iss_start']))
        try:
            start_of_action_date = str(consequence['iss_start'])  #.strftime('%Y-%m-%d')
        except:
            start_of_action_date = ''
            report_this_action = False
        length_of_action_count = str(consequence['iss_days'])
        debug_string = debug_string + "-consequence['iss_days']:" + str(consequence['iss_days']) + '-datatype:' + str(type(consequence['iss_days']))
        debug_string = debug_string + '-length_of_action_count set to:' + length_of_action_count
    else:
        report_this_action = False
        disciplinary_action_code = 'x'
        start_of_action_date = ''
        length_of_action_count = ''
    # Here comes an embarrassing series of 'if' statements
    # There MUST be a way to do this mathematically but I'm out of time
    if length_of_action_count == 'None':
        report_this_action = False
    if length_of_action_count == '0.08' or length_of_action_count == '0.17' or length_of_action_count == '0.25' or length_of_action_count == '0.33' or length_of_action_count == '0.43':
        length_of_action_count = '0.5'
    if length_of_action_count == '0.67' or length_of_action_count == '0.75' or length_of_action_count == '0.83' or length_of_action_count == '0.84':
        length_of_action_count = '1.0'
    if length_of_action_count == '1.17' or length_of_action_count == '1.33' or length_of_action_count=='1.25':
        length_of_action_count = '1.5'
    if length_of_action_count == '1.67' or length_of_action_count == '1.83' or length_of_action_count == '1.85':
        length_of_action_count = '2.0'
    if length_of_action_count == '2.33' or length_of_action_count == '2.83':
        length_of_action_count = '2.5'
    if length_of_action_count == '3.33':
        length_of_action_count = '3.5' 
    if length_of_action_count == '5.23':
        length_of_action_count = '5.5'
    # translate BAIT majors and minors to state incident type
    if consequence['problem_behavior_minor']:
        try:
            state_incident_code = incident_type_lookup['consequence.problem_behavior_minor']
        except:
            state_incident_code = '56'
    elif consequence['problem_behavior_major']:
        try:
            state_incident_code = incident_type_lookup['consequence.problem_behavior_major']
        except:
            state_incident_code = '56'
    else:
        state_incident_code = '56'
    # get location when needed
    reporting_location = ''
    reporting_time = ''
    if state_incident_code in types_needing_location:
        if consequence['event_location'] == 'School Function - Off property':
            reporting_location = '3'
        elif consequence['event_location'] == 'Bus':
            reporting_location = '2'
        else:
            reporting_location = '1'
    return report_this_action, disciplinary_action_code, start_of_action_date, length_of_action_count, state_incident_code, reporting_location, debug_string

# Filters for validation checks
def has_no_student(items):
    if items[9] == '':
        return True
    else:
        return False

def has_no_consequence(items):
    if items[6] == '':
        return True
    else:
        return False
    
def has_unparsable_student(items):
    if items[11] == 'error':
        return True
    else:
        return False
    
def create_google_barchart_setvalue_string(tuple_list):
    google_setvalue = ''
    i = 0
    for value_pair in tuple_list:
        if value_pair[0]:
            value_name = value_pair[0]
        else:
            value_name = 'None'
        google_setvalue = google_setvalue + 'data.setValue(' + str(i) + ",0,'" + value_name + "');\n"
        google_setvalue = google_setvalue + 'data.setValue(' + str(i) + ',1,' + str(value_pair[1]) + ');\n'
        i = i + 1
    return google_setvalue


def create_incident_id():
    today = datetime.date.today()
    currentTime = datetime.datetime.now()
    random_digits = random.randint(10, 99)
    mi_incident_id_string = today.strftime("%j") + currentTime.strftime("%H%M") + currentTime.strftime("%s")[:1] + str(random_digits)
    return mi_incident_id_string

def cookie_monster(forwarded_request):
    account = Accounts()
    active_school_year = default_school_year
    require_login = False
    try:
        if forwarded_request.COOKIES['number']:
            building_number = forwarded_request.COOKIES['number']
            account = Accounts.objects.get(number=building_number)
        else:
            require_login = True
        if forwarded_request.COOKIES['school_year']:
            active_school_year = forwarded_request.COOKIES['school_year']
        else:
            require_login = True
    except:
        require_login = True
    return account, active_school_year, require_login

def data_for_header(school_year_view):
    header_data = []
    header_data.append(Incident.objects.filter(school_id=100).filter(school_year=school_year_view).count())
    header_data.append(Incident.objects.filter(school_id=200).filter(school_year=school_year_view).count())
    header_data.append(Incident.objects.filter(school_id=300).filter(school_year=school_year_view).count())
    header_data.append(Incident.objects.filter(school_id=400).filter(school_year=school_year_view).count())
    header_data.append(Incident.objects.filter(school_id=500).filter(school_year=school_year_view).count())
    header_data.append(Incident.objects.filter(school_id=600).filter(school_year=school_year_view).count())
    header_data.append(Incident.objects.filter(school_id=700).filter(school_year=school_year_view).count())
    header_data.append(DisciplineAction.objects.filter(school_id=100).filter(school_year=school_year_view).count())
    header_data.append(DisciplineAction.objects.filter(school_id=200).filter(school_year=school_year_view).count())
    header_data.append(DisciplineAction.objects.filter(school_id=300).filter(school_year=school_year_view).count())
    header_data.append(DisciplineAction.objects.filter(school_id=400).filter(school_year=school_year_view).count())
    header_data.append(DisciplineAction.objects.filter(school_id=500).filter(school_year=school_year_view).count())
    header_data.append(DisciplineAction.objects.filter(school_id=600).filter(school_year=school_year_view).count())
    header_data.append(DisciplineAction.objects.filter(school_id=700).filter(school_year=school_year_view).count())
    school_year_list = get_school_year_list()
    return header_data, school_year_list

def change_school_year(request):
    account, school_year_view, require_login = cookie_monster(request)
    school_year_list = get_school_year_list()
    debug_string = ''
    try:
        changed_year = request.POST['year']
    except:
        changed_year = default_school_year
    page_title = 'Year changed to ' + changed_year
    variables = Context({
        'debug_string': debug_string,
        'account': account,
        'head_title': page_title,
        'page_title': page_title,
        'school_year_list': school_year_list,
        'school_year': changed_year,
        })
    template = get_template('disciplineform_school_year_changed.html')
    output = template.render(variables)
    response = HttpResponse(output)
    response.set_cookie('school_year', changed_year)
    return response

def discipline_login(request):
    debug_string = ''
    page_title = 'Please sign in to BAIT'
    variables = Context({
        'debug_string': debug_string,
        'page_title': page_title,
        'head_title': page_title,
        })
    template = get_template('discipline_login.html')
    output = template.render(variables)
    response = HttpResponse(output)
    response.delete_cookie('number')
    response.delete_cookie('school_year')
    return response

def discipline_login_submit(request):
    debug_string = ''
    try:
        password = request.POST['password']
        account = Accounts.objects.get(password=password)
        building_number = account.number
    except:
        return HttpResponseRedirect("/discipline_login/")
    page_title = 'BAIT - Signed in to ' + account.name
    variables = Context({
        'debug_string': debug_string,
        'page_title': page_title,
        })
    template = get_template('discipline_login_successful.html')
    output = template.render(variables)
    response = HttpResponse(output)
    response.set_cookie('number', building_number)
    response.set_cookie('school_year', default_school_year)
    return response

def discipline_home(request):
    account, school_year_view, require_login = cookie_monster(request)
    entry_counts, school_year_list = data_for_header(school_year_view)
    if require_login:
        return HttpResponseRedirect("/discipline/login/")
    try:
        building_number = account.number
    except:
        building_number = ''
    entry_counts, school_year_list = data_for_header(school_year_view)
    staffInBuilding = Staff.objects.filter(school_id=building_number)
    staffDropdownString = ''
    for staff in staffInBuilding:
        staffDropdownString += '"' + staff.AutocompleteName + '",'
    studentsInBuilding = Student.objects.filter(school_id=building_number)
    studentDropdownString = ''
    for student in studentsInBuilding:
        studentDropdownString += '"' + student.AutocompleteName + '",'
    incident_list = []
    incidents = Incident.objects.filter(school_id=building_number).filter(school_year=school_year_view).order_by('-last_changed')
    for incident in incidents:
        try:
            associated_actions = DisciplineAction.objects.filter(mi_incident_id=incident.mi_incident_id)
        except:
            associated_actions = DisciplineAction()
        for action in associated_actions:
            list_item = [incident.mi_incident_id, action.id, incident.event_date, incident.referrer, action.student, incident.description_of_incident ]
            incident_list.append(list_item)
    return render_to_response('disciplineform_home.html',
        {
        'account': account,
        'incident_list': incident_list,
        'head_title': u'PBIS Behavior Analysis and Intervention Tool (BAIT)',
        'page_title': u'PBIS Behavior Analysis and Intervention Tool (BAIT)',
        'entry_counts': entry_counts,
        'staffdropdownstring': staffDropdownString,
        'studentdropdownstring': studentDropdownString,
        'school_year': school_year_view,
        'school_year_list': school_year_list,
        })

def enter_incident(request):
    if 'number' in request.COOKIES:
        buildingNumber = request.COOKIES['number']
        account = get_object_or_404(Accounts,number=buildingNumber)
        staffInBuilding = Staff.objects.filter(school_id=buildingNumber)
    else:
        return HttpResponseRedirect("/discipline/")
    if 'school_year' in request.COOKIES:
        school_year_view = request.COOKIES['school_year']
    else:
        school_year_view = default_school_year
    if request.method == 'POST':
        form = IncidentEntryForm(request.POST)
        if form.is_valid():
            # using commit=False so that I can set the school_id programatically
            # and generate a mi_incident_id
            new_incident = form.save(commit=False)
            new_incident.school_id = buildingNumber
            new_incident.school_year = default_school_year
            new_incident.event_time = form.cleaned_data['event_hour'] + ':' + form.cleaned_data['event_minute']
            # loop until we know we have a unique incident_id
            # for some reason the 'while' thing isn't working so I'm going to do this ugly thing
            new_incident_id = create_incident_id()
            test_query = Incident.objects.filter(mi_incident_id=new_incident_id)
            if test_query.count() > 0:
                new_incident_id = create_incident_id()
            new_incident.mi_incident_id = new_incident_id
            new_incident.save()
            title_string = "Added incident " + new_incident_id + " to BAIT"
            variables = Context({
                'account': account,
                'date': form.cleaned_data['event_date'],
                'description': form.cleaned_data['description_of_incident'],
                'mi_incident_id': new_incident.mi_incident_id,
                'head_title': title_string,
                'page_title': title_string,
            })
            template = get_template('discipline_confirm_edit_incident.html')
            output = template.render(variables)
            response = HttpResponse(output)
            return response
        else:
            # validation error - form was not valid
            variables = Context({
                'errors': form.errors,
                'postdata': request.POST,
                'account': account,
                'head_title': u'Validation Error',
                'page_title': u'Validation Error!'
            })
            template = get_template('discipline_validation_errors.html')
            output = template.render(variables)
            response = HttpResponse(output)
            return response
    else:
        staffDropdownString = ''
        for staff in staffInBuilding:
            staffDropdownString += '"' + staff.AutocompleteName + '",'
        form = IncidentEntryForm(initial={'event_hour':'00','mi_time_of_incident':'During school hours','reported_to_state':'',})
        variables = Context({
            'account': account,
            'staffdropdownstring': staffDropdownString,
            'form': form,
            'head_title': u'Enter a discipline incident',
            'page_title': u'Enter a discipline incident',
            'school_year': default_school_year,
        })
        template = get_template('discipline_incident_edit_form.html')
        output = template.render(variables)
        response = HttpResponse(output)
        return response


def add_disciplinary_action(request, mi_incident_id):
    if 'number' in request.COOKIES:
        buildingNumber = request.COOKIES['number']
        account = get_object_or_404(Accounts,number=buildingNumber)
        studentsInBuilding = Student.objects.filter(school_id=buildingNumber)
    else:
        return HttpResponseRedirect("/discipline/")
    if request.method == 'POST':
        form = DisciplineActionEntryForm(request.POST)
        if form.is_valid():
            new_action = form.save(commit=False)
            new_action.school_id = buildingNumber
            new_action.mi_incident_id = mi_incident_id
            new_action.school_year = '2011-2012'
            new_action.save()
            current_incident = Incident.objects.get(mi_incident_id=mi_incident_id)
            related_actions = DisciplineAction.objects.filter(mi_incident_id=mi_incident_id)
            title_string = 'Disciplinary action added for student ' + new_action.student
            variables = Context({
                'account': account,
                'incident': current_incident,
                'edited_action': new_action,
                'related_actions': related_actions,
                'head_title': title_string,
                'page_title': title_string,
            })
            template = get_template('discipline_confirm_edit_action.html')
            output = template.render(variables)
            response = HttpResponse(output)
            return response
        else:
            # validation error - form was not valid
            variables = Context({
                'errors': form.errors,
                'postdata': request.POST,
                'account': account,
                'head_title': u'Validation Error',
                'page_title': u'Validation Error!'
            })
            template = get_template('discipline_validation_errors.html')
            output = template.render(variables)
            response = HttpResponse(output)
            return response
    else:
        studentDropdownString = ''
        for student in studentsInBuilding:
            studentDropdownString += '"' + student.AutocompleteName + '",'
        form = DisciplineActionEntryForm()
        variables = Context({
            'account': account,
            'mi_incident_id': mi_incident_id,
            'studentdropdownstring': studentDropdownString,
            'form': form,
            'head_title': u'Add or modify disciplinary action',
            'page_title': u'Add or modify disciplinary action'
        })
        template = get_template('discipline_action_edit_form.html')
        output = template.render(variables)
        response = HttpResponse(output)
        return response

def edit_disciplinary_action(request, actionid):
    debug_string = ''
    if 'number' in request.COOKIES:
        try:
            buildingNumber = request.COOKIES['number']
            account = Accounts.objects.get(number=buildingNumber)
            studentsInBuilding = Student.objects.filter(school_id=buildingNumber)
        except:
            #404 for now - later redirect
            raise Http404()
    if request.method == 'POST':
        object_to_edit = get_object_or_404(DisciplineAction,id=actionid)
        debug_string = str(object_to_edit)
        form = DisciplineActionEntryForm(data = request.POST or None, instance=object_to_edit)
        if form.is_valid():
            edited_action = form.save(commit=False)
            edited_action.school_id = buildingNumber
            edited_action.last_changed = datetime.datetime.now()
            edited_action.save()
            action_to_confirm = DisciplineAction.objects.get(id=actionid)
            related_incident = Incident.objects.get(mi_incident_id=action_to_confirm.mi_incident_id)
            variables = Context({
                'account': account,
                'edited_action': action_to_confirm,
                'incident': related_incident,
                'debug_string': debug_string,
            })
            template = get_template('discipline_confirm_edit_action.html')
            output = template.render(variables)
            response = HttpResponse(output)
            return response
    else:
        action_to_edit = DisciplineAction.objects.get(id=actionid)
        form = DisciplineActionEntryForm(instance=action_to_edit)
        try:
            related_incident = Incident.objects.get(mi_incident_id=action_to_edit.mi_incident_id)
        except:
            related_incident = Incident()
        studentDropdownString = ''
        for student in studentsInBuilding:
            studentDropdownString += '"' + student.AutocompleteName + '",'
        title_string = 'Edit action for ' + action_to_edit.student
        return render_to_response('discipline_action_edit_form.html',
                                  {
                                      'head_title': title_string,
                                      'page_title': title_string,
                                      'debug_string': debug_string,
                                      'action': action_to_edit,
                                      'incident': related_incident,
                                      'form': form,
                                      'editing': True,
                                      'studentdropdownstring': studentDropdownString,
                                  })

def edit_incident(request, mi_incident_id):
    if 'number' in request.COOKIES:
        try:
            buildingNumber = request.COOKIES['number']
            account = Accounts.objects.get(number=buildingNumber)
            staffInBuilding = Staff.objects.filter(school_id=buildingNumber)
        except:
            #404 for now - later redirect
            raise Http404()
    if request.method == 'POST':
        object_to_edit = get_object_or_404(Incident,mi_incident_id=mi_incident_id)
        form = IncidentEntryForm(data = request.POST or None, instance=object_to_edit)
        if form.is_valid():
            changed_incident = form.save(commit=False)
            changed_incident.school_id = buildingNumber
            changed_incident.mi_incident_id = mi_incident_id
            changed_incident.event_time = form.cleaned_data['event_hour'] + ':' + form.cleaned_data['event_minute']
            changed_incident.save()
            associated_actions = DisciplineAction.objects.filter(mi_incident_id=mi_incident_id)
        variables = Context({
            'account': account,
            'date': form.cleaned_data['event_date'],
            'description': form.cleaned_data['description_of_incident'],
            'mi_incident_id': mi_incident_id,
            'actions': associated_actions
        })
        template = get_template('discipline_confirm_edit_incident.html')
        output = template.render(variables)
        response = HttpResponse(output)
        return response
    else:
        if 'number' in request.COOKIES:
            try:
                buildingNumber = request.COOKIES['number']
                account = Accounts.objects.get(number=buildingNumber)
            except:
                #404 for now - later redirect
                raise Http404()
        editedIncident = Incident.objects.get(mi_incident_id=mi_incident_id)
        staffDropdownString = ''
        for staff in staffInBuilding:
            staffDropdownString += '"' + staff.AutocompleteName + '",'
        form = IncidentEntryForm(instance=editedIncident)
        variables = Context({
            'account': account,
            'staff': staffInBuilding,
            'staffdripdownstring': staffDropdownString,
            'form': form,
            'head_title': u'Edit this discipline incident',
            'page_title': u'Edit this discipline incident',
            'mi_incident_id': mi_incident_id,
            'building_number': buildingNumber
        })
        template = get_template('discipline_incident_edit_form.html')
        output = template.render(variables)
        response = HttpResponse(output)
        return response

def edit_action(request, mi_incident_id):
    if 'number' in request.COOKIES:
        try:
            buildingNumber = request.COOKIES['number']
            account = Accounts.objects.get(number=buildingNumber)
        except:
            #404 for now - later redirect
            raise Http404()
    incident = Incident.objects.get(mi_incident_id=mi_incident_id)
    actions_to_edit = DisciplineAction.objects.filter(mi_incident_id=mi_incident_id)
    title_string = 'Edit disciplinary actions for incident ' + mi_incident_id
    return render_to_response('disciplineform_edit_actions_for_incident.html',
                              {
                                  'account':account,
                                  'head_title': title_string,
                                  'page_title': title_string,
                                  'incident': incident,
                                  'actions': actions_to_edit,
                              })

def view_students_for_incident(request, incidentNumber):
    if 'number' in request.COOKIES:
        try:
            buildingNumber = request.COOKIES['number']
            account = Accounts.objects.get(number=buildingNumber)
            staffInBuilding = Staff.objects.filter(school_id=buildingNumber)
        except:
            #404 for now - later redirect
            raise Http404()
    if request.method == 'POST':
        object_to_edit = get_object_or_404(Incident,id=incidentNumber)
        form = IncidentEntryForm(data = request.POST or None, instance=object_to_edit)
        if form.is_valid():
            changed_incident = form.save(commit=False)
            changed_incident.school_id = buildingNumber
            changed_incident.event_time = form.cleaned_data['event_hour'] + ':' + form.cleaned_data['event_minute']
            changed_incident.save()
            related_students = DisciplineAction.objects.filter(incident=incidentNumber)
        variables = Context({
            'account': account,
            'date': form.cleaned_data['event_date'],
            'description': form.cleaned_data['description_of_incident'],
            'incident_id': incidentNumber,
            'students': related_students
        })
        template = get_template('discipline_confirm_add_incident.html')
        output = template.render(variables)
        response = HttpResponse(output)
        return response
    else:
        if 'number' in request.COOKIES:
            try:
                buildingNumber = request.COOKIES['number']
                account = Accounts.objects.get(number=buildingNumber)
            except:
                #404 for now - later redirect
                raise Http404()
        editedIncident = Incident.objects.get(id=incidentNumber)
        staffDropdownString = ''
        for staff in staffInBuilding:
            staffDropdownString += '"' + staff.AutocompleteName + '",'
        form = IncidentEntryForm(instance=editedIncident)
        variables = Context({
            'account': account,
            'staff': staffInBuilding,
            'staffdripdownstring': staffDropdownString,
            'form': form,
            'head_title': u'Edit this discipline incident',
            'page_title': u'Edit this discipline incident',
            'existing_primary_key': editedIncident.id,
            'building_number': buildingNumber
        })
        template = get_template('discipline_incident_entry_form.html')
        output = template.render(variables)
        response = HttpResponse(output)
        return response

def incident_detail(request,incident_id):
    if 'number' in request.COOKIES:
        buildingNumber = request.COOKIES['number']
        account = get_object_or_404(Accounts,number=buildingNumber)
    else:
        return HttpResponseRedirect("/discipline/")
    incident = Incident.objects.get(id=incident_id)
    title_string = 'Details for this incident'
    return render_to_response('disciplineform_incident_detail.html',{'account':account,'head_title': title_string, 'page_title': title_string, 'incident':incident})


def discipline_summary(request):
    if 'number' in request.COOKIES:
        buildingNumber = request.COOKIES['number']
        account = get_object_or_404(Accounts,number=buildingNumber)
    else:
        return HttpResponseRedirect("/discipline/")
    variables = Context({
        'account': account,
        'head_title': u'BAIT Summary of PBIS Data',
        'page_title': u'BAIT Summary of PBIS Data',
        'building_number': buildingNumber,
        'month_count_list': monthCountList
    })

def output_csv_for_powerschool(request):
    if 'number' in request.COOKIES:
        buildingNumber = request.COOKIES['number']
        account = get_object_or_404(Accounts,number=buildingNumber)
    else:
        return HttpResponseRedirect("/discipline/")
    response = HttpResponse(mimetype='text/csv')
    contentDisposition  = 'attachment; filename=PBIS_data_for_PS_log_building_'
    contentDisposition += buildingNumber
    contentDisposition += '_'
    contentDisposition += get_datestamp()
    contentDisposition += '.csv'
    response['Content-Disposition'] = contentDisposition
    tab_file  = ''
    tab_file += ''

    incident_queryset = DisciplineEvent.objects.filter(school_id=buildingNumber)
    for incident in incident_queryset:
        download_writer.writerow([incident.school_id,])

    return response




# DETAIL VIEWS ----------------------------------------------------------------------
def view_incidents_student_post(request):
    if request.method == 'POST':
        student_string = request.POST['student']
        return view_incidents_student(request, student_string)
    else:
        return HttpResponseRedirect("/discipline")

def view_incidents_student(request, student_string):
    account, school_year_view, require_login = cookie_monster(request)
    school_year_list = get_school_year_list()
    debug_string = ''
    actions_for_student = DisciplineAction.objects.filter(student=student_string).filter(school_year=school_year_view)
    oss_total = Decimal(0)
    iss_total = Decimal(0)
    detention_total = Decimal(0)
    behavior_list = []
    for action in actions_for_student:
        if action.iss_number_days:
            iss_total = iss_total + action.iss_number_days
        if action.oss_number_days:
            oss_total = oss_total + action.oss_number_days
        if action.detention_number_days:
            detention_total = detention_total + action.detention_number_days
        try:
            associated_incident = Incident.objects.get(mi_incident_id=action.mi_incident_id)
        except:
            associated_incident = Incident()
        behavior = [action.mi_incident_id, associated_incident.event_date, associated_incident.event_time, action.problem_behaviors_minor, action.problem_behaviors_major, action.iss_number_days, action.oss_number_days, action.detention_number_days, associated_incident.description_of_incident]
        behavior_list.append(behavior)
    title_string = 'Incidents for student: ' + student_string
    try:
        student = Student.objects.get(AutocompleteName=student_string)
        is_special_ed_eligible = student.SpecialEdEligible
    except:
        is_special_ed_eligible = False
    return render_to_response('disciplineform_view_incidents_student.html',
                              {
                                  'debug_string': debug_string,
                                  'account':account,
                                  'head_title': title_string,
                                  'page_title': title_string,
                                  'student_string': student_string,
                                  'behavior_list': behavior_list,
                                  'is_special_ed_eligible': is_special_ed_eligible,
                                  'oss_total': oss_total,
                                  'iss_total': iss_total,
                                  'detention_total': detention_total,
                                  'school_year_list':school_year_list,
                                  'school_year': school_year_view,
                              })

def view_incidents_student_fail(request, student_string):
    debug_string = ''
    if 'number' in request.COOKIES:
        buildingNumber = request.COOKIES['number']
        account = get_object_or_404(Accounts,number=buildingNumber)
    else:
        return HttpResponseRedirect("/discipline/")
    title_string = 'Possible alternatives to "' + student_string + '"'
    possible_students = []
    students_contained = Student.objects.filter(AutocompleteName__icontains=student_string)
    for student in students_contained:
        student_data = [student.AutocompleteName, student.grade, student.date_of_birth, student.gender, student.ethnicity]
        possible_students.append(student_data)
    return render_to_response('disciplineform_view_incidents_student_fail.html',
                              {
                                  'debug_string': debug_string,
                                  'account':account,
                                  'head_title': title_string,
                                  'page_title': title_string,
                                  'failed_student_name': student_string,
                                  'possible_count': len(possible_students),
                                  'possible_students': possible_students,
                              })

def view_incidents_date_post(request):
    if request.method == 'POST':
        try:
            date_from_POST = request.POST['incident_date']
        except:
            today = datetime.date.today()
            date_from_POST = today.strftime("%Y-%m-%d")
        return view_incidents_date(request, date_from_POST)
    else:
        return HttpResponseRedirect("/discipline")

def view_incidents_date(request, event_date):
    if 'number' in request.COOKIES and request.method == 'POST':
        buildingNumber = request.COOKIES['number']
        account = get_object_or_404(Accounts,number=buildingNumber)
    else:
        return HttpResponseRedirect("/discipline/")
    lines_to_report = []
    incidents_on_date = Incident.objects.filter(event_date=event_date).filter(school_id=buildingNumber).order_by('referrer','event_time')
    for behavior_incident in incidents_on_date:
        try:
            associated_actions = DisciplineAction.objects.filter(mi_incident_id=behavior_incident.mi_incident_id)
        except:
            associated_actions = DisciplineAction()
        for action in associated_actions:
            report_line = [behavior_incident.mi_incident_id, behavior_incident.referrer, behavior_incident.location, action.student, action.problem_behaviors_minor, action.problem_behaviors_major, behavior_incident.description_of_incident]
            lines_to_report.append(report_line)
    title_string = 'Incidents on date: ' + str(event_date)
    return render_to_response('disciplineform_view_incidents_date.html',{'account':account,'head_title': title_string, 'page_title': title_string, 'event_date': event_date, 'lines_to_report': lines_to_report})



def view_incidents_referrer_post(request):
    if request.method == 'POST':
        referrer_string = request.POST['referrer']
        return view_incidents_referrer(request, referrer_string)
    else:
        return HttpResponseRedirect("/discipline")

def view_incidents_referrer(request, referrer_string):
    if 'number' in request.COOKIES:
        buildingNumber = request.COOKIES['number']
        account = get_object_or_404(Accounts,number=buildingNumber)
    else:
        return HttpResponseRedirect("/discipline/")
    incidents_for_referrer = Incident.objects.filter(referrer=referrer_string).order_by('-event_date', '-event_time')
    list_to_report = []
    for incident in incidents_for_referrer:
        actions = DisciplineAction.objects.filter(mi_incident_id=incident.mi_incident_id)
        for action in actions:
            list_item = [incident.mi_incident_id, incident.event_date, action.student, incident.location, incident.description_of_incident]
            list_to_report.append(list_item)
    title_string = 'Incidents referred by: ' + referrer_string
    return render_to_response('disciplineform_view_incidents_referrer.html',{'account':account,'head_title': title_string, 'page_title': title_string, 'referrer_string': referrer_string, 'list_to_report':list_to_report})

def view_incidents_location(request, location_string=u'Classroom'):
    if 'number' in request.COOKIES:
        buildingNumber = request.COOKIES['number']
        account = get_object_or_404(Accounts,number=buildingNumber)
    else:
        return HttpResponseRedirect("/discipline/")
    if request.method == 'POST':
        location_string = request.POST['location']
    incidents_for_location = Incident.objects.filter(location=location_string).filter(school_id=buildingNumber).order_by('-event_date', '-event_time')
    list_to_report = []
    for incident in incidents_for_location:
        actions = DisciplineAction.objects.filter(mi_incident_id=incident.mi_incident_id)
        for action in actions:
            list_item = [incident.mi_incident_id, incident.event_date, action.student, incident.referrer, incident.description_of_incident]
            list_to_report.append(list_item)
    title_string = 'Incidents occurating at: ' + location_string
    return render_to_response('disciplineform_view_incidents_location.html',{'account':account,'head_title': title_string, 'page_title': title_string, 'location_string':location_string, 'list_to_report':list_to_report})

def view_incidents_problem_behaviors_minor(request, location_string=u'Classroom'):
    if 'number' in request.COOKIES:
        buildingNumber = request.COOKIES['number']
        account = get_object_or_404(Accounts,number=buildingNumber)
    else:
        return HttpResponseRedirect("/discipline/")
    if request.method == 'POST':
        location_string = request.POST['location']
    incidents_for_location = Incident.objects.filter(location=location_string).filter(school_id=buildingNumber).order_by('-event_date', '-event_time')
    title_string = 'Incidents occurating at: ' + location_string
    return render_to_response('disciplineform_view_incidents_location.html',{'account':account,'head_title': title_string, 'page_title': title_string, 'referrer_string': referrer_string, 'incidents' :incidents_for_location})

def view_incidents_problem_behaviors_major(request, location_string=u'Classroom'):
    if 'number' in request.COOKIES:
        buildingNumber = request.COOKIES['number']
        account = get_object_or_404(Accounts,number=buildingNumber)
    else:
        return HttpResponseRedirect("/discipline/")
    if request.method == 'POST':
        location_string = request.POST['location']
    incidents_for_location = Incident.objects.filter(location=location_string).filter(school_id=buildingNumber).order_by('-event_date', '-event_time')
    title_string = 'Incidents occurating at: ' + location_string
    return render_to_response('disciplineform_view_incidents_location.html',{'account':account,'head_title': title_string, 'page_title': title_string, 'referrer_string': referrer_string, 'incidents' :incidents_for_location})

# DATA VIEWS ---------------------------------------------------------------------------------

def incidents_by_student(request):
    account, school_year_view, require_login = cookie_monster(request)
    school_year_list = get_school_year_list()
    student_list_with_count = get_student_list_with_count(account.number, school_year_view)
    row_count = len(student_list_with_count)
    google_setvalue = create_google_barchart_setvalue_string(student_list_with_count)
    title_string = "Discipline incidents by student for " + school_year_view
    return render_to_response('disciplineform_incidents_by_student_max.html',{'account':account, 'school_year_list':school_year_list, 'head_title': title_string, 'page_title': title_string, 'student_list_with_count': student_list_with_count, 'school_year': school_year_view, 'row_count': row_count, 'google_setvalue': google_setvalue})

def incidents_by_referrer(request):
    account, school_year_view, require_login = cookie_monster(request)
    school_year_list = get_school_year_list()
    # Django 1.1 includes aggregate query functions that will greatly improve this code
    # Being afraid to upgrade in place right now, I'm going to do this the ugly way
    # You may want to avert your eyes
    referrer_incidents = Incident.objects.filter(school_id=account.number).filter(school_year=school_year_view)
    referrer_list = []
    for incident in referrer_incidents:
        referrer_list.append(incident.referrer)
    referrer_set = set(referrer_list)
    referrer_list_with_count = []
    for referrer in referrer_set:
        incident_count = Incident.objects.filter(referrer=referrer).filter(school_year=school_year_view).count()
        referrer_list_with_count.append([referrer,incident_count])
    referrer_list_with_count.sort(key=itemgetter(1), reverse=True)
    # OK, it's safe to look now
    row_count = len(referrer_list_with_count)
    google_setvalue = create_google_barchart_setvalue_string(referrer_list_with_count)
    title_string = "Discipline Incident Referrers for " + school_year_view
    return render_to_response('disciplineform_incidents_by_referrer_max.html',{'account':account,'head_title': title_string, 'page_title': title_string, 'school_year_list':school_year_list, 'school_year': school_year_view, 'referrer_list_with_count': referrer_list_with_count, 'row_count': row_count, 'google_setvalue': google_setvalue})

def incidents_by_location(request):
    account, school_year_view, require_login = cookie_monster(request)
    school_year_list = get_school_year_list()
    location_list_with_count = get_location_list_with_count(account.number, school_year_view)
    row_count = len(location_list_with_count)
    google_setvalue = create_google_barchart_setvalue_string(location_list_with_count)
    title_string = "Locations of discipline incidents for " + school_year_view
    return render_to_response('disciplineform_incidents_by_location.html',{'account':account,'head_title': title_string, 'page_title': title_string, 'school_year_list':school_year_list, 'school_year': school_year_view, 'location_list_with_count': location_list_with_count, 'row_count': row_count, 'google_setvalue': google_setvalue})

def incidents_by_grade(request):
    account, school_year_view, require_login = cookie_monster(request)
    school_year_list = get_school_year_list()
    # Django 1.1 includes aggregate query functions that will greatly improve this code
    # Being afraid to upgrade in place right now, I'm going to do this the ugly way
    # You may want to avert your eyes
    grade_incidences = DisciplineAction.objects.filter(school_id=account.number).filter(school_year=school_year_view)
    grade_list = []
    for incidence in grade_incidences:
        grade_list.append(incidence.student_grade)
    grade_set = set(grade_list)
    grade_list_with_count = []
    for grade in grade_set:
        incidence_count = DisciplineAction.objects.filter(student_grade=grade).filter(school_year=school_year_view).count()
        grade_list_with_count.append([grade,incidence_count])
    grade_list_with_count.sort(key=itemgetter(0))
    # OK, it's safe to look now
    row_count = len(grade_list_with_count)
    google_setvalue = create_google_barchart_setvalue_string(grade_list_with_count)
    title_string = "Discipline incidents by grade for " + school_year_view
    return render_to_response('disciplineform_incidents_by_grade.html',{'account':account,'head_title': title_string, 'page_title': title_string, 'school_year_list':school_year_list, 'school_year': school_year_view, 'grade_list_with_count': grade_list_with_count, 'row_count': row_count, 'google_setvalue': google_setvalue})

def incidents_by_month(request):
    account, school_year_view, require_login = cookie_monster(request)
    school_year_list = get_school_year_list()
    month_list_with_count = []
    month_list_with_count.append(['August',Incident.objects.filter(school_id=account.number).filter(school_year=school_year_view).filter(event_date__month=8).count()])
    month_list_with_count.append(['September',Incident.objects.filter(school_id=account.number).filter(school_year=school_year_view).filter(event_date__month=9).count()])
    month_list_with_count.append(['October',Incident.objects.filter(school_id=account.number).filter(school_year=school_year_view).filter(event_date__month=10).count()])
    month_list_with_count.append(['November',Incident.objects.filter(school_id=account.number).filter(school_year=school_year_view).filter(event_date__month=11).count()])
    month_list_with_count.append(['December',Incident.objects.filter(school_id=account.number).filter(school_year=school_year_view).filter(event_date__month=12).count()])
    month_list_with_count.append(['January',Incident.objects.filter(school_id=account.number).filter(school_year=school_year_view).filter(event_date__month=1).count()])
    month_list_with_count.append(['February',Incident.objects.filter(school_id=account.number).filter(school_year=school_year_view).filter(event_date__month=2).count()])
    month_list_with_count.append(['March',Incident.objects.filter(school_id=account.number).filter(school_year=school_year_view).filter(event_date__month=3).count()])
    month_list_with_count.append(['April',Incident.objects.filter(school_id=account.number).filter(school_year=school_year_view).filter(event_date__month=4).count()])
    month_list_with_count.append(['May',Incident.objects.filter(school_id=account.number).filter(school_year=school_year_view).filter(event_date__month=5).count()])
    month_list_with_count.append(['June',Incident.objects.filter(school_id=account.number).filter(school_year=school_year_view).filter(event_date__month=6).count()])
    month_list_with_count.append(['July',Incident.objects.filter(school_id=account.number).filter(school_year=school_year_view).filter(event_date__month=7).count()])
    row_count = len(month_list_with_count)
    google_setvalue = create_google_barchart_setvalue_string(month_list_with_count)
    title_string = "Discipline incidents in each month for " + school_year_view
    return render_to_response('disciplineform_incidents_by_month.html',{'account':account,'head_title': title_string, 'page_title': title_string, 'school_year_list':school_year_list, 'school_year': school_year_view, 'month_list_with_count': month_list_with_count, 'row_count': row_count, 'google_setvalue': google_setvalue})


def incidents_by_day_of_week(request):
    account, school_year_view, require_login = cookie_monster(request)
    school_year_list = get_school_year_list()
    all_incidents = Incident.objects.filter(school_id=account.number).filter(school_year=school_year_view)
    incident_count = Incident.objects.filter(school_id=account.number).filter(school_year=school_year_view).count()
    monday_count = 0;
    tuesday_count = 0;
    wednesday_count = 0;
    thursday_count = 0;
    friday_count = 0;
    saturday_count = 0;
    sunday_count = 0;
    for incident in all_incidents:
        incident_dow = incident.event_date.weekday()
        if incident_dow == 0:
            monday_count = monday_count + 1
        elif incident_dow == 1:
            tuesday_count = tuesday_count + 1
        elif incident_dow == 2:
            wednesday_count = wednesday_count + 1
        elif incident_dow == 3:
            thursday_count = thursday_count + 1
        elif incident_dow == 4:
            friday_count = friday_count + 1
        elif incident_dow == 5:
            saturday_count = saturday_count + 1
        elif incident_dow == 6:
            sunday_count = sunday_count + 1
    dow_list_with_count = []
    dow_list_with_count.append(['Monday',monday_count])
    dow_list_with_count.append(['Tuesday',tuesday_count])
    dow_list_with_count.append(['Wednesday',wednesday_count])
    dow_list_with_count.append(['Thursday',thursday_count])
    dow_list_with_count.append(['Friday',friday_count])
    dow_list_with_count.append(['Saturday',saturday_count])
    dow_list_with_count.append(['Sunday',sunday_count])
    row_count = len(dow_list_with_count)
    google_setvalue = create_google_barchart_setvalue_string(dow_list_with_count)
    title_string = "Discipline incident totals for each day of the week for " + school_year_view
    return render_to_response('disciplineform_incidents_by_day_of_week.html',{'account':account,'head_title': title_string, 'page_title': title_string, 'school_year_list':school_year_list, 'school_year': school_year_view, 'dow_list_with_count': dow_list_with_count, 'incident_count':incident_count, 'row_count': row_count, 'google_setvalue': google_setvalue})


def incidents_by_time(request):
    account, school_year_view, require_login = cookie_monster(request)
    school_year_list = get_school_year_list()
    # Django 1.1 includes aggregate query functions that will greatly improve this code
    # Being afraid to upgrade in place right now, I'm going to do this the ugly way
    # You may want to avert your eyes
    time_incidents = Incident.objects.filter(school_id=account.number).filter(school_year=school_year_view)
    time_list = []
    for incident in time_incidents:
        time_list.append(incident.event_time)
    time_set = set(time_list)
    time_list_with_count = []
    for time in time_set:
        incident_count = Incident.objects.filter(school_id=account.number).filter(event_time=time).filter(school_year=school_year_view).count()
        time_list_with_count.append([time,incident_count])
    time_list_with_count.sort(key=itemgetter(0))
    # OK, it's safe to look now
    row_count = len(time_list_with_count)
    google_setvalue = create_google_barchart_setvalue_string(time_list_with_count)
    title_string = "Discipline Incident times for " + school_year_view
    return render_to_response('disciplineform_incidents_by_time.html',{'account':account,'head_title': title_string, 'page_title': title_string, 'school_year_list':school_year_list, 'school_year': school_year_view, 'time_list_with_count': time_list_with_count, 'row_count': row_count, 'google_setvalue': google_setvalue})

def rules_broken(request):
    account, school_year_view, require_login = cookie_monster(request)
    school_year_list = get_school_year_list()
    # Django 1.1 includes aggregate query functions that will greatly improve this code
    # Being afraid to upgrade in place right now, I'm going to do this the ugly way
    # You may want to avert your eyes
    rule_incidences = DisciplineAction.objects.filter(school_id=account.number).filter(school_year=school_year_view)
    respectful_count = 0
    responsible_count = 0
    safe_count = 0
    rule_list_with_count = []
    for incidence in rule_incidences:
        if incidence.rule_broken_respectful == True:
            respectful_count = respectful_count + 1
        if incidence.rule_broken_responsible == True:
            responsible_count = responsible_count + 1
        if incidence.rule_broken_safe == True:
            safe_count = safe_count + 1
    rule_list_with_count.append(['Respectful', respectful_count])
    rule_list_with_count.append(['Responsible', responsible_count])
    rule_list_with_count.append(['Safe', safe_count])
    row_count = len(rule_list_with_count)
    google_setvalue = create_google_barchart_setvalue_string(rule_list_with_count)
    title_string = "Count of core behavioral values violated for " + school_year_view
    return render_to_response('disciplineform_rules_broken.html',{'account':account,'head_title': title_string, 'page_title': title_string, 'school_year_list':school_year_list, 'school_year': school_year_view, 'rule_list_with_count': rule_list_with_count, 'row_count': row_count, 'google_setvalue': google_setvalue})


def major_problem_behaviors(request):
    account, school_year_view, require_login = cookie_monster(request)
    school_year_list = get_school_year_list()
    # Django 1.1 includes aggregate query functions that will greatly improve this code
    # Being afraid to upgrade in place right now, I'm going to do this the ugly way
    # You may want to avert your eyes
    problem_behaviors_major_incidences = DisciplineAction.objects.filter(school_id=account.number).filter(school_year=school_year_view)
    problem_behaviors_major_list = []
    for incidence in problem_behaviors_major_incidences:
        if incidence.problem_behaviors_major:
            problem_behaviors_major_list.append(incidence.problem_behaviors_major)
    problem_behaviors_major_set = set(problem_behaviors_major_list)
    problem_behaviors_major_list_with_count = []
    for problem_behaviors_major in problem_behaviors_major_set:
        incidence_count = DisciplineAction.objects.filter(school_id=account.number).filter(problem_behaviors_major=problem_behaviors_major).filter(school_year=school_year_view).count()
        problem_behaviors_major_list_with_count.append([problem_behaviors_major,incidence_count])
    problem_behaviors_major_list_with_count.sort(key=itemgetter(1), reverse=True)
    # OK, it's safe to look now
    row_count = len(problem_behaviors_major_list_with_count)
    google_setvalue = create_google_barchart_setvalue_string(problem_behaviors_major_list_with_count)
    title_string = "Discipline incidents for each major problem behavior for " + school_year_view
    return render_to_response('disciplineform_major_problem_behaviors.html',{'account':account,'head_title': title_string, 'page_title': title_string, 'problem_behaviors_major_list_with_count': problem_behaviors_major_list_with_count, 'school_year_list':school_year_list, 'school_year': school_year_view, 'row_count': row_count, 'google_setvalue': google_setvalue})

def minor_problem_behaviors(request):
    account, school_year_view, require_login = cookie_monster(request)
    school_year_list = get_school_year_list()
    # Django 1.1 includes aggregate query functions that will greatly improve this code
    # Being afraid to upgrade in place right now, I'm going to do this the ugly way
    # You may want to avert your eyes
    problem_behaviors_minor_incidences = DisciplineAction.objects.filter(school_id=account.number)
    problem_behaviors_minor_list = []
    for incidence in problem_behaviors_minor_incidences:
        if incidence.problem_behaviors_minor:
            problem_behaviors_minor_list.append(incidence.problem_behaviors_minor)
    problem_behaviors_minor_set = set(problem_behaviors_minor_list)
    problem_behaviors_minor_list_with_count = []
    for problem_behaviors_minor in problem_behaviors_minor_set:
        incidence_count = DisciplineAction.objects.filter(school_id=account.number).filter(problem_behaviors_minor=problem_behaviors_minor).filter(school_year=school_year_view).count()
        problem_behaviors_minor_list_with_count.append([problem_behaviors_minor,incidence_count])
    problem_behaviors_minor_list_with_count.sort(key=itemgetter(1), reverse=True)
    # OK, it's safe to look now
    row_count = len(problem_behaviors_minor_list_with_count)
    google_setvalue = create_google_barchart_setvalue_string(problem_behaviors_minor_list_with_count)
    title_string = "Discipline incidents for each minor problem behavior for " + school_year_view
    return render_to_response('disciplineform_minor_problem_behaviors.html',{'account':account,'head_title': title_string, 'page_title': title_string, 'school_year_list':school_year_list, 'school_year': school_year_view, 'problem_behaviors_minor_list_with_count': problem_behaviors_minor_list_with_count, 'row_count':row_count,'google_setvalue':google_setvalue })

def in_school_suspensions(request):
    account, school_year_view, require_login = cookie_monster(request)
    school_year_list = get_school_year_list()
    title_string = "In-School Suspensions for " + school_year_view
    debug_string = ''
    suspensions = DisciplineAction.objects.filter(iss_start_date__isnull=False).filter(school_id=account.number).filter(school_year=school_year_view).order_by('iss_start_date')
    suspension_count = len(suspensions)
    in_school_suspension_list = []
    for suspension in suspensions:
        try:
            associated_incident = Incident.objects.get(mi_incident_id = suspension.mi_incident_id)
        except:
            debug_string = debug_string + 'Error finding Incident with mi_incident_id=' + suspension.mi_incident_id
        student_full_string = suspension.student
        student_last_name, student_first_name, student_number, debug_string = split_student_from_dropdown(student_full_string, debug_string)
        item = [suspension.mi_incident_id, suspension.student, associated_incident.event_date, student_last_name, student_first_name, suspension.iss_number_days, suspension.problem_behaviors_major, suspension.problem_behaviors_minor]
        in_school_suspension_list.append(item)
    return render_to_response('disciplineform_in_school_suspensions.html',{'account':account,'head_title': title_string, 'page_title': title_string, 'school_year_list':school_year_list, 'school_year': school_year_view, 'in_school_suspension_list': in_school_suspension_list, 'suspension_count':suspension_count, 'debug_string':debug_string})

def out_school_suspensions(request):
    account, school_year_view, require_login = cookie_monster(request)
    school_year_list = get_school_year_list()
    title_string = "Out-of-School Suspensions for " + school_year_view
    debug_string = ''
    suspensions = DisciplineAction.objects.filter(oss_start_date__isnull=False).filter(school_id=account.number).filter(school_year=school_year_view).order_by('oss_start_date')
    suspension_count = len(suspensions)
    out_school_suspension_list = []
    for suspension in suspensions:
        try:
            associated_incident = Incident.objects.get(mi_incident_id = suspension.mi_incident_id)
        except:
            debug_string = debug_string + 'Error finding Incident with mi_incident_id=' + suspension.mi_incident_id
        student_full_string = suspension.student
        student_last_name, student_first_name, student_number, debug_string = split_student_from_dropdown(student_full_string, debug_string)
        item = [suspension.mi_incident_id, suspension.student, suspension.oss_start_date, student_last_name, student_first_name, suspension.oss_number_days, suspension.problem_behaviors_major, suspension.problem_behaviors_minor]
        out_school_suspension_list.append(item)
    return render_to_response('disciplineform_out_school_suspensions.html',{'account':account,'head_title': title_string, 'page_title': title_string, 'school_year_list':school_year_list, 'school_year': school_year_view, 'out_school_suspension_list': out_school_suspension_list, 'suspension_count':suspension_count, 'debug_string':debug_string})

def out_school_suspensions_specialed(request):
    account, school_year_view, require_login = cookie_monster(request)
    school_year_list = get_school_year_list()
    title_string = "Out-of-School Suspensions of Special Ed Eligible Students in " + school_year_view
    debug_string = ''
    suspensions = DisciplineAction.objects.filter(oss_start_date__isnull=False).filter(school_id=account.number).filter(school_year=school_year_view).order_by('oss_start_date')
    suspension_count = len(suspensions)
    out_school_suspension_list = []
    for suspension in suspensions:
        try:
            associated_student = Student.objects.get(AutocompleteName=suspension.student)
        except:
            debug_string = debug_string + 'Error finding Student with AutocompleteName=' + suspension.student
            associated_student = Student()
        if associated_student.SpecialEdEligible == True:
            try:
                associated_incident = Incident.objects.get(mi_incident_id = suspension.mi_incident_id)
            except:
                debug_string = debug_string + 'Error finding Incident with mi_incident_id=' + suspension.mi_incident_id
            item = [suspension.mi_incident_id, suspension.student, suspension.oss_start_date, associated_student.NameLast, associated_student.NameFirst, suspension.oss_number_days, suspension.problem_behaviors_major, suspension.problem_behaviors_minor]
            out_school_suspension_list.append(item)
    return render_to_response('disciplineform_out_school_suspensions.html',{'account':account,'head_title': title_string, 'page_title': title_string, 'school_year_list':school_year_list, 'out_school_suspension_list': out_school_suspension_list, 'school_year': school_year_view, 'suspension_count':suspension_count, 'debug_string':debug_string})

def in_school_suspensions_specialed(request):
    account, school_year_view, require_login = cookie_monster(request)
    school_year_list = get_school_year_list()
    title_string = "In-School Suspensions of Special Ed Eligible Students in " + school_year_view
    debug_string = ''
    suspensions = DisciplineAction.objects.filter(iss_start_date__isnull=False).filter(school_id=account.number).filter(school_year=school_year_view).order_by('iss_start_date')
    suspension_count = len(suspensions)
    in_school_suspension_list = []
    for suspension in suspensions:
        try:
            associated_student = Student.objects.get(AutocompleteName=suspension.student)
        except:
            debug_string = debug_string + 'Error finding Student with AutocompleteName=' + suspension.student
            associated_student = Student()
        if associated_student.SpecialEdEligible == True:
            try:
                associated_incident = Incident.objects.get(mi_incident_id = suspension.mi_incident_id)
            except:
                debug_string = debug_string + 'Error finding Incident with mi_incident_id=' + suspension.mi_incident_id
            item = [suspension.mi_incident_id, suspension.student, suspension.iss_start_date, associated_student.NameLast, associated_student.NameFirst, suspension.iss_number_days, suspension.problem_behaviors_major, suspension.problem_behaviors_minor]
            in_school_suspension_list.append(item)
    return render_to_response('disciplineform_in_school_suspensions.html',{'account':account,'head_title': title_string, 'page_title': title_string, 'school_year_list':school_year_list, 'school_year': school_year_view, 'in_school_suspension_list': in_school_suspension_list, 'suspension_count':suspension_count, 'debug_string':debug_string})

def suspensions_specialed(request):
    account, school_year_view, require_login = cookie_monster(request)
    school_year_list = get_school_year_list()
    title_string = "Days of Suspension for Special Ed Eligible Students in " + school_year_view
    debug_string = ''
    students = Student.objects.filter(SpecialEdEligible=True).filter(school_id=account.number).order_by('NameLast')
    students_with_suspensions = []
    for student in students:
        consequences = DisciplineAction.objects.filter(student=student.AutocompleteName).filter(school_year=school_year_view)
        suspension_total = Decimal(0)
        background_color = 'white'
        for consequence in consequences:
            if consequence.iss_number_days:
                suspension_total = suspension_total + consequence.iss_number_days
            if consequence.oss_number_days:
                suspension_total = suspension_total + consequence.oss_number_days
        if suspension_total > 0:
            if suspension_total > Decimal(5):
                background_color = 'yellow'
            if suspension_total > Decimal(9):
                background_color = 'pink'
            suspended_student = [student.AutocompleteName, student.StudentNumber, student.NameFirst, student.NameLast, suspension_total, student.gender, student.ethnicity]
            students_with_suspensions.append(suspended_student)
    return render_to_response('disciplineform_suspensions_specialed.html',{'account':account,'head_title': title_string, 'page_title': title_string, 'school_year_list':school_year_list, 'school_year': school_year_view, 'students_with_suspensions': students_with_suspensions, 'background_color': background_color, 'debug_string':debug_string})

def referral_view(request, mi_incident_id):
    debug_string = ''
    if 'number' in request.COOKIES:
        buildingNumber = request.COOKIES['number']
        account = get_object_or_404(Accounts,number=buildingNumber)
    else:
        return HttpResponseRedirect("/discipline/")
    try:
        incident = Incident.objects.get(mi_incident_id=mi_incident_id)
    except:
        incident = Incident()

    associated_actions = DisciplineAction.objects.filter(mi_incident_id=mi_incident_id)

    title_string = 'Incident ' + incident.mi_incident_id
    return render_to_response('disciplineform_referral_view.html',
                              {
                                  'debug_string': debug_string,
                                  'account': account,
                                  'head_title': title_string,
                                  'page_title': title_string,
                                  'incident': incident,
                                  'associated_actions': associated_actions,
                              })
    

def generate_srm_xml(request):
    current_student = ''
    today_string = get_today_string()
    buildingLookup = {'4':'05235','004':'05235', '100':'05235','200':'07190','300':'02186','400':'05166','500':'02187','600':'00308','700':'09148', '800':'00405'}


    # get the data
    by_date = '2011-06-01'
    today = datetime.date.today()
    reported_incidents = []
    attribute_dictionary = {'SchemaVersionMinor': '1', 'SubmittingSystemVersion': '1.0', 'CollectionName': 'StudentRecordMaintenance', 'SubmittingSystemVendor': 'ScottOrwig', 'CollectionId': '124', 'SchemaVersionMajor': '2011-2012', 'SubmittingSystemName': 'BAIT', 'xsi:noNamespaceSchemaLocation': 'http://cepi.state.mi.us/msdsxml/StudentRecordMaintenance2011-20121.xsd', 'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance'}

    root = ET.Element('StudentRecordMaintenanceGroup', attribute_dictionary)
    
    consequences, consequences_time = list_of_consequences()
    
    counter = 0
    previous_student = 'first'
    for consequence in consequences:
        debug_string = ''
        # we only report when the action involved ISS, OSS, or similar that was greater than .5 days
        if consequence['iss_days'] > .5 or consequence['oss_days']  > .5 or 1==1:
            report_this_action, disciplinary_action_code, start_of_action_date, length_of_action, state_incident_code, reporting_location, debug_string = calculate_action_length_for_reporting(consequence, debug_string)
            # get time when needed
            if state_incident_code in types_needing_time:
                if consequence['mi_time_of_incident'] != 'During school hours':
                    reporting_time = '2'
                else:
                    reporting_time = '1'
            else:
                reporting_time = ''  
                
            
            debug_string_to_write = debug_string #+ consequence['debug_string'] + '-iss_days:' + str(consequence['iss_days']) + '-type:' + str(type(consequence['iss_days'])) + '-oss_days:' + str(consequence['oss_days'])+ '-type:' + str(type(consequence['oss_days'])) 
            if consequence['uic'] == '':
                report_this_action = False
                # means the student was not found
            if start_of_action_date == '':
                report_this_action = False
            
            if report_this_action:
                if previous_student != consequence['uic']:
                    record = ET.SubElement(root,'StudentRecordMaintenance')
                
                    submittingEntity = ET.SubElement(record, 'SubmittingEntity')
                    entityTypeCode = ET.SubElement(submittingEntity,'SubmittingEntityTypeCode')
                    entityTypeCode.text = 'D'
                    entityCode = ET.SubElement(submittingEntity, 'SubmittingEntityCode')
                    entityCode.text = '81070'
                
                    personal_core = ET.SubElement(record, 'PersonalCore')
                    ##student_from_bait = ET.SubElement(personal_core,'StudentFromBAIT')
                    ##student_from_bait.text = student_full_string
                    uic_element = ET.SubElement(personal_core,'UIC')
                    uic_element.text = consequence['uic']
                    last_name = ET.SubElement(personal_core,'LastName')
                    try:
                        last_name.text = consequence['student_last_name']
                    except:
                        last_name.text = ''
                    first_name = ET.SubElement(personal_core,'FirstName')
                    try:
                        first_name.text = consequence['student_first_name']
                    except:
                        first_name.text = ''
                    date_of_birth = ET.SubElement(personal_core, 'DateOfBirth')
                    try:
                        date_of_birth.text = consequence['date_of_birth']
                    except:
                        date_of_birth.text = str(sys.exc_info()[0])
                    gender = ET.SubElement(personal_core, 'Gender')
                    try:
                        gender.text = consequence['gender']
                    except:
                        gender.text = ''
                
                    student_record_maintenance = ET.SubElement(record, 'StudentRecordMaintenance')
                    as_of_date = ET.SubElement(student_record_maintenance, 'AsOfDate')
                    as_of_date.text = '2012-01-10'
                
                    try:
                        school_id_state = buildingLookup[consequence['school_id']]
                    except:
                        school_id_state = 'error looking up:' + consequence['school_id']
                    
                    school_demographics = ET.SubElement(record, 'SchoolDemographics')
                    operating_isd_esa_number = ET.SubElement(school_demographics, 'OperatingISDESANumber')
                    operating_isd_esa_number.text = '81'
                    operating_district_number = ET.SubElement(school_demographics, 'OperatingDistrictNumber')
                    operating_district_number.text = '81070'
                    school_facility_number = ET.SubElement(school_demographics,'SchoolFacilityNumber')
                    school_facility_number.text = school_id_state
                    grade_or_setting = ET.SubElement(school_demographics, 'GradeOrSetting')
                    try:
                        grade_or_setting.text = consequence['grade']
                    except:
                        grade_or_setting.text = ''
                    
                    personal_demographics = ET.SubElement(record, 'PersonalDemographics')
                    resident_lea_number = ET.SubElement(personal_demographics, 'ResidentLEANumber')
                    resident_lea_number.text = '81070'
                    street_address = ET.SubElement(personal_demographics, 'StreetAddress')
                    try:
                        street_address.text = consequence['address']
                    except:
                        street_address.text = ''
                    personal_demographics_city = ET.SubElement(personal_demographics, 'PersonalDemographicsCity')
                    try:
                        personal_demographics_city.text = consequence['city']
                    except:
                        personal_demographics_city.text = ''
                    state = ET.SubElement(personal_demographics, 'State')
                    try:
                        state.text = consequence['state']
                    except:
                        state.text = ''
                    zip_code = ET.SubElement(personal_demographics, 'ZipCode')
                    try:
                        zip_code.text = consequence['zip']
                    except:
                        zip_code.text = ''
                    
                    
                    ethnicity = ET.SubElement(personal_demographics, 'Ethnicity')
                    try:
                        ethnicity.text = consequence['ethnicity']
                    except:
                        ethnicity.text = ''
                    
                    enrollment = ET.SubElement(record, 'Enrollment')
                    enrollment_date = ET.SubElement(enrollment, 'EnrollmentDate')
                    try:
                        enrollment_date.text = consequence['entry_date']
                    except:
                        enrollment_date.text = ''
                    exit_status = ET.SubElement(enrollment, 'ExitStatus')
                    exit_status.text = '19'
                    
                    membership = ET.SubElement(record, 'Membership')
                    student_residency = ET.SubElement(membership, 'StudentResidency')
                    student_residency.text = '14'
                    
                
                if consequence['mi_incident_id'] not in reported_incidents:
                    reported_incidents.append(consequence['mi_incident_id'])
                    discipline_element = ET.SubElement(record, 'Discipline')
                    incident_id = ET.SubElement(discipline_element, 'IncidentID')
                    incident_id.text = consequence['mi_incident_id']
                    date_of_incident = ET.SubElement(discipline_element, 'DateOfIncident')
                    date_of_incident.text = str(consequence['event_date'])
                    incident_type = ET.SubElement(discipline_element, 'IncidentType')
                    incident_type.text = state_incident_code
                    initial_consequence_type = ET.SubElement(discipline_element, 'InitialConsequenceType')
                    initial_consequence_type.text = disciplinary_action_code
                    initial_days = ET.SubElement(discipline_element, 'InitialDays')
                    initial_days.text = length_of_action
                    initial_start_date = ET.SubElement(discipline_element, 'InitialStartDate')
                    initial_start_date.text = start_of_action_date
                    
                    #if reporting_location:
                        #location_of_incident = ET.SubElement(discipline_element, 'LocationOfIncident')
                        #location_of_incident.text = reporting_location
                    #if reporting_time:
                        #time_of_incident = ET.SubElement(discipline_element, 'TimeOfIncident')
                        #time_of_incident.text = reporting_time
         
                #debug_data = ET.SubElement(record, 'DebugData')
                #debug_information = ET.SubElement(debug_data, 'DebugString')
                #debug_information.text = debug_string_to_write
                
                previous_student = consequence['uic']
                
    
    # assemble the actual response to send to the user via attachment
    file_name = 'student_record_maintenance_discipline_' + today_string + '.xml'
    response = HttpResponse(mimetype='application/xml')
    response['Content-Disposition'] = 'attachment; filename=' + file_name
    tree = ET.ElementTree(root)
    tree.write(response)
    return response

def generate_check_csv(request):
    # There are better ways to do this, but the goal is to replicate the XML process as closely as possible
    current_student = ''
    today_string = get_today_string()
    buildingLookup = {'4':'05235','004':'05235', '100':'05235','200':'07190','300':'02186','400':'05166','500':'02187','600':'00308','700':'09148', '800':'00405'}


    # get the data
    by_date = '2011-06-01'
    today = datetime.date.today()
    reported_incidents = []
    
    consequences, consequences_time = list_of_consequences()
    
    file_name = 'BAIT_csv_check_file_' + today_string + '.csv'
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + file_name
    writer = csv.writer(response)    
    writer.writerow(['uic','last_name','first_name', 'dob', 'school', 'grade', 'incident_id', 'event_date', 'disciplinary_action_code', 'length_of_action', 'start_of_action_date'])
    

    counter = 0
    previous_student = 'first'
    for consequence in consequences:
        debug_string = ''
        # we only report when the action involved ISS, OSS, or similar that was greater than .5 days
        if consequence['iss_days'] > .5 or consequence['oss_days']  > .5 or 1==1:
            report_this_action, disciplinary_action_code, start_of_action_date, length_of_action, state_incident_code, reporting_location, debug_string = calculate_action_length_for_reporting(consequence, debug_string)
            # get time when needed
            if state_incident_code in types_needing_time:
                if consequence['mi_time_of_incident'] != 'During school hours':
                    reporting_time = '2'
                else:
                    reporting_time = '1'
            else:
                reporting_time = ''  
                
            
            debug_string_to_write = debug_string #+ consequence['debug_string'] + '-iss_days:' + str(consequence['iss_days']) + '-type:' + str(type(consequence['iss_days'])) + '-oss_days:' + str(consequence['oss_days'])+ '-type:' + str(type(consequence['oss_days'])) 
            if consequence['uic'] == '':
                report_this_action = False
                # means the student was not found
            if start_of_action_date == '':
                report_this_action = False
            
            if report_this_action:
                if previous_student != consequence['uic']:
                
                    csv_uic = consequence['uic'] + ','
                
                    try:
                        csv_last_name = consequence['student_last_name']
                    except:
                        csv_last_name = ''
                    
                    try:
                        csv_first_name = consequence['student_first_name']
                    except:
                        csv_first_name = ''
                    
                    try:
                        csv_dob = consequence['date_of_birth']
                    except:
                        csv_dob = ''
                
                    try:
                        csv_school = consequence['school_id']
                    except:
                        csv_school = ''
                    
                    try:
                        csv_grade = consequence['grade']
                    except:
                        csv_grade = ''
                    
                
                if consequence['mi_incident_id'] not in reported_incidents:
                    reported_incidents.append(consequence['mi_incident_id'])
                    csv_incident_id = consequence['mi_incident_id']

                    csv_event_date = str(consequence['event_date'])

                    current_line = current_line + disciplinary_action_code

                    current_line = current_line + length_of_action + ','
                    
                    current_line = current_line + start_of_action_date + ','
                    
                
                writer.writerow([csv_uic,csv_last_name,csv_first_name, csv_dob, csv_school, csv_grade, csv_incident_id, csv_event_date, disciplinary_action_code, length_of_action, start_of_action_date])

                previous_student = consequence['uic']


    return response



def validation_summary(request):
    debug_string = ''
    oss_totals = []
    iss_totals = []
    if 'number' in request.COOKIES:
        buildingNumber = request.COOKIES['number']
        account = get_object_or_404(Accounts,number=buildingNumber)
    else:
        return HttpResponseRedirect("/discipline/")
    
    # get the data
    by_date = '2011-04-01'
    #discipline_incidents = Incident.objects.filter(event_date__gt = by_date)
    #discipline_consequences = DisciplineAction.objects.filter(created_on__gt = by_date)
    consequences, consequences_time = list_of_consequences(by_date)
    for consequence in consequences:
        report_this_action, disciplinary_action_code, start_of_action_date, length_of_action, state_incident_code, reporting_location = calculate_action_length_for_reporting(consequence)
    #incidents_missing_students = filter(has_no_student, consequences)
    #incidents_missing_consequences = filter(has_no_consequence, consequences)
    #consequences_with_unparsable_students = filter(has_unparsable_student, consequences)
    
    consequences_missing_incidents = []
    #for consequence in discipline_consequences:
        #try:
            #valid_incident = Incident.objects.get(mi_incident_id=consequence.mi_incident_id)
        #except:
            #consequences_missing_incidents.append([consequence.id, consequence.student, consequence.created_on, consequence.last_changed])

    title_string = 'Summary of possible validation issues for ' + str(len(consequences)) + ' incidents'
    return render_to_response('disciplineform_validation_summary.html',
                              {
                                  'account':account,
                                  'head_title': title_string, 
                                  'page_title': title_string, 
                                  'consequences': consequences,
                                  'consequences_time': consequences_time,
                                  #'incidents_missing_students':incidents_missing_students,
                                  #'incidents_missing_consequences':incidents_missing_consequences,
                                  #'consequences_missing_incidents':consequences_missing_incidents,
                                  #'consequences_with_unparsable_students': consequences_with_unparsable_students,
                                  #'oss_totals': oss_totals,
                                  #'iss_totals': iss_totals,
                              })

def show_incidents_no_actions(request):
    if 'number' in request.COOKIES:
        buildingNumber = request.COOKIES['number']
        account = get_object_or_404(Accounts,number=buildingNumber)
    else:
        return HttpResponseRedirect("/discipline/")
    debug_string = ''
    page_title = 'Incidents without associated disciplinary actions'
    all_incidents = Incident.objects.order_by('school_id', 'event_date')
    incident_list = []
    for incident in all_incidents:
        associated_actions_count = DisciplineAction.objects.filter(mi_incident_id=incident.mi_incident_id).count()
        if associated_actions_count == 0:
            item = [incident.id, incident.mi_incident_id, incident.event_date, incident.school_id, incident.location, incident.school_year, incident.description_of_incident]
            incident_list.append(item)
    return render_to_response('disciplineform_show_incidents_no_actions.html',
                              {
                                  'debug_string': debug_string,
                                  'account': account,
                                  'head_title': page_title,
                                  'page_title': page_title,
                                  'incident_list': incident_list,
                              })

def show_actions_no_incidents(request):
    if 'number' in request.COOKIES:
        buildingNumber = request.COOKIES['number']
        account = get_object_or_404(Accounts,number=buildingNumber)
    else:
        return HttpResponseRedirect("/discipline/")
    debug_string = ''
    page_title = 'Disciplinary actions without associated incidents'
    all_actions = DisciplineAction.objects.order_by('school_id', 'student')
    action_list = []
    for action in all_actions:
        associated_incident_count = Incident.objects.filter(mi_incident_id=action.mi_incident_id).count()
        if associated_incident_count == 0:
            item = [action.id, action.student, action.student_grade, action.problem_behaviors_minor, action.problem_behaviors_major, action.school_year]
            action_list.append(item)
    return render_to_response('disciplineform_show_actions_no_incidents.html',
                              {
                                  'debug_string': debug_string,
                                  'account': account,
                                  'head_title': page_title,
                                  'page_title': page_title,
                                  'action_list': action_list,
                              })

def show_students_nonstandard_names(request):
    if 'number' in request.COOKIES:
        buildingNumber = request.COOKIES['number']
        account = get_object_or_404(Accounts,number=buildingNumber)
    else:
        return HttpResponseRedirect("/discipline/")
    debug_string = ''
    page_title = 'Disciplinary actions for students with non-standard names'
    action_list = []
    no_hyphens = DisciplineAction.objects.exclude(student__contains='-')
    for action in no_hyphens:
        list_item = [action.id, action.student, action.school_id, action.student_grade, action.created_on]
        action_list.append(list_item)
    return render_to_response('disciplineform_show_students_nonstandard_names.html',
                              {
                                  'debug_string': debug_string,
                                  'account': account,
                                  'head_title': page_title,
                                  'page_title': page_title,
                                  'action_list': action_list,
                                })

def pyramid_view(request):
    account, school_year_view, require_login = cookie_monster(request)
    school_year_list = get_school_year_list()
    debug_string = ''
    page_title = 'Pyramid view'
    students_in_building = Student.objects.filter(school_id=account.number)
    total_population = len(students_in_building)
    zero_to_one = 0
    two_to_five = 0
    six_or_more = 0
    for student in students_in_building:
        action_count = DisciplineAction.objects.filter(student=student.AutocompleteName).filter(school_year=school_year_view).count()
        if action_count < 2:
            zero_to_one = zero_to_one + 1
        elif action_count < 6:
            two_to_five = two_to_five + 1
        else:
            six_or_more = six_or_more + 1
    return render_to_response('discipline_pyramid_view.html',
                              {
                                  'debug_string': debug_string,
                                  'account': account,
                                  'head_title': page_title,
                                  'page_title': page_title,
                                  'school_year_list': school_year_list,
                                  'total_population': total_population,
                                  'zero_to_one': zero_to_one,
                                  'two_to_five': two_to_five,
                                  'six_or_more': six_or_more,
                                })