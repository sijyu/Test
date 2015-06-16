from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from django import forms

# Create your models here.
class UserManager(BaseUserManager):
	# creates a normal user, a 'volunteer' if I may
	def create_user(self, email, first_name, last_name, address, phone_number, date_of_birth, password):
		now  = timezone.now()
		
		# check if they passed an email
		if not email:
			raise ValueError('The given email is not good')
		email = self.normalize_email(email)
		
		# create the user
		user = self.model(
			email = email,
			first_name = first_name,
			last_name = last_name,
			address = address,
			phone_number = phone_number,
			date_of_birth = date_of_birth,
			start_date = now,
			is_active = False,
			is_staff = False,
			is_superuser = False
		)

		# save the user
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, first_name, last_name, address, phone_number, date_of_birth, password):
		now  = timezone.now()
		
		# check if they passed an email
		if not email:
			raise ValueError('The given email is not good')
		email = self.normalize_email(email)
		
		# create the user
		user = self.model(
			email = email,
			first_name = first_name,
			last_name = last_name,
			address = address,
			phone_number = phone_number,
			date_of_birth = date_of_birth,
			start_date = now,
			is_active = True,
			is_staff = True,
			is_superuser = True
		)
		
		# save the new user
		user.set_password(password)
		user.save(using=self._db)
		return user

# this allows us to define a new user based on the volunteer class 
# this means that we can also create an authentication process that
# uses our Volunteer objects
class User(AbstractBaseUser, PermissionsMixin):
	# there is an implicit primary key that is declared - its just an integer 
	# so if you look at this table there will be a primary key called 'id' that 
	# will be an integer. However, email is still unique and will be used for authentication
	email = models.EmailField(max_length=75, unique=True, db_index=True)
	first_name = models.CharField(max_length=25)
	last_name = models.CharField(max_length=25)
	address = models.CharField(max_length=200)
	phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
	phone_number = models.CharField(validators=[phone_regex], blank=True, max_length=15)
	date_of_birth = models.DateField('Birthday')
	start_date = models.DateField('start date')
	is_active = models.BooleanField(default=False)
	is_staff = models.BooleanField(default = False)
	
	
	# make sure that the username field points to the email address
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = [
		'first_name', 'last_name', 'address', 'phone_number', 'date_of_birth']
	
	objects = UserManager()
	
	def get_full_name(self):
		return self.first_name + " " + self.last_name
		
	def get_short_name(self):
		return self.email
		
	def email_user(self, subject, message, from_email=None):
		send_mail(subject, message, from_email, [self.email])
	
	def __unicode__(self):
		return self.email

#==================================================
#ADMIN
class Volunteer(User):
	class Meta:
		verbose_name = 'Volunteer user'

#==================================================
class Limited(Volunteer):
	class Meta:
		verbose_name = 'Limited User'
#==================================================
class Admin(Limited):
	class Meta:
		verbose_name = 'Admin User'

#==================================================
class Program(models.Model):
	program_name=models.CharField(max_length=50)
	program_start_date=models.DateField()
	program_end_date=models.DateField()
	program_type_choices = (
		('TH', 'Therapeutic'), 
		('RC', 'Recreational'), 
		('VT', 'Veteran'),
		('SP', 'Special'),
	)
	program_type=models.CharField(max_length=50, choices=program_type_choices)

class Vet(models.Model):
	vet_first_name=models.CharField(max_length=50)
	vet_last_name=models.CharField(max_length=50)
	vet_address_street=models.CharField(max_length=50)
	vet_address_suite=models.IntegerField(max_length=10)
	vet_address_city=models.CharField(max_length=50)
	vet_address_state=models.CharField(max_length=2)
	vet_address_zip=models.IntegerField(max_length=10)
	vet_phone=models.IntegerField(max_length=10)
	vet_email=models.CharField(max_length=50)

#=======Person Table======
yes_no=(
		('Y', 'Yes'),
		('N', 'NO'),
	)
