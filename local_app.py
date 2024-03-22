import codecs
import os
import tempfile
import time


from model.Configuration import Configuration
from algorithm.GeneticAlgorithm import GeneticAlgorithm
from api.Output import get_result
from output.HtmlOutput import HtmlOutput
from io_data.testData import data


def local_app():
    start_time = int(round(time.time() * 1000))
    configuration = Configuration()

    file_name = "input.json"
    configuration.parse_file(data)

    alg = GeneticAlgorithm(configuration)
    alg.run(9999, 0.98)

    get_result(alg.result)

    html_result = HtmlOutput.getResult(alg.result)

    temp_file_path = tempfile.gettempdir() + file_name.replace(".json", ".htm")
    writer = codecs.open(temp_file_path, "w", "utf-8")
    writer.write(html_result)
    writer.close()

    seconds = (int(round(time.time() * 1000)) - start_time) / 1000.0
    print("\nCompleted in {} secs.\n".format(seconds))
    os.system("open " + temp_file_path)

    # configuration.print_lab_section_dict()


if __name__ == '__main__':
    local_app()
