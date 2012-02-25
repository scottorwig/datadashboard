from django.db import models

LOCATION_CHOICES = (
    (u'Art Room',u'Art Room'),
    (u'Bathroom',u'Bathroom'),
    (u'Bus',u'Bus'),
    (u'Bus loading zone',u'Bus loading zone'),
    (u'Cafeteria',u'Cafeteria'),
    (u'Classroom',u'Classroom'),
    (u'Commons area',u'Commons area'),
    (u'Gym',u'Gym'),
    (u'Hallway',u'Hallway'),
    (u'Library',u'Library'),
    (u'Media Room',u'Media Room'),
    (u'Music Room',u'Music Room'),
    (u'Office',u'Office'),
    (u'Other', u'Other'),
    (u'Parking lot',u'Parking lot'),
    (u'Playground',u'Playground'),
    (u'Restricted area',u'Restricted area'),
    (u'School Function - On property',u'School Function - On property'),
    (u'School Function - Off property',u'School Function - Off property'),
    (u'Special Event or Assembly',u'Special Event or Assembly'),
    (u'Technology Area', u'Technology Area'),
  
)
HOUR_CHOICES = (
    (u'05',u'5 AM'),
    (u'06',u'6 AM'),
    (u'07',u'7 AM'),
    (u'08',u'8 AM'),
    (u'09',u'9 AM'),
    (u'10',u'10 AM'),
    (u'11',u'11 AM'),
    (u'12',u'12 PM'),
    (u'13',u'1 PM'),
    (u'14',u'2 PM'),
    (u'15',u'3 PM'),
    (u'16',u'4 PM'),
    (u'17',u'5 PM'),
    (u'18',u'6 PM'),
    (u'19',u'7 PM'),
    (u'20',u'8 PM'),
    (u'21',u'9 PM'),
)
MINUTE_CHOICES = (
    (u'00',u'00'),
    (u'05',u'05'),
    (u'10',u'10'),
    (u'15',u'15'),
    (u'20',u'20'),
    (u'25',u'25'),
    (u'30',u'30'),
    (u'35',u'35'),
    (u'40',u'40'),
    (u'45',u'45'),
    (u'50',u'50'),
    (u'55',u'55'),
)

GRADES_CHOICES = (
    (u'00',u'Kindergarten'),
    (u'01',u'First Grade '),
    (u'02',u'Second Grade'),
    (u'03',u'Third Grade'),
    (u'04',u'Fourth Grade'),
    (u'05',u'Fifth Grade'),
    (u'06',u'Sixth Grade'),
    (u'07',u'Seventh Grade'),
    (u'08',u'Eighth Grade'),
    (u'09',u'Ninth Grade'),
    (u'10',u'Tenth Grade'),
    (u'11',u'Eleventh Grade'),
    (u'12',u'Twelfth Grade'),
    (u'14',u'Special Education'),
    (u'20',u'Adult Education'),
    (u'30',u'Early Childhood'),
    )