class Person(models.Model):
	person_salutation_choices=(
		('Mr.', 'Mr.'),
		('Mrs.', 'Mrs.'),
		('Ms.', 'Ms.'),
		('Dr.', 'Dr.'),
	)
	person_salutation=models.CharField(max_length=4, choices=person_salutation_choices)
	person_first_name=models.CharField(max_length=50)
	person_middle_name=models.CharField(max_length=50)
	person_last_name=models.CharField(max_length=50)
	person_address_street=models.CharField(max_length=50)
	person_address_suite=models.IntegerField(max_length=10)
	person_address_city=models.CharField(max_length=50)
	person_address_state=models.CharField(max_length=2)
	person_address_zip=models.IntegerField(max_length=10)
	person_address_county=models.CharField(max_length=25)
	person_live_within_bloom=models.CharField(max_length=1, choices=yes_no)
	person_home_phone=models.IntegerField(max_length=10)
	person_cell_phone=models.IntegerField(max_length=10)
	person_work_phone=models.IntegerField(max_length=10)
	person_email=models.CharField(max_length=50)
	person_second_email=models.CharField(max_length=50)
	person_communication_preference_choices=(
		('Phone','Phone'), 
		('Email', 'Email'), 
		('Text', 'Text'),
	)
	person_communication_preference=models.CharField(max_length=10, choices=person_communication_preference_choices)
	person_dob=models.DateField()
	person_entered_in_donor_database=models.CharField(max_length=1, choices=yes_no)
	person_community_member=models.CharField(max_length=1, choices=yes_no)
	person_participation_start_date=models.DateField()
	person_participation_end_date=models.DateField()
	person_reason_for_leaving_choices=(
		('Moving', 'Moving'), 
		('Financial', 'Financial'), 
		('Medical', 'Medical'), 
		('Graduated', 'Graduated'), 
		('CSH', 'Completed Service Hours'), 
		('Other', 'Other'),
	)
	person_reason_for_leaving=models.CharField(max_length=20, choices=person_reason_for_leaving_choices)
	#// ^ needs to be checkboxes
	person_consent_medical_release_completed=models.CharField(max_length=1, choices=yes_no)
	person_consent_medical_release_completion_date=models.DateField()
	person_photo_consent_completed=models.CharField(max_length=1, choices=yes_no)
	person_photo_consent_completion_date=models.DateField()
	person_liability_consent_completed=models.CharField(max_length=1, choices=yes_no)
	person_liability_consent_completion_date=models.DateField()
	person_health_history_completed=models.CharField(max_length=1, choices=yes_no)
	person_health_history_completion_date=models.DateField()
	person_note=models.CharField(max_length=500)

#Client Table
	
