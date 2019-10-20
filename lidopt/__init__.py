import yaml

with open("config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

exp = config['experiment']
sim = config['simulation']