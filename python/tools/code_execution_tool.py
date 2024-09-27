import asyncio
from dataclasses import dataclass
import shlex
from python.helpers.tool import Tool, Response
from python.helpers import files
from python.helpers.print_style import PrintStyle
from python.helpers.shell_local import LocalInteractiveSession
from python.helpers.shell_ssh import SSHInteractiveSession
from python.helpers.docker import DockerContainerManager

@dataclass
class State:
    shell: LocalInteractiveSession | SSHInteractiveSession
    docker: DockerContainerManager | None

class CodeExecution(Tool):

    def __init__(self, agent, **kwargs):
        super().__init__(agent, **kwargs)
        self.agent = agent  # Properly initialize the agent attribute
        self.state = None
        self.log = None
        self.args = kwargs

    async def execute(self, **kwargs):
        await self.agent.handle_intervention()  # Wait for intervention and handle it, if paused
        await self.prepare_state()

        runtime = self.args.get("runtime", "").lower().strip()
        code = self.args.get("code", "")
        if runtime == "python":
            response = await self.execute_python_code(code)
        elif runtime == "nodejs":
            response = await self.execute_nodejs_code(code)
        elif runtime == "terminal":
            response = await self.execute_terminal_command(code)
        elif runtime == "output":
            response = await self.get_terminal_output(
                wait_with_output=5, wait_without_output=20
            )
        elif runtime == "reset":
            response = await self.reset_terminal()
        else:
            response = self.agent.read_prompt(
                "fw.code_runtime_wrong.md", runtime=runtime
            )

        if not response:
            response = self.agent.read_prompt("fw.code_no_output.md")
        return Response(message=response, break_loop=False)

    async def before_execution(self, **kwargs):
        await self.agent.handle_intervention()  # Wait for intervention and handle it, if paused
        PrintStyle(
            font_color="#1B4F72", padding=True, background_color="white", bold=True
        ).print(f"{self.agent.agent_name}: Using tool '{self.name}':")
        if self.args and isinstance(self.args, dict):
            for key, value in self.args.items():
                PrintStyle(font_color="#85C1E9", bold=True).stream(f"{key}: ")
                PrintStyle(
                    font_color="#85C1E9",
                    padding=isinstance(value, str) and "\n" in value,
                ).stream(value)
                PrintStyle().print()

    async def after_execution(self, response, **kwargs):
        msg_response = self.agent.read_prompt(
            "fw.tool_response.md", tool_name=self.name, tool_response=response.message
        )
        await self.agent.append_message(msg_response, human=True)

    async def prepare_state(self, reset=False):
        self.state = self.agent.get_data("cot_state")
        if not self.state or reset:
            # Initialize Docker container if execution in Docker is configured
            if self.agent.config.code_exec_docker_enabled:
                docker = DockerContainerManager(
                    logger=self.agent.context.log,
                    name=self.agent.config.code_exec_docker_name,
                    image=self.agent.config.code_exec_docker_image,
                    ports=self.agent.config.code_exec_docker_ports,
                    volumes=self.agent.config.code_exec_docker_volumes,
                )
                docker.start_container()
            else:
                docker = None

            # Initialize local or remote interactive shell interface
            if self.agent.config.code_exec_ssh_enabled:
                shell = SSHInteractiveSession(
                    self.agent.context.log,
                    self.agent.config.code_exec_ssh_addr,
                    self.agent.config.code_exec_ssh_port,
                    self.agent.config.code_exec_ssh_user,
                    self.agent.config.code_exec_ssh_pass,
                )
            else:
                shell = LocalInteractiveSession()

            self.state = State(shell=shell, docker=docker)
            await shell.connect()
        self.agent.set_data("cot_state", self.state)

    async def execute_python_code(self, code):
        escaped_code = shlex.quote(code)
        command = f"python3 -c {escaped_code}"
        return await self.terminal_session(command)

    async def execute_nodejs_code(self, code):
        escaped_code = shlex.quote(code)
        command = f"node -e {escaped_code}"
        return await self.terminal_session(command)

    async def execute_terminal_command(self, command):
        return await self.terminal_session(command)

    async def terminal_session(self, command):
        await self.agent.handle_intervention()  # Wait for intervention and handle it, if paused
        if self.state is None or self.state.shell is None:
            return "Error: Shell is not initialized."
        self.state.shell.send_command(command)
        PrintStyle(background_color="white", font_color="#1B4F72", bold=True).print(
            f"{self.agent.agent_name} code execution output:"
        )
        return await self.get_terminal_output()

    async def get_terminal_output(self, wait_with_output=3, wait_without_output=10):
        if self.state is None or self.state.shell is None:
            return "Error: Shell is not initialized."
        idle = 0
        SLEEP_TIME = 0.1
        full_output = ""
        while True:
            await asyncio.sleep(SLEEP_TIME)  # Wait for some output to be generated
            try:
                full_output, partial_output = await self.state.shell.read_output()
            except AttributeError:
                return "Error: Unable to read output from shell."

            await self.agent.handle_intervention()  # Wait for intervention and handle it, if paused

            if partial_output:
                PrintStyle(font_color="#85C1E9").stream(partial_output)
                if self.log:
                    self.log.update(content=full_output)
                idle = 0
            else:
                idle += 1
                if (full_output and idle > wait_with_output / SLEEP_TIME) or (
                    not full_output and idle > wait_without_output / SLEEP_TIME
                ):
                    return full_output

    async def reset_terminal(self):
        if self.state is None or self.state.shell is None:
            return "Error: Shell is not initialized."
        try:
            self.state.shell.close()
        except AttributeError:
            return "Error: Unable to close shell."
        await self.prepare_state(reset=True)
        response = self.agent.read_prompt("fw.code_reset.md")
        if self.log:
            self.log.update(content=response)
        return response