class Client(Person):
	client_doctor_form_completion_date=models.DateField()
	client_diagnosis_name_choices=(
		('Amputation', 'Amputation'), 
		('Anxiety Dis', 'Anxiety disorder'), 
		('Arthritis/Rheumatoid', 'Arthritis/Rheumatoid Arthritis'), 
		('ADHD', 'Attention Deficit Hyperactivity Disorder'), 
		('Autism', 'autism spectrum (including Aspergers)'),
		('Bipolar', 'Bipolar disorder'), 
		('Borderline','Borderline personality'), 
		('Brain Injury', 'Brain injury'), 
		('CP', 'Cerebral palsy'), 
		('Deression', 'Depression'), 
		('Down Syndrome', 'Down syndrome'), 
		('Dyscalculia', 'Dyscalculia'), 
		('Dyslexia', 'Dyslexia'), 
		('Epilepsy', 'Epilepsy'), 
		('FAS', 'Fetal alcohol syndrome'), 
		('Fibromyalgia', 'Fibromyalgia'), 
		('Fragile X', 'Fragile X syndrome'), 
		('Hearing Impairment', 'Hearing impairment'), 
		('Hypotonia/Hypertonia', 'Hypotonia/Hypertonia'), 
		('Intellectual Disability', 'Intellectual Disability'), 
		('Muscular dystrophy', 'Muscular dystrophy'), 
		('OCD', 'Obsessive compulsive disorder'), 
		('PDD', 'Pervasive development disorder'), 
		('Schizophrenia', 'Schizophrenia'), 
		('Sensory Processing Disorder', 'Sensory processing disorder'), 
		('Speech Delay', 'Speech delay'), 
		('Spina Bifida', 'Spina bifida'), 
		('Visual Impairment', 'Visual impairment'), 
		('Other', 'Other'), 
		('Tramatic Brain Injury', 'Traumatic brain injury'), 
		('PTSD', 'Post traumatic stress disorder'),
	)
	#// ^ needs to be a checkboxes because client can have multiple disabilities; "Other" selection needs to have a text box with it
	client_diagnosis_name=models.CharField(max_length=100, choices=client_diagnosis_name_choices)
	client_disability_category_choices=(
		('Physical', 'Physical'), 
		('Cognitive/Neurological', 'Cognitive/Neurological'), 
		('Social', 'Social'), 
		('Emotional', 'Emotional'), 
		('Developmental', 'Developmental'),
	)
	client_disability_category=models.CharField(max_length=100, choices=client_disability_category_choices)
	#// ^ again, checkboxes because they can be multiple
	client_other_therapies_choices=(
		('PT', 'PT'), 
		('OT', 'OT'), 
		('Speech', 'Speech'), 
		('Other', 'Other'),
	)
	client_other_therapies=models.CharField(max_length=50, choices=client_other_therapies_choices)
	#// checkboxes, also 'Other' needs to have a Text box
	client_scholarship_name=models.CharField(max_length=50)
	client_scholarship_quarter_year=models.CharField(max_length=50)
	client_scholarship_application_date=models.DateField()
	client_scholarship_acceptance_date=models.DateField()
	client_scholarship_disbursement_date=models.DateField()
	client_service_hours_for_quarter_completed=models.CharField(max_length=1)
	client_service_hours_completion_date=models.DateField()
	client_income_bracket_choices=()
	#// ^ don't know what these choices should be; SHOULD BE OPTIONAL
	client_income_bracket=models.CharField(max_length=50, choices=client_income_bracket_choices)
	client_household_size=models.IntegerField(max_length=10)
	client_veteran_WWP_alumni=models.CharField(max_length=1, choices=yes_no)
	client_veteran_military_branch=models.CharField(max_length=50)
	client_veteran_referral_info_choices=(
		('WWP', 'WWP'), 
		('IU', 'IU'), 
		('Ivy Tech', 'Ivy Tech'), 
		('VA Clinic', 'VA'), 
		('Other', 'Other'),
	)
	client_veteran_referral_info=models.CharField(max_length=50, choices=client_veteran_referral_info_choices)
	client_participated_in_fun_show=models.CharField(max_length=1, choices=yes_no)
	client_participated_in_fun_show_date=models.DateField()
	client_participated_in_special_olympics=models.CharField(max_length=1, choices=yes_no)
	client_participated_in_special_olympics_date=models.DateField()

#Staff Table
	
class Staff(Person):
	staff_role=models.CharField(max_length=50)

#Horese Specialist Table
	
class Horse_Specialist(Person):
	specialist_role_choices= (
		('Vet', 'Veterinarian'), 
		('Far', 'Farrier'), 
		('Ch', 'Chiropractor'), 
		('MT', 'Massage Therapist'), 
		('DS', 'Dental Specialist'), 
		('T', 'Trainer'),
	)
	specialist_role_choices= models.CharField(max_length=50, choices= specialist_role_choices)

#Client Specialist Table
	
class client_specialist:
	cspecialist_role_choices= (
		('Vet', 'Veterinarian'), 
		('Far', 'Farrier'), 
		('Ch', 'Chiropractor'), 
		('MT', 'Massage Therapist'), 
		('DS', 'Dental Specialist'), 
		('T', 'Trainer'),
	)
	#// ^^ These are copied from the Horse Specialist, but realistically we need to ask Lindsay what the choices for client specialist should be
	cspecialist_role_choices= models.CharField(max_length=50, choices= cspecialist_role_choices)


