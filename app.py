from flask import Flask
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import redirect

from Database import db
from Models import Voter, History
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from flask_graphql import GraphQLView
import os

VOTER_LIMIT = 50  # Maximum number of results per query to limit excessive ram usage
HISTORY_LIMIT = 10
app = Flask("VoterLookup")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///voters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = os.urandom(24)
db.init_app(app)
db.create_all(app=app)


# Schema Objects
class VoterObject(SQLAlchemyObjectType):
	class Meta:
		model = Voter
		interfaces = (graphene.relay.Node,)


class VoterHistoryObject(SQLAlchemyObjectType):
	class Meta:
		model = History
		interfaces = (graphene.relay.Node,)


voterData = '"1"\t"ALAMANCE"\t"000009144385"\t"I"\t"INACTIVE"\t"IN"\t"CONFIRMATION NOT RETURNED"\t" "\t" "\t"AARON"\t"SANDRA"\t"ESCOBAR"\t""\t"1013  EDITH ST   "\t"BURLINGTON"\t"NC"\t"27215"\t"1013 EDITH ST"\t""\t""\t""\t"BURLINGTON"\t"NC"\t"27215"\t""\t"W"\t"HL"\t"UNA"\t"F"\t"44"\t""\t"N"\t"12/05/2013"\t"124"\t"BURLINGTON 4"\t"BUR"\t"BURLINGTON"\t""\t""\t"13"\t"15A"\t"15A"\t"24"\t"063"\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""\t"BUR"\t"BURLINGTON"\t"17"\t"17TH PROSECUTORIAL"\t" "\t" "\t"N"\t"1975"\t"AA181361"\t"124"\t"124"'
sampleVoter = Voter(voterData)
sampleHistory = History(
	'"1"\t"ALAMANCE"\t"000009050405"\t"11/04/2014"\t"11/04/2014 GENERAL"\t"IN-PERSON"\t"REP"\t"REPUBLICAN"\t"09S"\t"SOUTH THOMPSON"\t"AA100006"\t"1"\t"ALAMANCE"\t"09S"\t"09S"')
types = {type(""): graphene.String(), type(True): graphene.Boolean(), type(int()): graphene.Int(),
         type(None): graphene.Int()}

with app.app_context():
	remove = {"id", "query", "metadata", "history"}
	filterParams = {}
	for a in dir(Voter):
		if not a.startswith('_') and not callable(getattr(Voter, a)) and a not in remove:
			filterParams[a] = types[type(getattr(sampleVoter, a))]
	recordsParams = {}
	for a in dir(History):
		if not a.startswith('_') and not callable(getattr(History, a)) and a not in remove:
			recordsParams[a] = types[type(getattr(sampleHistory, a))]

	props = {key for (key, value) in filterParams.items()}
	histProps = {key for (key, value) in recordsParams.items()}


class Query(graphene.ObjectType):
	node = graphene.relay.Node.Field()
	voters = SQLAlchemyConnectionField(VoterObject, sort=VoterObject.sort_argument(), **filterParams)
	voting_records = SQLAlchemyConnectionField(VoterHistoryObject, **recordsParams)

	def resolve_voters(self, info, **kwargs):
		"""Allows filtering by any of the voter class's attributes"""
		query = db.session.query(Voter)
		for key, value in kwargs.items():
			if key in props:
				if isinstance(getattr(sampleVoter, key), str):
					query = query.filter(getattr(Voter, key) == value.upper())
				else:
					query = query.filter(getattr(Voter, key) == value)

		return query.limit(VOTER_LIMIT).all()

	def resolve_voting_records(self, info, **kwargs):
		"""Allows filtering by any of the History class's attributes"""
		query = db.session.query(History)
		for key, value in kwargs.items():
			if key in histProps:
				if isinstance(getattr(sampleHistory, key), str):
					query = query.filter(getattr(History, key) == value.upper())
				else:
					query = query.filter(getattr(History, key) == value)
		return query.limit(HISTORY_LIMIT).all()


schema = graphene.Schema(query=Query)

app.add_url_rule(
	'/graphql',
	view_func=GraphQLView.as_view(
		'graphql',
		schema=schema,
		graphiql=True  # for having the GraphiQL interface
	)
)


@app.route("/")
def index():
	return redirect("/graphql")


def handle_error(items):
	"""Handles an error in bulk insertion by individually inserting records
	 and skipping the one causing the issue"""
	print("Handling Error")
	for item in items:
		db.session.add(item)
		try:
			db.session.commit()
		except IntegrityError:
			# print("Integrity Error", item, item.voter_reg_num)
			db.session.rollback()
	print("Error Handled")


def load_data():
	"""Loads bulk data from tab delineated text files voters.txt and history.txt"""
	with app.app_context():
		print("Loading voters...")
		i = 0

		voters = []
		with open("voters.txt", "r") as f:
			f.readline()  # discard header
			line = f.readline()
			while line is not None or line != "":
				try:
					voter = Voter(line)
				except IndexError:
					break
				voters.append(voter)
				print("\rProcessing voter {}".format(i), end=" ")
				if i % 50000 == 0:
					try:
						db.session.bulk_save_objects(voters)
						db.session.commit()
					except IntegrityError:
						print("Integrity Error", voter, voter.voter_reg_num)
						db.session.rollback()
						handle_error(voters)
					voters = []

				i += 1
				line = f.readline()
		db.session.bulk_save_objects(voters)
		db.session.commit()
		voters = []

		i = 0

		print("Loading voter records...")

		records = []
		with open("history.txt", "r") as f:
			f.readline()  # discard header
			line = f.readline()

			while line is not None or line != "":
				try:
					history = History(line)
				except IndexError:
					break
				# db.session.add(history)
				i += 1
				records.append(history)
				print("\rProcessing voter record {}".format(i), end=" ")

				if i % 100000 == 0:
					try:
						db.session.bulk_save_objects(records)
						db.session.commit()
					except IntegrityError:
						print("Integrity Error", history, history.voter_reg_num)
						db.session.rollback()
						handle_error(records)
					records = []
				line = f.readline()
		db.session.commit()


with app.app_context():
	# Automatically load data if database is empty
	if db.session.query(Voter).first() is None:
		load_data()

if __name__ == '__main__':
	app.run(debug=True, host='127.0.0.1')
