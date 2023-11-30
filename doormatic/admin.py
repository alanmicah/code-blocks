
import utilities

# ================================== SWITCHES ================================== #
object_type = "opportunities"

# =================================== GLOBALS =================================== #
main_directory = "doormatic/"
data_directory = "data/"
data_store_filename = "data_store.json"
processed_object_ids_filename = f"processed_ids_{object_type}.json"
object_note_records_filename = f"note_records_{object_type}_<NUMBER>.json"

objects_csv_filename = f"{object_type}.csv"
notes_filename = f"notes_{object_type}_<NUMBER>.csv"

object_id_column = 1  # Zero indexed
total_objects_processed = 0  # For console logging


def compare_object_lists():
    array_of_objects = utilities.import_csv_file(f'{data_directory}{objects_csv_filename}'
                                                 .replace('<OBJECT_TYPE>', object_type))
    processed_ids_data_store = utilities.retrieve_dict(f'{data_directory}{processed_object_ids_filename}'
                                                       .replace('<OBJECT_TYPE>', object_type))
    list_of_processed_ids = processed_ids_data_store.get('data')
    percent_processed = int(len(list_of_processed_ids) / len(array_of_objects) * 1000) / 10
    print(f'Total {object_type} = {len(array_of_objects)}')
    print(f'Processed {object_type} = {len(list_of_processed_ids)} ({percent_processed}%)')


compare_object_lists()