# this allows us to define a new user based on the volunteer class 
# this means that we can also create an authentication process that
# uses our Volunteer objects
class Volunteer(AbstractBaseUser, PermissionsMixin):
	# there is an implicit primary key that is declared - its just an integer 
	# so if you look at this table there will be a primary key called 'id' that 
	# will be an integer. However, email is still unique and will be used for authentication
    
#	volunteer_allergies=models.CharField(max_length=100)
#	volunteer_medications=models.CharField(max_length=100)
#	volunteer_health_notes=models.CharField(max_length=100)	
    
	volunteer_high_school_grad_date=models.DateField(null=True, blank=True) # replace null = True.... with name as done for date_of_birth
	volunteer_college_name=models.CharField(max_length=50)
	volunteer_college_grad_date=models.DateField(null=True, blank=True)
	volunteer_orientation_date=models.DateField(null=True, blank=True)
	leader_training1_start_date=models.DateField(null=True, blank=True)
	leader_training1_end_date=models.DateField(null=True, blank=True)
	leader_training2_start_date=models.DateField(null=True, blank=True)
	leader_training2_end_date=models.DateField(null=True, blank=True)
	stable_manager_training_start_date=models.DateField(null=True, blank=True)
	stable_manager_training_end_date=models.DateField(null=True, blank=True)
	volunteer_community_member=models.CharField(max_length=1, choices=yes_no)
	volunteer_board_member=models.CharField(max_length=1, choices=yes_no)
	volunteer_board_member_start_date=models.DateField(null=True, blank=True)
	volunteer_board_member_end_date=models.DateField(null=True, blank=True)
	volunteer_horse_experience=models.CharField(max_length=1, choices=yes_no)
	volunteer_horse_experience_details=models.CharField(max_length=100)
	volunteer_experience_with_disabilities=models.CharField(max_length=1, choices=yes_no)
	volunteer_experience_with_disabilities_details=models.CharField(max_length=100)
	volunteer_computer_skills_details=models.CharField(max_length=100)
	volunteer_facility_maintenance_experience_details=models.CharField(max_length=100)
	volunteer_construction=models.CharField(max_length=1, choices=yes_no)
	volunteer_lift_fifty_lbs=models.CharField(max_length=1, choices=yes_no)
	volunteer_language_proficiency=models.CharField(max_length=50)
	volunteer_CPR_trained=models.CharField(max_length=1, choices=yes_no)
	volunteer_landscaping=models.CharField(max_length=1, choices=yes_no)
	volunteer_skill_fundraising=models.CharField(max_length=1, choices=yes_no)
	volunteer_skill_PR=models.CharField(max_length=1, choices=yes_no)
	volunteer_skills_other=models.CharField(max_length=500)
	volunteer_of_month_recognition=models.DateField(null=True, blank=True)
	volunteer_of_year_recognition=models.DateField(null=True, blank=True)

class Committee_volunteer(Volunteer):
	cvolunteer_committee_name=models.CharField(max_length=50)
	#// volunteer can be a part of multiple committees... will most likely need to be a checkbox but we haven't been given any of the committee names yet

class Admin_volunteer(Volunteer):
	avolunteer_role_choices=(
		('Intern', 'Intern'), 
		('SL', 'Service Learner'), 
		('OV', 'Office Volunteer')
	)
	avolunteer_role=models.CharField(max_length=50, choices=avolunteer_role_choices)
	avolunteer_academic_institution=models.CharField(max_length=100)
	avolunteer_for_credit=models.CharField(max_length=1, choices=yes_no)
	avolunteer_hours_required=models.IntegerField(max_length=3)
	avolunteer_level=models.CharField(max_length=100)
	avolunteer_staff_supervisor=models.ForeignKey(Person)

