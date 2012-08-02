from opbeat.command import CommandBase
from opbeat.credentials import load_credentials

class StatusCommand(CommandBase):
	name = "status"
	description = "Outputs various information regarding login, projects etc.."

	def run(self, args):
		credentials = load_credentials(args.config_file)

		if not credentials:
			self.logger.info("Not logged in.")
		else:
			self.logger.info("Logged in.")
			self.logger.info("Credentials expire on %s", credentials['expires'])

command = StatusCommand
