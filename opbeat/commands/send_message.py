from opbeat.command import CommandBase



class SendTestMessageCommand(CommandBase):
	name = "send_test_message"
	description = "Sends test error message to Opbeat"

	def add_args(self):
		self.parser.add_argument('--project-id', help='Use this project id.')

	def run(self, args):
		self.logger.info('Sending message...')
		ident = client.get_ident(client.captureMessage(
			message='This is a test message generated using ``opbeat send_test_message``',
			data={
				'culprit': 'opbeat_python.scripts.runner',
				'logger': 'opbeat_python.test',
				'http': {
					'method': 'GET',
					'url': 'http://example.com',
				}
			},
			level=logging.INFO,
			stack=True,
			extra={
				'user': pwd.getpwuid(os.geteuid())[0],
				'loadavg': os.getloadavg(),
			}
		))

		self.logger.info('success!')

command = SendTestMessageCommand