class Program_volunteer(Volunteer):
	pvolunteer_role_choices=(
		('Intern', 'Intern'), 
		('SL', 'Service Learner'), 
		('General', 'General')
	)
	pvolunteer_role=models.CharField(max_length=20, choices=pvolunteer_role_choices)
	pvolunteer_position_choices=(
		('L', 'Leader'),
		('SW', 'Side walker'), 
		('SM', 'Stable manager'), 
		('AO', 'Aisle only'),
	)
	#// ^ needs to be a checkbox because these are not exclusive positions
	pvolunteer_position=models.CharField(max_length=1, choices=pvolunteer_position_choices)
	pvolunteer_academic_institution=models.CharField(max_length=100)
	pvolunteer_for_credit=models.CharField(max_length=1, choices=yes_no)
	pvolunteer_level=models.CharField(max_length=100)
	pvolunteer_staff_supervisor=models.ForeignKey(Person)


class Emergency_contact(models.Model):
	contact_first_name=models.CharField(max_length=50)
	contact_last_name=models.CharField(max_length=50)
	contact_phone=models.IntegerField(max_length=10)
	contact_relationship_to_client=models.CharField(max_length=100)
	contact_client=models.ForeignKey(Person)
#horse
class Horse_Medical(models.Model):
	pass

# horse
class Horse(models.Model):
	gender_list= ( 
		('male', 'male'), 
		('female', 'female'), 
	)
	horse_name=models.CharField(max_length=100)
	horse_dob=models.DateField()
	horse_sex=models.CharField(max_length=6, choices=gender_list) #default=male)
	horse_breed=models.CharField(max_length=50)
	horse_height=models.CharField(max_length=50)
	horse_weight=models.CharField(max_length=50)
	horse_color_markings=models.CharField(max_length=50)
	horse_saddle_number=models.IntegerField(max_length=50)
	donation_date=models.DateField()
	horse_trail_approval_date=models.DateField()
	registration_organization=models.CharField(max_length=50)
	acceptance_date=models.DateField()
	leaving_date=models.DateField()
	horse_donor_first_name=models.CharField(max_length=50)
	horse_donor_last_name=models.CharField(max_length=50)
	horse_donor_phone_number_home=models.CharField(max_length=50)
	horse_donor_phone_number_cell=models.CharField(max_length=50)
	horse_donor_email=models.CharField(max_length=50)
	horse_donor_address_street=models.CharField(max_length=50)
	horse_donor_address_suite=models.IntegerField(max_length=10)
	horse_donor_address_city=models.CharField(max_length=50)
	horse_donor_address_state=models.CharField(max_length=2)
	horse_donor_address_zip=models.IntegerField(max_length=10)
	horse_boarder_address_street=models.CharField(max_length=50)
	horse_boarder_address_suite=models.IntegerField(max_length=10)
	horse_boarder_address_city=models.CharField(max_length=50)
	horse_boarder_address_state=models.CharField(max_length=2)
	horse_boarder_address_zip=models.IntegerField(max_length=10)
	donation_agreement_additions=models.CharField(max_length=3, choices=yes_no)
	#horse_medical_history=models.ForeignKey(Horse_Medical)
	horse_sponsor_level=models.CharField(max_length=50)
	horse_sponsor_donor=models.CharField(max_length=50)
	horse_sponsorship_start_date=models.DateField()
	horse_sponsorship_end_date=models.DateField()
	horse_note=models.CharField(max_length=500)

class Medical_Farrier(Horse_Medical):
	horse_farrier_name=models.ForeignKey(Horse_Specialist)     #(foreign key from Horse Specialist Table)
	last_farrier_appointment=models.DateField()
	farrier_appointment_notes=models.CharField(max_length=500)

class Spring_Immunizations(models.Model):
	immunization_date=models.DateField()
	immunizations_received=models.CharField(max_length=500)
	immunization_notes=models.CharField(max_length=500)

