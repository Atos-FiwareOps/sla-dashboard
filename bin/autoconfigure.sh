#!/bin/bash

cp sladashboard/settings.py.sample sladashboard/settings.py

sed 's/{sla_manager_url}/'$sla_manager_url'/g' sladashboard/settings.py -i
sed 's/{sla_manager_user}/'$sla_manager_user'/g' sladashboard/settings.py -i
sed 's/{sla_manager_password}/'$sla_manager_password'/g' sladashboard/settings.py -i
sed 's/{sla_gui_host}/'$sla_gui_host'/g' sladashboard/settings.py -i
sed 's/{idm_client_id}/'$idm_client_id'/g' sladashboard/settings.py -i
sed 's/{idm_client_secret}/'$idm_client_secret'/g' sladashboard/settings.py -i

echo "Autoconfiguring executed successfully"

exit 0
