from flask import Flask, request, render_template, send_file
from pypdf import PdfReader, PdfWriter
from collections import defaultdict
import csv
import os


def create_write_page(fn):
    reader = PdfReader(fn)
    writer = PdfWriter()
    page = reader.pages[0]
    writer.add_page(page)
    return writer


def create_pages(fn, num):
    # TODO: account for multiple pages
    reader = PdfReader(fn)
    writer = PdfWriter()
    page = reader.pages[0]
    fields = reader.get_form_text_fields()
    for i in range(num):
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
    page_num = 0
    j = 0
    for i in range(len(manifest_data["LINE"])):
        if j == 0:
            line_field = "LINE[0]"
            name_field = "NAME_A[0]"
            org_field = "ORG_A[0]"
            grade_field = "GRADE_A[0]"
            type_of_jump_field = "TY_JUMP[0]"
            type_of_aircraft_field = "AIRCRAFT[0]"
            date_of_jump_field = "DATE[0]"
            location_field = "LOCATION[0]"
            # officer_field = "OFFICER[0]"
            writer.update_page_form_field_values(writer.pages[page_num], {f"{line_field}": manifest_data["LINE"][i]})
            writer.update_page_form_field_values(writer.pages[page_num], {f"{name_field}": manifest_data["NAME"][i]})
            writer.update_page_form_field_values(
                writer.pages[page_num], {f"{org_field}": manifest_data["ORGANIZATION"][i]}
            )
            writer.update_page_form_field_values(writer.pages[page_num], {f"{grade_field}": manifest_data["GRADE"][i]})
            writer.update_page_form_field_values(
                writer.pages[page_num], {f"{type_of_jump_field}": manifest_data["TYPE_OF_JUMP"][i]}
            )
            writer.update_page_form_field_values(
                writer.pages[page_num],
                {
                    f"{type_of_aircraft_field}": manifest_data["TYPE_OF_AIRCRAFT"][i]
                    + " (CHALK NUMBER "
                    + manifest_data["CHALK"][i]
                    + ")"
                },
            )
            writer.update_page_form_field_values(
                writer.pages[page_num], {f"{date_of_jump_field}": manifest_data["DATE_OF_JUMP"][i]}
            )
            writer.update_page_form_field_values(
                writer.pages[page_num], {f"{location_field}": manifest_data["LOCATION_OF_JUMP"][i]}
            )
            j += 1
        elif (j % 20) == 0:
            print(f"Page Number: {page_num}")
            write_pdf(writer, page_num)
            page_num += 1
            j = 0
        else:
            line_field = f"LINE_{j}[0]"
            name_field = f"NAME_A_{j}[0]"
            org_field = f"ORG_A_{j}[0]"
            grade_field = f"GRADE_A_{j}[0]"
            type_of_jump_field = f"TY_JUMP_{j}[0]"

            writer.update_page_form_field_values(writer.pages[page_num], {f"{line_field}": manifest_data["LINE"][i]})
            writer.update_page_form_field_values(writer.pages[page_num], {f"{name_field}": manifest_data["NAME"][i]})
            writer.update_page_form_field_values(
                writer.pages[page_num], {f"{org_field}": manifest_data["ORGANIZATION"][i]}
            )
            writer.update_page_form_field_values(writer.pages[page_num], {f"{grade_field}": manifest_data["GRADE"][i]})
            writer.update_page_form_field_values(
                writer.pages[page_num], {f"{type_of_jump_field}": manifest_data["TYPE_OF_JUMP"][i]}
            )
            j += 1
    if page_num == 0:
        write_pdf(writer, page_num)
    return writer


def write_pdf(writer, page_num):
    # TODO: organize the output to save to the right location
    with open(f"filled-out_{page_num}.pdf", "wb") as output_stream:
        writer.write(output_stream)


def collect_pdfs():
    pdfs = [i for i in os.listdir() if i.startswith("filled-out")]
    pdfs = sorted(pdfs)
    for pdf in pdfs:
        reader = PdfReader(pdf)
        page = reader.pages[0]
        writer = PdfWriter()
        writer.add_page(page)
    with open("filled-out.pdf", "wb") as output_stream:
        writer.write(output_stream)


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        # TODO: figure out file naming conventions
        csv_reader = csv.reader(request.files.get("file").read().decode("utf8").splitlines())
        manifest_data = get_manifest_data(csv_reader)
        print(f"Length of manifest data: {len(manifest_data['LINE'])}")
        num = int(len(manifest_data["LINE"]) / 20)
        if num == 0:
            num = 1
        fn_form = "blank_form_ARN8626_A1306 FINAL.pdf"
        reader, writer, page, fields = create_pages(fn_form, num)
        writer = update_pdf(writer, fields, manifest_data)
        collect_pdfs()
        return send_file("filled-out.pdf", as_attachment=True)
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