class Fall_Immunizations(models.Model):
	immunization_date=models.DateField()
	immunizations_received=models.CharField(max_length=500)
	immunization_notes=models.CharField(max_length=500)

class Wormer_History(models.Model):
	appointment_date=models.DateField()
	appointment_notes=models.CharField(max_length=500)

class Medical_Vet(Horse_Medical):
	horse_medications=models.CharField(max_length=500)
	horse_immunization_records_spring_shots=models.ForeignKey(Spring_Immunizations)
	horse_immunization_records_fall_shots=models.ForeignKey(Fall_Immunizations)
	horse_wormer_history=models.ForeignKey(Wormer_History)
	horse_allergies_notes=models.CharField(max_length=500)
	dietary_notes=models.CharField(max_length=500)
	horse_vet_name=models.ForeignKey(Horse_Specialist)         #(foreign key from Specialist Table)
	horse_last_vet_appointment_date=models.DateField()
	horse_last_vet_appointment_notes=models.CharField(max_length=500)
	Injury_date=models.DateField()
	Injury_medications=models.CharField(max_length=50)
	Injury_pals_employee=models.CharField(max_length=50)
	Injury_notes=models.CharField(max_length=50)
	last_teeth_floating=models.DateField()
#participation

class Participation (models.Model): 
	participation_persion = models.ForeignKey(Person) 
	participation_program = models.ForeignKey(Program) 
	participation_horse=models.ForeignKey(Horse)
	participation_tack_notes=models.CharField(max_length=100)
	participation_session_day=models.DateField()
	participation_session_time=models.CharField(max_length=100)
	participation_quarter=models.CharField(max_length=50)
	participation_year=models.CharField(max_length=50)

class Goals(models.Model):
	#yes_no=('Y', 'N')
	participation=models.ForeignKey(Participation)
	client=models.ForeignKey(Person)
	goal_code=models.CharField(max_length=50)
	goal_met=models.CharField(max_length=1, choices=yes_no)
	goal_notes=models.CharField(max_length=500)

		
# these are the four choices from which a worker can select when clocking in
WORK_CHOICES = (
	('a', 'Administration'),
	('s', 'Staff'),
	('v', 'Volunteer'),
	('o', 'Other'),
)
		
class Log(models.Model):
	# there is an implicit primary key that is declared - its just an integer 
	# so if you look at this table there will be a primary key called 'id' that 
	# will be an integer
	volunteer = models.ForeignKey(Volunteer)
	clock_in = models.DateTimeField('in')
	clock_out = models.DateTimeField('out', default=None, null=True)
	total_hours = models.FloatField(default=0)
	work_type = models.CharField(max_length=1, choices=WORK_CHOICES)
	
	def set_total_hours(self):
		if self.clock_out:
			diff = self.clock_out - self.clock_in
			minutes = diff.days * 1440 + diff.seconds // 60
			self.total_hours = float(minutes) / 60
		else:
			print "can't do that yet - you need to clock out"
	
	def __unicode__(self):
		return "clock-in: " + str(self.clock_in) + " clock-out: " + str(self.clock_out)

    
class MedicalInformtaion(forms.Form):
    volunteer_allergies = forms.CharField(max_length=100)
    volunteer_medications = forms.CharField(max_length=100)
    volunteer_health_notes = forms.CharField(max_length=100)	
    
class RegiForm(forms.Form):
	email = forms.EmailField(max_length=75)
	first_name = forms.CharField(max_length=25)
	last_name = forms.CharField(max_length=25)
	address = forms.CharField(max_length=200)
	phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
	phone_number = forms.CharField(validators=[phone_regex], max_length=15)
	date_of_birth = forms.DateField()
	start_date = forms.DateField()
	contact_first_name = forms.CharField(max_length=25)
	contact_last_name = forms.CharField(max_length=25)
	contact_phone_number = forms.CharField(validators=[phone_regex], max_length=15)
	relation_to_contact = forms.CharField(max_length=200)
	password = forms.CharField(max_length=25)
	
    


			
