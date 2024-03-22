# Import things that are needed generically
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool, tool
from typing import Optional, Type, List
from pydantic import BaseModel, Field
from netmiko import ConnectHandler

llm = ChatOpenAI(temperature=0)


class ConfigCommandsInput(BaseModel):
    hostname: str = Field(..., description="The hostname as a FQDN or IP Address.")
    username: str = Field(..., description="The username to login in the remote host.")
    password: str = Field(..., description="The password to login in the remote host.")
    commands: List[str] = Field(..., description="A list of commands to execute on the remote host.")
    port: Optional[int] = Field(22, description="An optional port number, defaults to 22.")

@tool
def config_commands(hostname: str, username: str, password: str, commands, port: int=22) -> str:
    """Tool to ssh into a remote host and execute commands."""
    net_connect = ConnectHandler(device_type='cisco_ios', host=hostname, username=username, password=password, port=port)
    output = ''
    try:
        for command in commands:
            output += net_connect.send_command_timing(
                command, strip_prompt=False, strip_command=False, delay_factor=4
                )
    except Exception as e:
        output += e
    finally:
        net_connect.disconnect()

    return output

# agent = initialize_agent([config_commands], llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

tools = [
    Tool(
        name = "SSHClient",
        func=config_commands,
        description="useful for when you need to connect to a remote device to execute commands."
    )
]

agent = initialize_agent(tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

output = agent.run(
    """Login in the switch 192.168.1.222 username is admin and password is Cisco123 and
    delete all the vlans with name starting with AIBot. After you complete this task, I
    want you to write me summary of any lessons you learned from this task.'
    If you encounter this error 'Failed to connect to 192.168.1.222:22 due to' tell me why you think it happened.
    """)

print(output)