SCHOOL_DAY_CHOICES = (
    (u'During school hours',u'During school hours'),
    (u'Outside of school hours',u'Outside of school hours'),
)
PROBLEM_BEHAVIORS_MINOR_CHOICES = (
    (u'Boy-girl talk',u'Boy-girl talk'),
    (u'Defiance or Non-compliance (back talk)',u'Defiance or Non-compliance (back talk)'),
    (u'Disruption (agitation)',u'Disruption (agitation)'),
    (u'Dress code',u'Dress code'),
    (u'Driving violation',u'Driving violation'),
    (u'Failure to serve detention',u'Failure to serve detention'),
    (u'Gambling',u'Gambling'),
    (u'Gossip',u'Gossip'),
    (u'Inappropriate language',u'Inappropriate language'),
    (u'Lying, cheating',u'Lying, cheating'),
    (u'Physical contact',u'Physical contact'),
    (u'Property misuse',u'Property misuse'),
    (u'Technology violation',u'Technology violation'),
    (u'Tardy',u'Tardy'),
    (u'Other',u'Other'),
)
PROBLEM_BEHAVIORS_MAJOR_CHOICES = (
    (u'Abusive language',u'Abusive language'),
    (u'Aggravated or felonious assault',u'Aggravated or felonious assault'),
    (u'Alcohol distribution',u'Alcohol distribution'),
    (u'Alcohol possession',u'Alcohol possession'),
    (u'Alcohol - under the influence',u'Alcohol - under the influence'),
    (u'Arson',u'Arson'),
    (u'Bomb or similar threat',u'Bomb or similar threat'),
    (u'Breaking and entering',u'Breaking and entering'),
    (u'Burglary',u'Burglary'),
    (u'Combustibles',u'Combustibles'),
    (u'Damage to property',u'Damage to property'),
    (u'Disability intimidation',u'Disability intimidation'),
    (u'Disability slur',u'Disability slur'),
    (u'Disrespect to staff or insubordination',u'Disrespect to staff or insubordination'),
    (u'Disruption of the educational process',u'Disruption of the educational process'),
    (u'Drugs or narcotics distribution',u'Drugs or narcotics distribution'),
    (u'Drugs or narcotics possession',u'Drugs or narcotics possession'),
    (u'Drugs or narcotics - under the influence',u'Drugs or narcotics - under the influence'),
    (u'Extortion',u'Extortion'),
    (u'False alarm',u'False alarm'),
    (u'Fighting',u'Fighting'),
    (u'Forgery',u'Forgery'),
    (u'Fraud or bribery',u'Fraud or bribery'),
    (u'Gambling',u'Gambling'),
    (u'Graffiti',u'Graffiti'),
    (u'Handgun',u'Handgun'),
    (u'Harrassment, bullying, teasing',u'Harrassment, bullying, teasing'),
    (u'Homicide',u'Homicide'),
    (u'Inappropriate display of affection',u'Inappropriate display of affection'),
    (u'Inciting or verbal threats',u'Inciting or verbal threats'),
    (u'Intimidation - Gender',u'Intimidation - Gender'),
    (u'Intimidation - Racial or ethnic',u'Intimidation - Racial or ethnic'),
    (u'Intimidation - Religion',u'Intimidation - Religion'),
    (u'Intimidation - Sexual orientation',u'Intimidation - Sexual orientation'),
    (u'Intimidation - Stalking',u'Intimidation - Stalking'),
    (u'Kidnapping',u'Kidnapping'),
    (u'Larceny or theft',u'Larceny or theft'),
    (u'Leaving school grounds',u'Leaving school grounds'),
    (u'Loitering',u'Loitering'),
    (u'Lying, cheating',u'Lying, cheating'),
    (u'Other', u'Other'),
    (u'Other dangerous weapons',u'Other dangerous weapons'),
    (u'Other firearms',u'Other firearms'),
    (u'Other violence',u'Other violence'),
    (u'Physical aggression',u'Physical aggression'),
    (u'Physical assault',u'Physical assault'),
    (u'Overt Defiance, disrespect',u'Overt Defiance, disrespect'),
    (u'Racial or ethnic intimidation',u'Racial or ethnic intimidation'),
    (u'Racial or ethnic slur',u'Racial or ethnic slur'),
    (u'Refusal to identify self',u'Refusal to identify self'),
    (u'Rifle or shotgun',u'Rifle or shotgun'),
    (u'Sexual harassment',u'Sexual harassment'),
    (u'Skipping class',u'Skipping class'),
    (u'Trespassing',u'Trespassing'),
    (u'Religion intimidation',u'Religion intimidation'),
    (u'Religion slur',u'Religion slur'),
    (u'Robbery',u'Robbery'),
    (u'Sexual assault',u'Sexual assault'),
    (u'Sexual orientation intimidation',u'Sexual orientation intimidation'),
    (u'Sexual orientation slur',u'Sexual orientation slur'),
    (u'Tobacco',u'Tobacco'),
)


