from flask import Flask
from graphene import Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
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
	props = [a for a in dir(Voter) if not a.startswith('_') and not callable(getattr(Voter, a))]
	histProps = [a for a in dir(History) if not a.startswith('_') and not callable(getattr(History, a))]


class Query(graphene.ObjectType):
	node = graphene.relay.Node.Field()
	voters = SQLAlchemyConnectionField(VoterObject, **filterParams)
	voting_records = SQLAlchemyConnectionField(VoterHistoryObject, **recordsParams)

	def resolve_voters(self, info, **kwargs):
		query = db.session.query(Voter)
		for property in props:
			if property in kwargs:
				query = query.filter(getattr(Voter, property) == kwargs[property].upper())
		return query.all()

	def resolve_voting_records(self, info, **kwargs):
		query = db.session.query(History)
		for property in histProps:
			if property in kwargs:
				query = query.filter(getattr(History, property) == kwargs[property].upper())
		return query.all()


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
				#db.session.add(history)
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


if __name__ == '__main__':
	with app.app_context():
		if db.session.query(Voter).first() is None:
			load_data()
	app.run(debug=True, host='127.0.0.1')
