import json


def getJson():
    with open('data.json') as f:
        file=json.load(f)
        value=file['bank_name']
        loan_types=list(value['iob']['loan'].keys())
        loan_fields=list(value['iob']['loan']['personal_loan'].keys())
        sample=value['iob']['loan'][loan_types[0]][loan_fields[0]]
        print(loan_types)
        print(loan_fields)
        print(sample)
        # print(dict(indiv_loan))

getJson()