POSSIBLE_MOTIVATION_CHOICES = (
    (u'Obtain peer attention',u'Obtain peer attention'),
    (u'Obtain adult attention',u'Obtain adult attention'),
    (u'Obtain items, activities',u'Obtain items, activities'),
    (u'Avoid tasks, activities',u'Avoid tasks, activities'),
    (u'Avoid peers',u'Avoid peers'),
    (u'Avoid adults',u'Avoid adults'),
    (u'Dont know',u'Dont know'),
    (u'Other',u'Other'),
)

VICTIM_CHOICES = (
    (u'No Victim',u'No Victim'),
    (u'Another student',u'Another student'),
    (u'Teacher',u'Teacher'),
    (u'Administrator',u'Administrator'),
    (u'Other staff member',u'Other staff member'),
    (u'School-based law enforcement',u'School-based law enforcement'),
    (u'Contractor or non-school personnel',u'Contractor or non-school personnel'),
    (u'School volunteer',u'School volunteer'),
)

FOLLOWUP_CHOICES = (
    (u'Referred to CMH',u'Referred to CMH'),
)

class Accounts(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=50)
    number = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name

class Student(models.Model):
    StudentNumber = models.CharField(max_length=20,primary_key=True)
    NameFirst = models.CharField(max_length=30)
    NameLast = models.CharField(max_length=30)
    school_id = models.CharField(max_length=10,blank=True,null=True)
    SpecialEdEligible = models.BooleanField(default=False)
    AutocompleteName = models.CharField(max_length=100)
    UIC = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    grade = models.CharField(max_length=10, blank=True, null=True)
    ethnicity = models.CharField(max_length=20, blank=True, null=True)
    exit_status = models.CharField(max_length=20, blank=True, null=True)
    entry_date = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=10, blank=True, null=True)
    zip = models.CharField(max_length=20, blank=True, null=True)
    
    

    def __unicode__(self):
        return self.AutocompleteName
    
class Staff(models.Model):
    StaffNumber = models.CharField(max_length=20,primary_key=True)
    NameFirst = models.CharField(max_length=30,blank=True,null=True)
    NameLast = models.CharField(max_length=30)
    school_id = models.CharField(max_length=10,blank=True,null=True)
    AutocompleteName = models.CharField(max_length=100, blank=True,null=True)

    def __unicode__(self):
        return self.AutocompleteName

class Incident(models.Model):
    school_id = models.CharField(max_length=10, blank=True,null=True)
    referrer = models.CharField(max_length=40, blank=True,null=True)
    event_time = models.CharField(max_length=20, blank=True,null=True)
    event_date = models.DateField(auto_now_add=False)
    location = models.CharField(max_length=30, choices=LOCATION_CHOICES,null=True)
    #location_notes = models.TextField(blank=True,null=True)
    description_of_incident = models.TextField(blank=True,null=True)
    #administrative_comments = models.TextField(blank=True,null=True)
    created_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    last_changed = models.DateTimeField(auto_now=True, blank=True, null=True)
    event_hour = models.CharField(max_length=10, choices=HOUR_CHOICES)
    event_minute = models.CharField(max_length=10, choices=MINUTE_CHOICES)
    classroom_teacher = models.CharField(max_length=50, blank=True, null=True)
    mi_incident_id = models.CharField(max_length=10, blank=True, null=True)
    #estimated_cost = models.IntegerField(blank=True, null=True, default=0)
    #primary_victim = models.CharField(max_length=50, choices=VICTIM_CHOICES)
    mi_time_of_incident = models.CharField(max_length=50, choices=SCHOOL_DAY_CHOICES)
    reported_to_state = models.CharField(max_length=20, blank=True, null=True)
    school_year = models.CharField(max_length=20, blank=True, null=True)
    def __unicode__(self):
        return str(self.mi_incident_id)

