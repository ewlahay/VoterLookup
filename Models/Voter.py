from sqlalchemy.orm import relationship

from Database import db
from sqlalchemy import Column, String, Integer, Boolean, CHAR


class Voter(db.Model):
	__tablename__ = "voters"
	county_id = Column(Integer)
	county_desc = Column(String)
	voter_reg_num = Column(Integer, primary_key=True)
	status_cd = Column(CHAR(1))
	voter_status_desc = Column(String)
	reason_cd = Column(CHAR(2))
	voter_status_reason_desc = Column(String)
	absent_ind = Column(String)
	name_prefx_cd = Column(String)
	last_name = Column(String)
	first_name = Column(String)
	middle_name = Column(String)
	name_suffix_lbl = Column(String)
	res_street_address = Column(String)
	res_city_desc = Column(String)
	state_cd = Column(CHAR(2))
	zip_code = Column(String)
	mail_addr1 = Column(String)
	mail_addr2 = Column(String)
	mail_addr3 = Column(String)
	mail_addr4 = Column(String)
	mail_city = Column(String)
	mail_state = Column(String)
	mail_zipcode = Column(String)
	full_phone_number = Column(String)
	race_code = Column(CHAR(1))
	ethnic_code = Column(CHAR(2))
	party_cd = Column(String)
	gender_code = Column(CHAR(1))
	birth_age = Column(Integer)
	birth_state = Column(CHAR(2))
	drivers_lic = Column(Boolean)
	registr_dt = Column(String)
	precinct_abbrv = Column(String)
	precinct_desc = Column(String)
	municipality_abbrv = Column(String)
	municipality_desc = Column(String)
	ward_abbrv = Column(String)
	ward_desc = Column(String)
	cong_dist_abbrv = Column(String)
	super_court_abbrv = Column(String)
	judic_dist_abbrv = Column(String)
	nc_senate_abbrv = Column(String)
	nc_house_abbrv = Column(String)
	county_commiss_abbrv = Column(String)
	county_commiss_desc = Column(String)
	township_abbrv = Column(String)
	township_desc = Column(String)
	school_dist_abbrv = Column(String)
	school_dist_desc = Column(String)
	fire_dist_abbrv = Column(String)
	fire_dist_desc = Column(String)
	water_dist_abbrv = Column(String)
	water_dist_desc = Column(String)
	sewer_dist_abbrv = Column(String)
	sewer_dist_desc = Column(String)
	sanit_dist_abbrv = Column(String)
	sanit_dist_desc = Column(String)
	rescue_dist_abbrv = Column(String)
	rescue_dist_desc = Column(String)
	munic_dist_abbrv = Column(String)
	munic_dist_desc = Column(String)
	dist_1_abbrv = Column(String)
	dist_1_desc = Column(String)
	dist_2_abbrv = Column(String)
	dist_2_desc = Column(String)
	confidential_ind = Column(Boolean)
	birth_year = Column(Integer)
	ncid = Column(String)
	vtd_abbrv = Column(String)
	vtd_desc = Column(String)
	history = relationship('History', backref='voter', uselist=True)

	def __init__(self, string:str):
		values = string.split('"\t"')
		self.county_id = int(values[0][1:])
		self.county_desc = values[1]
		self.voter_reg_num = int(values[2])
		self.status_cd = values[3]
		self.voter_status_desc = values[4]
		self.reason_cd = values[5]
		self.voter_status_reason_desc = values[6]
		self.absent_ind = values[7]
		self.name_prefx_cd = values[8]
		self.last_name = values[9]
		self.first_name = values[10]
		self.middle_name = values[11]
		self.name_suffix_lbl = values[12]
		self.res_street_address = values[13]
		self.res_city_desc = values[14]
		self.state_cd = values[15]
		self.zip_code = values[16]
		self.mail_addr1 = values[17]
		self.mail_addr2 = values[18]
		self.mail_addr3 = values[19]
		self.mail_addr4 = values[20]
		self.mail_city = values[21]
		self.mail_state = values[22]
		self.mail_zipcode = values[23]
		self.full_phone_number = values[24]
		self.race_code = values[25]
		self.ethnic_code = values[26]
		self.party_cd = values[27]
		self.gender_code = values[28]
		self.birth_age = int(values[29])
		self.birth_state = values[30]
		self.drivers_lic = values[31] == "Y"
		self.registr_dt = values[32]
		self.precinct_abbrv = values[33]
		self.precinct_desc = values[34]
		self.municipality_abbrv = values[35]
		self.municipality_desc = values[36]
		self.ward_abbrv = values[37]
		self.ward_desc = values[38]
		self.cong_dist_abbrv = values[39]
		self.super_court_abbrv = values[40]
		self.judic_dist_abbrv = values[41]
		self.nc_senate_abbrv = values[42]
		self.nc_house_abbrv = values[43]
		self.county_commiss_abbrv = values[44]
		self.county_commiss_desc = values[45]
		self.township_abbrv = values[46]
		self.township_desc = values[47]
		self.school_dist_abbrv = values[48]
		self.school_dist_desc = values[49]
		self.fire_dist_abbrv = values[50]
		self.fire_dist_desc = values[51]
		self.water_dist_abbrv = values[51]
		self.water_dist_desc = values[53]
		self.sewer_dist_abbrv = values[54]
		self.sewer_dist_desc = values[55]
		self.sanit_dist_abbrv = values[56]
		self.sanit_dist_desc = values[57]
		self.rescue_dist_abbrv = values[58]
		self.rescue_dist_desc = values[59]
		self.munic_dist_abbrv = values[60]
		self.munic_dist_desc = values[61]
		self.dist_1_abbrv = values[62]
		self.dist_1_desc = values[63]
		self.dist_2_abbrv = values[64]
		self.dist_2_desc = values[65]
		self.confidential_ind = values[66] == "Y"
		self.birth_year = int(values[67])
		self.ncid = values[68]
		self.vtd_abbrv = values[69]
		self.vtd_desc = values[70][:-1]

	def save(self):
		db.session.add(self)
		db.session.commit()
