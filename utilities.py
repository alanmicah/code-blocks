

def write_to_csv(csv_file_path, data_list):
    # Check for existing data in file
    try:
        existing_data_array = import_csv_file(csv_file_path)
    except:
        existing_data_array = []

    list_length = len(data_list)
    if list_length == 1:
        row_or_rows = 'row'
    else:
        row_or_rows = 'rows'
    print(f'> Exporting {list_length} data points')

    first_item = data_list[0]
    if str(type(first_item)) == "<class 'dict'>":
        print(f'> List of dicts')
        headers = list(first_item.keys())
        with open(csv_file_path, 'a+') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            if len(existing_data_array) == 0:
                writer.writeheader()
            for row_dict in data_list:
                writer.writerow(row_dict)
    else:
        with open(csv_file_path, 'a+') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(data_list)
    print(headline(f'Data exported to "{csv_file_path}" with {str(list_length)} {row_or_rows}', '*', 100))


def import_csv_file(csv_file_path):
    try:
        csv_file = open(csv_file_path, 'r')
    except FileNotFoundError:
        return []
    output_array = []

    with csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            first_column = row[0]
            if not first_column == '':
                if first_column[0] != '#':  # Ignore comment lines
                    output_array.append(row)

    return output_array


def store_dict(dict_payload, filename):
    dict_as_str = json.dumps(dict_payload)
    with open(filename, 'w') as file:
        file.write(dict_as_str)
    file.close()

    return 'success'


def retrieve_dict(filepath):
    try:
        with open(filepath, "r") as file:
            output_str = ''
            for line in file:
                # print(f'line = {line}')
                # line = line.decode('utf-8','ignore').encode("utf-8")
                output_str = output_str + line
            # print(f'str 1 = {output_str}')

        # print(f'str 2 = {output_str}')
        dict_payload = json.loads(output_str)
    # print(f'dict loaded')
    except:
        dict_payload = {}
    return dict_payload


def headline(text, symbol, width):
    return f" {text} ".center(width, symbol)
