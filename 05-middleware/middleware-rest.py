import logging
from asyncua import Client, Node
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models for the response
class OPCValue(BaseModel):
    node_id: str
    value: Any
    timestamp: datetime
    quality: str

class OPCNodeInfo(BaseModel):
    node_id: str
    browse_name: str
    description: Optional[str] = None

class OPCConnection:
    def __init__(self, url: str):
        self.url = url
        self.client = None
    
    async def connect(self):
        if not self.client:
            self.client = Client(url=self.url)
            await self.client.connect()
            logger.info(f"Connected to OPC UA server: {self.url}")

    async def disconnect(self):
        if self.client:
            await self.client.disconnect()
            self.client = None
            logger.info(f"Disconnected from OPC UA Server")
    
    # Method to get OPC UA Node from Node ID
    async def get_node(self, node_id: str) -> Node:
        if not self.client:
            await self.connect()
        return self.client.get_node(node_id)
    
    # Method to get 0:Objects Node
    async def get_objects_node(self):
        if not self.client:
            await self.connect()
        return self.client.get_objects_node()
    
# Global connection instance
opc_connection = OPCConnection("opc.tcp://localhost:3005")

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await opc_connection.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await opc_connection.disconnect()

@app.get("/")
async def root():
    return {"status": "online", "message": "OPC UA REST Middleware"}