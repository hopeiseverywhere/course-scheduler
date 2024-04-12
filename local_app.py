import codecs
import os
import tempfile
import time

from model.Configuration import Configuration
from algorithm.GeneticAlgorithm import GeneticAlgorithm
from api.Api_Output import get_result
from local_output.HtmlOutput import HtmlOutput
from io_data.input.testData import data
import multiprocessing as mp

def local_app():
    """Local version starter
    """
    start_time = int(round(time.time() * 1000))

    # Set up the number of threads (quantity below) to search for an algorithm
    pool_size = min(5, os.cpu_count() - 1)
    print("Pool size: {}".format(pool_size))
    pool = []
    manager = mp.Manager()
    result = manager.dict()
    keep_searching = manager.Event()
    keep_searching.set()

    # Create the processes and start them
    for i in range(pool_size):
        configuration = Configuration()
        configuration.parse_file(data)
        alg = GeneticAlgorithm(configuration)
        pool.append(mp.Process(target=alg.run, args=(keep_searching, result, 9999, 0.999)))
        pool[i].start()
    print("Threads created {}".format((int(round(time.time() * 1000)) - start_time) / 1000.0))

    # Block until a configuration is found
    for process in pool:
        process.join()

    # Get best result (first solution that satisfies constraints to be found)
    solution = result['solution']

    # Save the number of seconds it took to find the result and let child threads terminate gracefully
    seconds = (int(round(time.time() * 1000)) - start_time) / 1000.0

    # Check that solution found
    if solution is None:
        print("Solution timed out")
        return -1

    # save json version of result
    get_result(solution.result)
    print("Iterations: {}".format(solution.current_generation))

    # time table visualization
    html_result = HtmlOutput.getResult(solution.result)
    file_name = "temp.json"
    temp_file_path = tempfile.gettempdir() + file_name.replace(".json", ".htm")
    writer = codecs.open(temp_file_path, "w", "utf-8")
    writer.write(html_result)
    writer.close()
    os.system("start " + temp_file_path)

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
