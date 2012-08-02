from opbeat.command import CommandBase
import os

class ProjectsCommand(CommandBase):
	name = "projects"
	description = "Lists projects."

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

