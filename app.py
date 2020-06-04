from flask import Flask
from graphene import Field
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import redirect

from Database import db
from Models import Voter, History
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from flask_graphql import GraphQLView

app = Flask("VoterLookup")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///voters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "pnC0TZam7xBaN1LckSo8"
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


with app.app_context():
	filterParams = {a: graphene.String() for a in dir(Voter) if not a.startswith('_') and not callable(getattr(Voter, a))}
	recordsParams = {a: graphene.String() for a in dir(History) if not a.startswith('_') and not callable(getattr(History, a))}


class Query(graphene.ObjectType):
	node = graphene.relay.Node.Field()
	voters = SQLAlchemyConnectionField(VoterObject, **filterParams)
	voting_records = SQLAlchemyConnectionField(VoterHistoryObject, **recordsParams)

	'''
	# Change the resolver
	def resolve_voters(self, info, first_name=None, last_name=None, middle_name=None, status_cd=None,
	                   voter_status_desc=None, voter_status_reason_desc=None, name_suffix_lbl=None,
	                   res_street_address=None, res_city_desc=None, zip_code=None, mail_addr1=None,
	                   race_code=None, ethnic_code=None, party_cd=None, **kwargs):
		# The value sent with the search parameter will be in the args variable
		'''
	def resolve_voters(self, info, **kwargs):
		query = db.session.query(Voter)
		#print(vars(Voter))
		props = [a for a in dir(Voter) if not a.startswith('_') and not callable(getattr(Voter, a))]
		#print(props)
		for property in props:
			if property in kwargs:
				query = query.filter(getattr(Voter, property) == kwargs[property].upper())
		'''
		if first_name:
			query = query.filter(Voter.first_name == first_name)
		if middle_name:
			query = query.filter(Voter.middle_name == middle_name)
		if last_name:
			query = query.filter(Voter.last_name == last_name)
		'''
		return query.all()


with app.app_context():
	Query.fields = {a: Field(a) for a in dir(Voter) if not a.startswith('_') and not callable(getattr(Voter, a))}

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
	print("Handling Error")
	for item in items:
		db.session.add(item)
		try:
			db.session.commit()
		except IntegrityError:
			#print("Integrity Error", item, item.voter_reg_num)
			db.session.rollback()
	print("Error Handled")


def load_data():
	with app.app_context():
		print("Loading voters...")
		i = 0
		with open("voters.txt", "r") as f:
			f.readline()  # discard header
			line = f.readline()
			voters = []
			while line is not None or line != "":
				voter = Voter(line)
				voters.append(voter)
				print("Processing voter {}".format(i), end="\r")
				if i % 1000 == 0:
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

		db.session.commit()
		i = 0
		print("Loading voter records...")
		with open("history.txt", "r") as f:
			f.readline()  # discard header
			for line in f.readlines():
				history = History(line)
				db.session.add(history)
				i += 1
				if i % 10000 == 0:
					db.session.commit()
		db.session.commit()


if __name__ == '__main__':
	with app.app_context():
		if len(db.session.query(Voter).all()) == 0:
			load_data()
	app.run(debug=True, host='127.0.0.1')
