from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool, tool
from typing import Optional, Type, List
from pydantic import BaseModel, Field
from netmiko import ConnectHandler

llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.7)


class ConfigCommandsInput(BaseModel):
    hostname: str = Field(..., description='The hostname as a FQDN or IP Address.')
    username: str = Field(..., description='The username to login in the remote host.')
    password: str = Field(..., description='The password to login in the remote host.')
    commands: List[str] = Field(..., description='A list of commands to execute on the remote host.')
    port: Optional[int] = Field(22, description='An optional port number, defaults to 22.')


@tool
def config_commands(hostname: str, username: str, password: str, commands: list, port: int=22) -> str:
    """
    This tool automates the process of SSH-ing into a Cisco network device, entering configuration mode, 
    and executing a series of configuration commands. It is designed specifically for use with Cisco devices 
    and takes care of entering configuration mode as well as saving the configuration changes automatically 
    upon completion. Therefore, users do not need to include commands to enter configuration mode or to save 
    the configuration changes manually.

    The function establishes an SSH connection to the specified Cisco device using the provided hostname (or IP address),
    username, and password. It then iterates over the given list of commands, executing them sequentially on the device.
    After executing all commands, the tool automatically saves the configuration changes to the device before disconnecting.

    It is important to note that this tool is tailored for Cisco devices and may not work as expected with non-Cisco devices.
    Users should ensure that the commands provided are compatible with the Cisco IOS version of the target device.

    Parameters:
        hostname (str): The hostname or IP address of the Cisco device to connect to.
        username (str): The username for authentication on the Cisco device.
        password (str): The password for authentication on the Cisco device.
        commands (list): A list of configuration commands to execute on the Cisco device.
        port (int, optional): The SSH port of the Cisco device. Defaults to 22.

    Returns:
        str: A string containing the concatenated output from each command executed on the Cisco device. 
             In case of an error, the error message will be appended to the output string.

    Example:
        config_commands(hostname='192.168.1.1', username='admin', password='admin123', 
                        commands=['interface GigabitEthernet0/1', 'ip address 192.168.2.1 255.255.255.0'])
    """
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


tools = [
    Tool(
        func=config_commands,
        name = 'config_commands',
        description="""
SSHClient is a specialized tool designed for automating secure command execution on Cisco network devices. It streamlines SSH 
connectivity, automatically enters configuration mode, executes user-specified commands, and saves the changes without 
requiring manual intervention for these steps. Tailored for Cisco devices, it ensures efficient and error-free configuration 
updates, making it ideal for routine network management tasks.""",
        args_schema=ConfigCommandsInput,
        return_direct=True
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
