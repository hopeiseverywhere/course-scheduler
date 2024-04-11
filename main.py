from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import asyncio
import time
from typing import List, Union
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
                    status_code=400, detail="Invalid request format")

        json_data_in_memory = saved_data

        configuration = Configuration()
        configuration.parse_file(json_data_in_memory)
        print(configuration)
        return JSONResponse({"message": "Data saved successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
                                detail="No JSON data available")
        if configuration is None:
            raise HTTPException(status_code=404,
                                detail="No config data available")

        result = local_algorithm(accuracy=accuracy, timeout=timeout)
        
        return JSONResponse(content=json.loads(result))
    except HTTPException as http_err:
        raise http_err
    except ValueError:
        raise HTTPException(status_code=400, detail="Accuracy and timeout parameters are required and must be valid.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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

    return JSONResponse({"message": "Data cleared successfully"})


def local_algorithm(accuracy=0.95, timeout=100):
    """Local version of the algorithm"""
    global configuration

    try:
        start_time = int(round(time.time() * 1000))
        pool_size = os.cpu_count() - 1  # minus one for main (parent) thread
        thread_list = []
        for i in range(pool_size):
            alg = GeneticAlgorithm(configuration)
            thread_list.append(
                (Thread(target=alg.run, args=(9999, accuracy,)), alg))
            thread_list[i][0].start()

        # Block until a configuration is found or timeout is reached
        best = None
        configuration_found = False
        elapsed_time = 0
        while not configuration_found and elapsed_time < timeout:
            for thread in thread_list:
                if thread[1].solution_found:
                    best = thread[1]
                    configuration_found = True
                    break  # Exit the loop if a solution is found
            time.sleep(1)  # Check every second
            elapsed_time = (int(round(time.time() * 1000)) -
                            start_time) / 1000.0

        # Check if timeout occurred
        if not configuration_found:
            raise TimeoutError(
                "Algorithm execution exceeded the specified timeout")

        # End all threads gracefully
        for thread in thread_list:
            thread[1].set_solution_found(True)
            thread[0].join()

        seconds = (int(round(time.time() * 1000)) - start_time) / 1000.0

        # visualize test
        # html_result = HtmlOutput.getResult(best.result)
        # file_name = "temp.json"
        # temp_file_path = tempfile.gettempdir() + file_name.replace(".json", ".htm")
        # writer = codecs.open(temp_file_path, "w", "utf-8")
        # writer.write(html_result)
        # writer.close()
        # os.system("open " + temp_file_path)

        print(f"\nCompleted in {seconds} secs.\n")
        # Assuming get_result is defined elsewhere
        result = get_result(best.result)
        return result
    except TimeoutError as e:
        # Raise a custom HTTPException with 500 status code and detailed message
        raise HTTPException(
            status_code=500, detail=f"Algorithm execution exceeded the specified timeout of {timeout} seconds.")

