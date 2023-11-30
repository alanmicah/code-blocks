
import utilities
import html2text

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
test_note_string = '''const originalString = `
<span style="font-family:Arial; font-size: 13px;">1 x Novoferm Steel Made to Measure Georgian up &amp; over Retractable Garage Door finished in White  1 2638.00 25% Sales 20% (VAT on Income) 1978.50<br />
1 1 x Steel Frame finished in White 1 270.00 25% Sales 20% (VAT on Income) 202.50<br />
4 UPVC finishing trim in white 1 75.00 Sales - UPVC 20% (VAT on Income) 75.00<br />
6 Removal &amp; Disposal of existing garage door 1 30.00 Sales - Disposal 20% (VAT on Income) 30.00<br />
5 Installation 1 330.00 Sales 20% (VAT on Income) £330.00 & <br />
<br />
Total VAT 20.00%523.20<br />
TotalGBP &pound;3,139.20<br />
<br />
Optional Extras for Novoferm 1 x Novomatic 563 motor (c/w 2 remotes &amp; 1 internal wall unit): &pound;429+VAT 1 x Rubber Hump (fitted to the ground where the door will sit, helps prevent water from entering the garage): &pound;149+VAT 1 x Brush strip (prevent and debris from entering under the door): &pound;125+VAT</span>
`;'''
# ================================== END GLOBALS ================================== #


def compare_object_lists():
    array_of_objects = utilities.import_csv_file(f'{data_directory}{objects_csv_filename}')
    processed_ids_data_store = utilities.retrieve_dict(f'{data_directory}{processed_object_ids_filename}')
    list_of_processed_ids = processed_ids_data_store.get('data')
    percent_processed = int(len(list_of_processed_ids) / len(array_of_objects) * 1000) / 10
    print(f'Total {object_type} = {len(array_of_objects)}')
    print(f'Processed {object_type} = {len(list_of_processed_ids)} ({percent_processed}%)')


def reformat_html_to_plain(html_text):
    # Handle some special characters
    # html_text = html_text.replace( / (< ([^ >]+) >) / gi, "");
    updated_text = html_text.replace('&pound;', '{GBP}')
    updated_text = updated_text.replace('&amp;', '{AND}')
    plain_text = html2text.html2text(updated_text)
    # Reinsert specials
    plain_text = plain_text.replace('{GBP}', '£')
    plain_text = plain_text.replace('{AND}', '&')
    print(f'PLAIN:\n"{plain_text}\n\n"from HTML:\n"{html_text}"')


# compare_object_lists()
reformat_html_to_plain(test_note_string)
