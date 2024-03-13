from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
import json
from fastapi.responses import JSONResponse
import asyncio
from time import time
from typing import List, Union
from algorithm.GeneticAlgorithm import GeneticAlgorithm
from model.Configuration import Configuration
from api.Output import get_result

description = """
Course Schedular
"""

app = FastAPI(title="Course Schedular API",
              description=description,
              version="0.0.2",
    debug=True)

json_data_in_memory = None
configuration = None


class Section(BaseModel):
    """
    Represents a section.

    Attributes:
        id (int): The unique identifier for the section.
        course (str): The course name associated with the section.
        professor (str): The professor teaching the section.
        pref_time (List[str]): The preferred times for the section, ["morning", "afternoon", "evening"].
        lab (bool | None): Indicates whether the section requires a lab FOR NOW.
        duration (int): The duration of the section in RELATIVE TIME for now.
        students (int): The number of students enrolled in the section.

    Methods:
        validate_positive_integer(cls, value): Validates that the value is a positive integer.
    """
    course: str
    professor: str
    pref_time: List[str]
    is_lab: bool | None
    duration: int
    students: int

    @validator('duration', 'students', pre=True)
    def validate_positive_integer(cls, value):
        """Validate that the value is a positive integer."""
        if value <= 0:
            raise ValueError('Value must be a positive integer')
        return value


class Room(BaseModel):
    """
    Represents a room.

    Attributes:
        name (str): The name or identifier of the room.
        size (int): The capacity or size of the room in terms of seats.

    Methods:
        validate_positive_integer(cls, value): Validates that the value is a positive integer.
    """
    name: str
    size: int

    @validator('size', pre=True)
    def validate_positive_integer(cls, value):
        """Validate that the value is a positive integer."""
        if value <= 0:
            raise ValueError('Value must be a positive integer')
        return value


class BaseRequest(BaseModel):
    section: Union[Section, None] = None
    room: Union[Room, None] = None


@app.get("/")
async def root():

    return {"message": "Hello World"}


@app.post("/data")
async def save_data(data: List[BaseRequest]):
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
        # print(saved_data)

        json_data_in_memory = saved_data

        configuration = Configuration()
        configuration.parse_file(json_data_in_memory)
        print(configuration)
        return JSONResponse({"message": "Data saved successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/run/{id}")
async def run_process(id: float = 0.93):
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
        timeout = 60
        try:
            start_time = time()  # Capture start time
            result = await asyncio.wait_for(
                asyncio.to_thread(alg.run, 9999, id, timeout),
                timeout=timeout
            )
            end_time = time()  # Capture end time
            elapsed_time = end_time - start_time  # Calculate elapsed time
            print("\nCompleted in {:.2f} seconds.".format(elapsed_time))
            print("Algorithm run completed successfully.\n")
        except asyncio.TimeoutError:
            raise HTTPException(status_code=500,
                                detail="Timeout exceeded while running the algorithm")

        solution = get_result(alg.result)
        alg.cleanup()

        return JSONResponse(content=json.loads(solution))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/clear")
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
