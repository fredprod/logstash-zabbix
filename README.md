# logstash-zabbix

Work with Logstash 5.x versions.

## Install requirements

From pip:

`pip install protobix`

## Configuration

Import Template in Zabbix with Template_Logstash.xml if you are using Zabbix 3.4.
If you are using Zabbix 3.2, you can use Template_Logstash-32.xml.

Put logstash.py in UserParameter in zabbix agent configuration.

`UserParameter=logstash.check,/usr/local/bin/logstash.py --update-items
UserParameter=logstash.discovery,/usr/local/bin/logstash.py --discovery`

Restart zabbix agent.

Link Template to host in Zabbix.

Enjoy!
