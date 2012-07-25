	@mock.patch('ssh.config.SSHConfig', MockConfigParser)
	def test_annotate(self):
		# parse['return_value'] = MockConfigParser({'github.com'})

		url ='https://ron@opbeat_python:opbeat/opbeat_python.git'
		actual_url = annotate_url_with_ssh_config_info(url)

		self.assertEqual(actual_url, 'https://ron@github.com/opbeat/opbeat_python.git')
		
