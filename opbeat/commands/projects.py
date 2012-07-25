from opbeat.command import CommandBase
import os

class ProjectsCommand(CommandBase):
	name = "projects"
	description = "Sends deployment info ASAP."

	# def add_args(self):
	# 	self.parser.add_argument('--directory', help='Take repository information from this directory.', default=os.getcwd())
	# 	self.parser.add_argument('--module-name', help='Use this as the module name.', default="_repository")

	def run(self, args):
		# self.logger.info('Sending a deployment info...')
		# self.logger.info("Using directory: %s", args.directory)
		# if len(args) > 0:
		# 	directory = os.path.abspath(args[0])
		# 	self.logger.debug("Using directory: %s", directory)
		# else:
		# 	directory = None

		# client.send_deployment_info(directory=args.directory)
		self.logger.info('success!')

command = ProjectsCommand

