# logstash-zabbix

## Install requirements

From pip:

`pip install protobix`

## Configuration

Import Template in Zabbix with Template_Logstash.xml

Put logstash.py in UserParameter in zabbix agent configuration.

`UserParameter=logstash.check,/usr/local/bin/logstash.py --update-items
UserParameter=logstash.discovery,/usr/local/bin/logstash.py --discovery`

Restart zabbix agent.

Link Template to host in Zabbix.

Enjoy!
