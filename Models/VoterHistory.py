from Database import db
from sqlalchemy import Column, String, Integer, ForeignKey


class History(db.Model):
	__tablename__ = "history"

	id = Column(Integer, primary_key=True, autoincrement=True)
	county_id = Column(Integer)
	county_desc = Column(String)
	voter_reg_num = Column(Integer, ForeignKey('voters.voter_reg_num'))
	election_lbl = Column(String)
	election_desc = Column(String)
	voting_method = Column(String)
	voted_party_cd = Column(String)
	voted_party_desc = Column(String)
	pct_label = Column(String)
	pct_description = Column(String)
	ncid = Column(String)
	voted_county_id = Column(Integer)
	voted_county_desc = Column(String)
	vtd_label = Column(String)
	vtd_description = Column(String)

	def __init__(self, string):
		values = string.split(sep='"\t"')
		self.county_id = int(values[0][1:])
		self.county_desc = values[1]
		self.voter_reg_num = int(values[2])
		self.election_lbl = values[3]
		self.election_desc = values[4]
		self.voting_method = values[5]
		self.voted_party_cd = values[6]
		self.voted_party_desc = values[7]
		self.pct_label = values[8]
		self.pct_description = values[9]
		self.ncid = values[10]
		self.voted_county_id = int(values[11])
		self.voted_county_desc = values[12]
		self.vtd_label = values[13]
		self.vtd_description = values[14][:-1]

	def save(self):
		db.session.add(self)
		db.session.commit()
