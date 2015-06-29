#!/bin/bash

cp sladashboard/settings.py.sample sladashboard/settings.py

sed 's/{sla_manager_url}/'$sla_manager_url'/g' sladashboard/settings.py -i
sed 's/{sla_manager_user}/'$sla_manager_user'/g' sladashboard/settings.py -i
sed 's/{sla_manager_password}/'$sla_manager_password'/g' sladashboard/settings.py -i

echo "Autoconfiguring executed successfully"

exit 0
