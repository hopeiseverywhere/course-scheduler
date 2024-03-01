import codecs
import pathlib
import os
import sys
import tempfile
import time
import traceback


from model.Configuration import Configuration
from algorithm.GeneticAlgorithm import GeneticAlgorithm
from Output import get_result
from HtmlOutput import HtmlOutput


def main():
    start_time = int(round(time.time() * 1000))
    configuration = Configuration()

    # Replace 'your_config_file.json' with the actual path to your JSON file
    file_name = 'input3.json'
    configuration.parse_file(file_name)
    # # for prof in configuration._rooms.values():
    # #     print(prof)
    # # for sec in configuration._sections:
    # #     print(sec)
    # # print("------- finished testing")
    #
    alg = GeneticAlgorithm(configuration)
    alg.run(9999, 0.95)
    # # also for testing
    get_result(alg.result)


    html_result = HtmlOutput.getResult(alg.result)

    temp_file_path = tempfile.gettempdir() + file_name.replace(".json", ".htm")
    writer = codecs.open(temp_file_path, "w", "utf-8")
    writer.write(html_result)
    writer.close()
    # #
    seconds = (int(round(time.time() * 1000)) - start_time) / 1000.0
    print("\nCompleted in {} secs.\n".format(seconds))
    os.system("open " + temp_file_path)


if __name__ == '__main__':
    main()
