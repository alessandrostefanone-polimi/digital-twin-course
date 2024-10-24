from asyncua import Client
import pandas as pd
import logging
import asyncio

_logger = logging.getLogger(__name__)

# Define a function to loop the values list
async def thread_function(values, var_server):
    while True:
        try:
            value = float(values.pop(0))
        except:
            value = str(values.pop(0))
        await var_server.write_value(value)
        _logger.info(f"Value {var_server}: {value}")
        values.append(value)

# define function to extract values from Excel file
def excel_to_list(Controller):
    filename = "./FridgeData.xlsx"

    # try to read file as Excel file, otherwise as a *.csv file
    try:
        workbook = pd.read_excel(filename)
    except:
        workbook = pd.read_csv(filename)

    # Extract values from Excel file

    inTemp_values = workbook.iloc[:,1].values.tolist()
    inHumid_values = workbook.iloc[:,3].values.tolist()
    outTemp_values = workbook.iloc[:,5].values.tolist()
    outHumid_values = workbook.iloc[:,7].values.tolist()
    doorStatus_values = workbook.iloc[:,8].values.tolist()
    powerStatus_values = workbook.iloc[:,9].values.tolist()

    # Instantiate controller object

    controller = Controller(inTemp_values, inHumid_values, outTemp_values, outHumid_values, doorStatus_values, powerStatus_values)

    return controller

url = "opc.tcp://127.0.0.1:3005/"
namespace = "http://examples.factory.github.io"

async def main():
    print(f"Connecting to {url} ...")
    async with Client(url=url) as client:
        nsidx = await client.get_namespace_index(namespace)
        print(f"Namespace Index for '{namespace}': {nsidx}")
        print(await client.nodes.root.get_children())

        class Controller:
            def __init__(self, inTemp, inHumid, outTemp, outHumid, doorStatus, powerStatus):
                self.inTemp = inTemp
                self.inHumid = inHumid
                self.outTemp = outTemp
                self.outHumid = outHumid
                self.doorStatus = doorStatus
                self.powerStatus = powerStatus

        controller = excel_to_list(Controller)

        objects = await client.nodes.root.get_child("0:Objects")
        fridge = await objects.get_child(f"{nsidx}:Fridge1")

        inTemp = await fridge.get_child(f"{nsidx}:inTemp")
        inHumid = await fridge.get_child(f"{nsidx}:inHumid")
        outTemp = await fridge.get_child(f"{nsidx}:outTemp")
        outHumid = await fridge.get_child(f"{nsidx}:outHumid")
        doorStatus = await fridge.get_child(f"{nsidx}:doorStatus")
        powerStatus = await fridge.get_child(f"{nsidx}:powerStatus")

        inTemp_task = asyncio.ensure_future(thread_function(controller.inTemp, inTemp))
        inHumid_task = asyncio.ensure_future(thread_function(controller.inHumid, inHumid))
        outTemp_task = asyncio.ensure_future(thread_function(controller.outTemp, outTemp))
        outHumid_task = asyncio.ensure_future(thread_function(controller.outHumid, outHumid))
        doorStatus_task = asyncio.ensure_future(thread_function(controller.doorStatus, doorStatus))
        powerStatus_task = asyncio.ensure_future(thread_function(controller.powerStatus, powerStatus))

        tasks = []

        tasks.append(inTemp_task)
        tasks.append(inHumid_task)
        tasks.append(outTemp_task)
        tasks.append(outHumid_task)
        tasks.append(doorStatus_task)
        tasks.append(powerStatus_task)

        # Wait for the completion of all the tasks

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())