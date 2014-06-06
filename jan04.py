
import numpy as np
import pandas as pd
import json
from princetonian import Princetonian


workbook = 'WorkshopRegistrationJan2014.xlsx'
df = pd.read_excel(workbook, 'Sheet1')

# workshop
ws = (23 * ['pandas'] + [np.NaN, np.NaN] +
    20 * ['python'] + [np.NaN, np.NaN] +
    19 * ['unix'])
df['workshop'] = ws

df.dropna(subset=['workshop'], inplace=True)

# netid
df['netid'] = df.iloc[:,2].str.split('@').apply(lambda x: x[0])
df = df.loc[:,['workshop', 'netid']].drop_duplicates()

df.reset_index(drop=True, inplace=True)

# manual fix
df.loc[df['netid'] == 'tdm', 'netid'] = 'tmorton'
df.loc[df['netid'] == 'elizabeth.sully', 'netid'] = 'esully'

# people
people = pd.DataFrame(df['netid'].drop_duplicates())

try:
    princetonian = pd.read_json('princetonian.json')
except:
    pu = [[Princetonian(netid).__dict__] for netid in people['netid']]
    princetonian = pd.DataFrame(pu)[0].apply(pd.Series)
    princetonian.to_json('princetonian.json')

people = pd.merge(people, princetonian)

# workshop nodes
wnode = '{id: %d, type: "workshop", topic: "%s"}'
topics = ['pandas', 'python', 'unix']
nodes = [wnode % (idx, topic) for idx, topic in enumerate(topics)]

# person nodes
people = people.sort('netid').reset_index(drop=True)
people['nodeid'] = pd.Series(range(len(people))) + len(nodes)

people['firstname'].fillna('Unknown', inplace=True)

smap = {'student': 'student', 'faculty/staff': 'staff'}
people['status'] = people['status'].map(lambda x: smap.get(x, 'other'))

dmap = {'Sociology': 'soc', 'Politics': 'pol', 'Population Research': 'pop'}
people['department'] = people['department'].map(lambda x: dmap.get(x, 'other'))

pnode = '{id: %d, type: "attendee", name: "%s", status: "%s", department: "%s"}'

def make_pnode(g):
    fn = g['firstname'].values[0]
    st = g['status'].values[0]
    dp = g['department'].values[0]
    return pnode % (g['nodeid'], fn, st, dp)

nodes += people.groupby('netid').apply(make_pnode).tolist()

# department nodes
dnode = '{id: %d, type: "department", name: "%s"}'
start = len(nodes)
ids = range(start, start + 3)
depts = ['pop', 'soc', 'pol']
dnodes = [dnode % (id, name) for id, name in zip(ids, depts)]

nodes = '[' + ',\n'.join(nodes + dnodes) + ']\n'


# edges
pw = pd.merge(df, people, on='netid')
wmap = {topic:idx for idx, topic in enumerate(topics)}
pw['wnodeid'] = pw['workshop'].map(wmap)

edge = '{source: %d, target: %d, type: "%s"}'

def make_edges(g):
    return edge % (g['nodeid'].values[0], g['wnodeid'].values[0],
        'attends')

edges = pw.groupby(['netid','workshop']).apply(make_edges).tolist()

# add edges within the same department

def do_dept(g):
    dept = g['department'].values[0]
    if  dept == 'other': return []
    dnodeid = {d: id for id, d in zip(ids, depts)}
    nodeids = g['nodeid'].drop_duplicates().tolist()
    return [edge % (dnodeid[dept], el, 'belongs') for el in nodeids]

gedges = sum(pw.groupby('department').apply(do_dept).tolist(), [])

edges = '[' + ',\n'.join(edges + gedges) + ']\n'


# html
with open('jan04.tmp', 'r') as fin, open('jan04.html', 'w') as fout:
    html = fin.read() % (str(nodes), str(edges))
    fout.write(html)
