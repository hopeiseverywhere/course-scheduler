from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import time
from typing import List, Union
import multiprocessing as mp
from threading import Thread

import codecs
import os
import tempfile
from local_output.HtmlOutput import HtmlOutput

from algorithm.GeneticAlgorithm import GeneticAlgorithm
from model.Configuration import Configuration
from api.Api_Output import get_result
from api.Data_Model import Section, Room
from model import Constant

description = """
Course Schedular
"""

app = FastAPI(title="Course Schedular API",
              description=description,
              version="5.0",
              debug=True)

json_data_in_memory = None
configuration = None


class BaseRequest(BaseModel):
    section: Union[Section, None] = None
    room: Union[Room, None] = None


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/data")
async def save_data(data: List[BaseRequest]):
    """Load the data to algorithm

    Args:
        data (List[BaseRequest]): including "section" and "room"

    """
    try:
        global configuration, json_data_in_memory
        saved_data = []
        for item in data:
            if item.section:
                # Save section data
                saved_data.append({"section": item.section.dict()})
            elif item.room:
                # Save room data
                saved_data.append({"room": item.room.dict()})
            else:
                raise HTTPException(
                    status_code=400, detail="Invalid request format.")

        json_data_in_memory = saved_data

        configuration = Configuration()
        configuration.parse_file(json_data_in_memory)
        print(configuration)
        return JSONResponse({"message": "Data saved successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/run/{accuracy}/{timeout}")
async def run_algorithm(accuracy: float = 0.95,
                        timeout: int = 150):
    """
    Run the process using the provided minimum accuracy of the genetic algorithm.

    Args:
        accuracy (float): The minimum accuracy of the algorithm. Defaults to 0.95.
        timeout (int): The maximum time (in seconds) to wait for the algorithm to complete. Defaults to 150 seconds.

    Returns:
        JSONResponse: The result of the process in JSON format.

    Raises:
        HTTPException: If there is an error during the process.
    """
    try:
        global configuration, json_data_in_memory

        if json_data_in_memory is None:
            raise HTTPException(status_code=404,
                                detail="No JSON data available.")
        if configuration is None:
            raise HTTPException(status_code=404,
                                detail="No config data available.")
        # Check accuracy and timeout ranges
        if not (0.2 <= accuracy <= 1):
            raise ValueError("Accuracy must be in the range 0.2 to 1")
        if not (10 <= timeout <= 250):
            raise ValueError("Timeout must be in the range 10 to 250")

        result = local_algorithm(accuracy=accuracy, timeout=timeout)
        return JSONResponse(content=json.loads(result))

    except HTTPException as http_err:
        raise http_err
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.delete("/clear")
async def clear():
    """
    Clears the previous configuration data.

    This endpoint clears any existing configuration data stored in memory.

    Returns:
        JSONResponse: A JSON response indicating the success of the operation.

    Example:
        If successful, returns:
        {"message": "Data cleared successfully"}
    """
    global json_data_in_memory, configuration

    configuration = None
    json_data_in_memory = None

    return JSONResponse({"message": "Data cleared successfully."})


def local_algorithm(accuracy=0.95, timeout=150):
    """Local version of the algorithm"""
    global configuration

    try:
        start_time = int(round(time.time() * 1000))
        # Set up the number of threads (quantity below) to search for an algorithm
        pool_size = min(5, os.cpu_count() - 1)
        pool = []
        manager = mp.Manager()
        result = manager.dict()
        keep_searching = manager.Event()
        keep_searching.set()

        # Create the processes and start them
        for _i in range(pool_size):
            alg = GeneticAlgorithm(configuration)
            # Add timeout to the process
            process = mp.Process(target=alg.run, args=(
                keep_searching, result, 9999, accuracy))
            process.start()
            # Store process and its timeout as a tuple in the pool list
            pool.append((process, time.time() + timeout))

        # Block until a configuration is found or timeout occurs
        for process, end_time in pool:
            # Calculate remaining time
            remaining_time = max(0, end_time - time.time())
            process.join(remaining_time)  # Join with remaining time

        # Save the number of seconds it took to find the result
        seconds = (int(round(time.time() * 1000)) - start_time) / 1000.0
        # print(f"Seconds: {seconds}")

        # Check if the algorithm exceeded the timeout
        if seconds > timeout:
            raise TimeoutError(
                f"Algorithm execution exceeded the specified timeout of {timeout} seconds.")
        # Get best result (first solution that satisfies constraints to be found)
        solution = result['solution']

        # Check that solution found
        if solution is None:
            raise ValueError(
                "No solution found within the specified timeout of {timeout} seconds.")

        # Visualize Test
        # html_result = HtmlOutput.getResult(best.result)
        # file_name = "temp.json"
        # temp_file_path = tempfile.gettempdir() + file_name.replace(".json", ".htm")
        # writer = codecs.open(temp_file_path, "w", "utf-8")
        # writer.write(html_result)
        # writer.close()
        # os.system("open " + temp_file_path)

        print(f"\nCompleted in {seconds} secs.\n")
        # Assuming get_result is defined elsewhere
        result = get_result(solution.result)
        return result
    except TimeoutError as e:
        # Raise a custom HTTPException with 500 status code and detailed message
        raise HTTPException(
            status_code=500, detail=str(e)) from e

    except ValueError as e:
        # Raise a custom HTTPException with 500 status code and detailed message
        raise HTTPException(
            status_code=500, detail=str(e)) from e

    except Exception as e:
        # Check general exceptions
        print("An error occurred:", e)
