from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import asyncio
from time import time
from typing import List, Union, Annotated

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
              version="4.0",
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


@app.get("/run/{accuracy}")
async def run_process(accuracy: float = 0.93):
    """
    Run the process using the provided minimum accuracy of the genetic algorithm.

    Args:
        id (float): The minimum accuracy of the algorithm. Defaults to 0.93.

    Returns:
        JSONResponse: The result of the process in JSON format.

    Raises:
        HTTPException: If there is an error during the process.
    """
    global json_data_in_memory, configuration

    try:
        if json_data_in_memory is None:
            raise HTTPException(status_code=404,
                                detail="No JSON data available")

        alg = GeneticAlgorithm(configuration)
        # print(configuration)
        timeout = 300
        try:
            start_time = time()  # Capture start time
            result = await asyncio.wait_for(
                asyncio.to_thread(alg.run, 9999, accuracy, timeout),
                timeout=timeout
            )
            end_time = time()  # Capture end time
            elapsed_time = end_time - start_time  # Calculate elapsed time
            print("\nCompleted in {:.2f} seconds.".format(elapsed_time))
            print("Algorithm run completed successfully.\n")
        except asyncio.TimeoutError:
            raise HTTPException(status_code=500,
                                detail="Timeout exceeded while running the algorithm")
        except asyncio.CancelledError:
            # Handle cancellation of the request
            alg.cleanup()  # Clean up resources
            raise HTTPException(
                status_code=499, detail="Request canceled by client")

        solution = get_result(alg.result)
        alg.cleanup()

        return JSONResponse(content=json.loads(solution))
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

    configuration.clear_data()
    json_data_in_memory = None

    return JSONResponse({"message": "Data cleared successfully"})