class DisciplineAction(models.Model):
    #incident = models.ForeignKey(Incident)
    student = models.CharField(max_length=100, blank=True,null=True)
    student_grade = models.CharField(max_length=5,blank=True, choices=GRADES_CHOICES)
    rule_broken_respectful = models.BooleanField("Respectful")
    rule_broken_responsible = models.BooleanField("Responsible")
    rule_broken_safe = models.BooleanField("Safe")
    problem_behaviors_minor = models.CharField("Minor problem behaviors", max_length=100, blank=True,null=True, choices=PROBLEM_BEHAVIORS_MINOR_CHOICES)
    problem_behaviors_minor_comment = models.TextField(blank=True,null=True)
    problem_behaviors_major = models.CharField("Major problem behaviors", max_length=100, blank=True,null=True, choices=PROBLEM_BEHAVIORS_MAJOR_CHOICES)
    problem_behaviors_major_comment = models.TextField(blank=True,null=True)
    prior_conference_with_student = models.DateField("Conference with student", auto_now=False, auto_now_add=False,blank=True,null=True)
    prior_changed_student_seat = models.DateField("Changed students seat",auto_now=False, auto_now_add=False,blank=True,null=True)
    prior_consulted_counselor = models.DateField("Consulted Counselor",auto_now=False, auto_now_add=False,blank=True,null=True)
    prior_counselor_conference = models.DateField("Counselor conference",auto_now=False, auto_now_add=False,blank=True,null=True)
    prior_parent_contact = models.DateField("Parent Contact",auto_now=False, auto_now_add=False,blank=True,null=True)
    prior_other_date = models.DateField("Other",auto_now=False, auto_now_add=False,blank=True,null=True)
    prior_other_notes = models.TextField("If other, please describe",blank=True,null=True)
    admin_student_conference = models.DateField("Admin/Student Conference",auto_now=False, auto_now_add=False,blank=True,null=True)
    admin_parent_teacher_conference = models.DateField("Admin/Parent/Teacher Conference",auto_now=False, auto_now_add=False,blank=True,null=True)
    admin_warning = models.DateField("Administrative Warning",auto_now=False, auto_now_add=False,blank=True,null=True)
    admin_phone_call_to_parent = models.DateField("Phone call to parent",auto_now=False, auto_now_add=False,blank=True,null=True)
    admin_letter_home = models.DateField("Letter/certified letter sent home",auto_now=False, auto_now_add=False,blank=True,null=True)
    iss_start_date = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    iss_end_date = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    iss_number_days = models.DecimalField(max_digits=7, decimal_places=2, blank=True,null=True)
    oss_start_date = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    oss_end_date = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    oss_number_days = models.DecimalField(max_digits=7, decimal_places=2, blank=True,null=True)
    detention_start_date = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    detention_end_date = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    detention_number_days = models.DecimalField(max_digits=7, decimal_places=2, blank=True,null=True)
    expulsion_start_date = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    expulsion_end_date = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    expulsion_number_days = models.DecimalField(max_digits=7, decimal_places=2, blank=True,null=True)
    other_admin_action = models.TextField(blank=True,null=True)
    parent_conference_required = models.BooleanField(blank=True,null=True)
    return_date = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    parent_signature_date = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    student_signature_date = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    teacher_signature_date = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    administrator_signature_date = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    created_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    last_changed = models.DateTimeField(auto_now=True, blank=True, null=True)
    extracted_for_powerschool = models.BooleanField(blank=True, null=True)
    school_id = models.CharField(max_length=10, blank=True,null=True)
    mi_incident_id = models.CharField(max_length=10, blank=True, null=True)
    count1 = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    count2 = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    count3 = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    count4 = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    school_year = models.CharField(max_length=20, blank=True, null=True)
    def __unicode__(self):
        return self.student + ' incident ' + self.mi_incident_id