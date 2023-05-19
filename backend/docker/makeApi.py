import os
from flask import Flask, request, make_response, send_from_directory, jsonify
import csv
from collections import defaultdict
from pypdf import PdfReader, PdfWriter


def setup_files(fn):
    # TODO: account for multiple pages
    reader = PdfReader(fn)
    writer = PdfWriter()
    page = reader.pages[0]
    fields = reader.get_form_text_fields()
    writer.add_page(page)
    return reader, writer, page, fields

def get_manifest_data(csv_reader):
    manifest_data = defaultdict(list)
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            pass
        else:
            manifest_data["LINE"].append(row[0])
            manifest_data["NAME"].append(row[1])
            manifest_data["GRADE"].append(row[2])
            manifest_data["ORGANIZATION"].append(row[3])
            manifest_data["TYPE_OF_JUMP"].append(row[4])
            manifest_data["TYPE_OF_AIRCRAFT"].append(row[5])
            manifest_data["DATE_OF_JUMP"].append(row[6])
            manifest_data["LOCATION_OF_JUMP"].append(row[7])
            manifest_data["CHALK"].append(row[8])
        line_count += 1
    return manifest_data

def update_pdf(writer, fields, manifest_data):
    # TODO: need to integrate the officer field from the real CSV
    for i in range(len(manifest_data["LINE"])):
        if i == 0:
            line_field = "LINE[0]"
            name_field = "NAME_A[0]"
            org_field = "ORG_A[0]"
            grade_field = "GRADE_A[0]"
            type_of_jump_field = "TY_JUMP[0]"
            type_of_aircraft_field = "AIRCRAFT[0]"
            date_of_jump_field = "DATE[0]"
            location_field = "LOCATION[0]"
            # officer_field = "OFFICER[0]"
            writer.update_page_form_field_values(writer.pages[0], {f"{line_field}": manifest_data["LINE"][i]})
            writer.update_page_form_field_values(writer.pages[0], {f"{name_field}": manifest_data["NAME"][i]})
            writer.update_page_form_field_values(writer.pages[0], {f"{org_field}": manifest_data["ORGANIZATION"][i]})
            writer.update_page_form_field_values(writer.pages[0], {f"{grade_field}": manifest_data["GRADE"][i]})
            writer.update_page_form_field_values(
                writer.pages[0], {f"{type_of_jump_field}": manifest_data["TYPE_OF_JUMP"][i]}
            )
            writer.update_page_form_field_values(
                writer.pages[0],
                {
                    f"{type_of_aircraft_field}": manifest_data["TYPE_OF_AIRCRAFT"][i]
                    + " (CHALK NUMBER "
                    + manifest_data["CHALK"][i]
                    + ")"
                },
            )
            writer.update_page_form_field_values(
                writer.pages[0], {f"{date_of_jump_field}": manifest_data["DATE_OF_JUMP"][i]}
            )
            writer.update_page_form_field_values(
                writer.pages[0], {f"{location_field}": manifest_data["LOCATION_OF_JUMP"][i]}
            )

        else:
            line_field = f"LINE_{i}[0]"
            name_field = f"NAME_A_{i}[0]"
            org_field = f"ORG_A_{i}[0]"
            grade_field = f"GRADE_A_{i}[0]"
            type_of_jump_field = f"TY_JUMP_{i}[0]"

            writer.update_page_form_field_values(writer.pages[0], {f"{line_field}": manifest_data["LINE"][i]})
            writer.update_page_form_field_values(writer.pages[0], {f"{name_field}": manifest_data["NAME"][i]})
            writer.update_page_form_field_values(writer.pages[0], {f"{org_field}": manifest_data["ORGANIZATION"][i]})
            writer.update_page_form_field_values(writer.pages[0], {f"{grade_field}": manifest_data["GRADE"][i]})
            writer.update_page_form_field_values(
                writer.pages[0], {f"{type_of_jump_field}": manifest_data["TYPE_OF_JUMP"][i]}
            )

    return writer

def write_pdf(writer):
    # TODO: organize the output to save to the right location
    with open("tmp/manifest.pdf", "wb") as output_stream:
        writer.write(output_stream)

app = Flask(__name__)

@app.route('/index', methods=['GET'])
def index():
    return 'Welcome'

@app.route('/processfile', methods=['POST'])
def processfile():
    content_type = request.headers.get('Content-Type')

    if 'multipart/form-data' in content_type:
        file = request.files['file']
        log_name = file.filename
        file.save(os.path.join("tmp", "manifest.csv"))

    else:
        return make_response({'message': f'Unsupported content type: {content_type}'}, 400)
    
    try:
        with open("tmp/manifest.csv") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            manifest_data = get_manifest_data(csv_reader)
        fn_form = "blank_form_ARN8626_A1306 FINAL.pdf"
        reader, writer, page, fields = setup_files(fn_form)
        writer = update_pdf(writer, fields, manifest_data)
        write_pdf(writer)
    
    except:
        return make_response({'message': 'Failed to process CSV'}, 500)

    return make_response({'message': 'Successfully processed CSV'}, 200)

@app.route("/files")
def list_files():
    """Endpoint to list files on the server."""
    files = []
    for filename in os.listdir("tmp"):
        path = os.path.join("tmp", filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify(files)

@app.route("/files/<path:path>")
def get_file(path):
    """Download a file."""
    return send_from_directory("tmp", "manifest.pdf", as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)