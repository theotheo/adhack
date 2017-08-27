from jinja2 import Environment, FileSystemLoader
import pandas as pd

import os
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template("template.html")
db = pd.read_csv('data/profiles.csv').set_index('uid')


def choose_recommendations(uid, kind):
    fn = 'data/{}.json'.format(uid)
    if os.path.isfile(fn):
        df = pd.read_json(fn)

    else:
        df = pd.read_excel('data/igoods/sales.xls')
        if kind == 'empty':
            df = pd.read_excel('data/igoods/sales.xls')
        elif kind == 'male':
            df = pd.read_excel('data/igoods/sales.xls')
            df['kind'] = 'mars'
            # df = df[df['gender'] != 'female']
        elif kind == 'female':
            df = pd.read_excel('data/igoods/sales.xls')
            df['kind'] = 'venus'
            # df = df[df['gender'] != 'male']
        elif kind == 'with_children':
            pass
        elif kind == 'familiar':
            df['kind'] = None
            df['kind'][:3] = 'bolt'
            df['kind'][3:6] = 'vk'
            df['kind'][9:] = 'vk'
        elif kind == 'friend':
            df = pd.read_excel('data/igoods/personal.xls')
            df['kind'] = None
            df['kind'][:3] = 'bolt'
            df['kind'][3:6] = 'heart'
            df['kind'][9:] = 'heart'
        elif kind == 'friends':
            df = pd.read_excel('data/igoods/personal.xls')
            df['kind'] = None
            df['kind'][:3] = 'heart'
            df['kind'][3:6] = 'bolt'
            df['kind'][9:] = 'bolt'

        df = df.sample(12)
        
    return df

def create_html(uid, kind):
    
    top = choose_recommendations(uid, kind)
    fn = 'data/{}.json'.format(uid)
    top.to_json(fn)
    # top = top.sample(12)
    html = template.render({'x': top})
    with open('static/MDB-Free/recommendations.html', 'w') as f:
        f.write(html)