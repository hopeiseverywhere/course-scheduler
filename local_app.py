import codecs
import os
import tempfile
import time


from model.Configuration import Configuration
from algorithm.GeneticAlgorithm import GeneticAlgorithm
from api.Api_Output import get_result
from local_output.HtmlOutput import HtmlOutput
from io_data.input.testData import data


def local_app():
    start_time = int(round(time.time() * 1000))
    configuration = Configuration()

    configuration.parse_file(data)

    alg = GeneticAlgorithm(configuration)
    alg.run(9999, 0.999)

    # save json version of result
    get_result(alg.result)

    html_result = HtmlOutput.getResult(alg.result)

    file_name = "temp.json"
    temp_file_path = tempfile.gettempdir() + file_name.replace(".json", ".htm")
    writer = codecs.open(temp_file_path, "w", "utf-8")
    writer.write(html_result)
    writer.close()

    # Save HTML file locally
    io_data_folder = "io_data"
    local_file_path = os.path.join(io_data_folder, "output_html.htm")
    print(local_file_path)
    with open(local_file_path, "w", encoding="utf-8") as local_writer:
        local_writer.write(html_result)


    seconds = (int(round(time.time() * 1000)) - start_time) / 1000.0
    print("\nCompleted in {} secs.\n".format(seconds))
    os.system("open " + temp_file_path)


    # print room mapped to day and time slot table
    # alg.result.configuration.print_room_slot()

    # print final criteria
    # alg.result.print_final_criteria()

if __name__ == '__main__':
    local_app()
