import codecs
import os
import tempfile
import time

from model.Configuration import Configuration
from algorithm.GeneticAlgorithm import GeneticAlgorithm
from api.Api_Output import get_result
from local_output.HtmlOutput import HtmlOutput
from io_data.input.testData import data
from threading import Thread

def local_app():
    """Local version starter
    """
    start_time = int(round(time.time() * 1000))
    print(start_time)

    # configuration = Configuration()
    # configuration.parse_file(data)
    # best = GeneticAlgorithm(configuration)
    # best.run(9999, 0.975)

    # Set up the number of threads (quantity below) to search for an algorithm
    pool_size = 5
    thread_list = []
    for i in range(pool_size):
        configuration = Configuration()
        configuration.parse_file(data)
        alg = GeneticAlgorithm(configuration)
        thread_list.append((Thread(target=alg.run, args=(9999, 0.999,)), alg))
        thread_list[i][0].start()

    print("Threads created {}".format((int(round(time.time() * 1000)) - start_time) / 1000.0))
        

    # Block until a configuration is found
    best = None
    configuration_found = False
    while not configuration_found:
        # Check if any have finished. If one has, set it to best
        for thread in thread_list:
            if thread[1].solution_found is True:
                best = thread[1]
                configuration_found = True

        # If a configuration was found, end all threads gracefully (set their solution found to true)
        if configuration_found is True:
            for thread in thread_list:
                thread[1].set_solution_found(True)
                thread[0].join()

    # Save the number of seconds it took to find the result and let child threads terminate gracefully
    seconds = (int(round(time.time() * 1000)) - start_time) / 1000.0

    # save json version of result
    get_result(best.result)

    # time table visualization
    html_result = HtmlOutput.getResult(best.result)
    file_name = "temp.json"
    temp_file_path = tempfile.gettempdir() + file_name.replace(".json", ".htm")
    writer = codecs.open(temp_file_path, "w", "utf-8")
    writer.write(html_result)
    writer.close()
    os.system("open " + temp_file_path)

    # Save HTML file locally
    io_data_folder = "io_data"
    local_file_path = os.path.join(io_data_folder, "output_html.htm")
    print(local_file_path)
    with open(local_file_path, "w", encoding="utf-8") as local_writer:
        local_writer.write(html_result)
    print(f"\nCompleted in {seconds} secs.\n")
    

    # print room mapped to day and time slot table
    # best.result.configuration.print_room_slot()

    # print final criteria
    # best.result.print_final_criteria()


if __name__ == '__main__':
    local_app()
