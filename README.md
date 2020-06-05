# VoterLookup
Project to make NC Voter data more accessible via a GraphQL API

## Usage
Either deploy using a WSGI server or run ```app.py```

Data is automatically loaded from two files:
```voters.txt``` should contain a tab-delineated list of voters

```history.txt``` should contain a list of voting records.

## Data
You can get voter data from the [NC State Board of Elections](https://www.ncsbe.gov/Public-Records-Data-Info/Election-Results-Data)

It's recommended to use the statewide [voters](http://dl.ncsbe.gov/data/ncvoter_Statewide.zip) and the [history](http://dl.ncsbe.gov/data/ncvhis_Statewide.zip) files. Be warned: they are both 3+ GB files and may take a while to process. It's recommended to have at least 20GB of free storage space before starting.
