import logging
import asyncio
from asyncua import Server, ua

async def main():
    # Create and initialize OPC UA Server
    server = Server()
    await server.init()
                
    # Configuration of the endpoint of the server
    server.set_endpoint("opc.tcp://0.0.0.0:3005/factory/server")
    server.set_server_name("MyFactory Server")

    # Set security policies
    server.set_security_policy(
        [
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
            ua.SecurityPolicyType.Basic256Sha256_Sign
        ]
    )

    async def powerOn(powerStatus):
        await powerStatus.write_value("PowerON")
        return "PowerON"
    
    async def powerOff(powerStatus):
        await powerStatus.write_value("PowerOff")
        return "PowerOff"

    # Namespace configuration
    uri = "http://examples.factory.github.io"
    idx = await server.register_namespace(uri)

    # Create Fridge Object Type
    fridge = await server.nodes.base_object_type.add_object_type(idx, "FridgeType")

    # Add variables to fridge type

    # Door Status
    doorStatus = await fridge.add_variable(idx, "doorStatus", val="DoorCLOSED", datatype=ua.NodeId(ua.ObjectIds.String))
    await doorStatus.set_modelling_rule(True)
    await doorStatus.set_writable()

    # Power Status
    powerStatus = await fridge.add_variable(idx, "powerStatus", val="PowerON", datatype=ua.NodeId(ua.ObjectIds.String))
    await powerStatus.set_modelling_rule(True)
    await powerStatus.set_writable()

    # Inner Temperature Sensor
    inTemp = await fridge.add_variable(idx, "inTemp", val=0.0, datatype=ua.NodeId(ua.ObjectIds.Float))
    await inTemp.set_modelling_rule(True)
    await inTemp.set_writable()

    # Outer Temperature Sensor
    outTemp = await fridge.add_variable(idx, "outTemp", val=0.0, datatype=ua.NodeId(ua.ObjectIds.Float))
    await outTemp.set_modelling_rule(True)
    await outTemp.set_writable()

    # Inner Humidity Sensor
    inHumid = await fridge.add_variable(idx, "inHumid", val=0.0, datatype=ua.NodeId(ua.ObjectIds.Float))
    await inHumid.set_modelling_rule(True)
    await inHumid.set_writable()

    # Outer Humidity Sensor
    outHumid = await fridge.add_variable(idx, "outHumid", val=1.0, datatype=ua.NodeId(ua.ObjectIds.Float))
    await outHumid.set_modelling_rule(True)
    await outHumid.set_writable()

    # Create Methods

    powerOnFunc = await fridge.add_method(idx, "powerOn", powerOn, None, [ua.VariantType.String])
    await powerOnFunc.set_modelling_rule(True)

    powerOffFunc = await fridge.add_method(idx, "powerOff", powerOff, None, [ua.VariantType.String])
    await powerOffFunc.set_modelling_rule(True)

    # Istantiate Fridge
    fridge1 = await server.nodes.objects.add_object(idx, "Fridge1", fridge)

    async with server:
        print("Server started")
        await asyncio.sleep(999999)

if __name__ == "__main__":
    # Logging configuration
    logging.basicConfig(level=logging.INFO)
    # Run the "main" part of the code in an asynchronous way
    asyncio.run(main())