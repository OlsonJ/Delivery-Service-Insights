import json, csv, os

file_path = r'G:\...\data'
json_file = os.path.join(file_path, 'activities.json')
csv_file = os.path.join(file_path, 'activities.csv')

with open(json_file, 'r') as f:
    data = json.load(f)

def flatten(obj, parent_key='', sep='_'):
    items = {}
    for k, v in obj.items():
        new_key = f'{parent_key}{sep}{k}' if parent_key else k
        if isinstance(v, dict):
            items.update(flatten(v, new_key, sep))
        else:
            items[new_key] = v
    return items

flat_data = [flatten(row) for row in data]
all_keys = list(dict.fromkeys(k for row in flat_data for k in row))

with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=all_keys)
    writer.writeheader()
    writer.writerows(flat_data)

print(f'Done: {len(flat_data)} rows, {len(all_keys)} columns -> {csv_file}')

