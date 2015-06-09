#!/usr/bin/env bash
#
# To be executed from application root path
#

#cmd=$($(grep SLA_MANAGER sladashboard/settings.py) && eval $cmd & print $SLA_MANAGER))
eval $(grep SLA_MANAGER_URL sladashboard/settings.py)
echo SLA_MANAGER_URL=$SLA_MANAGER_URL

#
echo \#Add provider-a
#
curl -H "Content-type: application/xml" -d@samples/provider-a.xml $SLA_MANAGER_URL/providers -X POST

#
echo \#Add provider-b
#
curl -H "Content-type: application/xml" -d@samples/provider-b.xml $SLA_MANAGER_URL/providers -X POST

#
echo \#Add template
#
curl -H "Content-type: application/xml" -d@samples/template02.xml $SLA_MANAGER_URL/templates -X POST

#
echo \#Add agreement03
#
curl -H "Content-type: application/xml" -d@samples/agreement03.xml $SLA_MANAGER_URL/agreements -X POST
curl -d@samples/enforcement03.xml -H "Content-type: application/xml" $SLA_MANAGER_URL/enforcements -X POST
curl $SLA_MANAGER_URL/enforcements/agreement03/start -X PUT

#
echo \#Add agreement04
#
curl -H "Content-type: application/xml" -d@samples/agreement04.xml $SLA_MANAGER_URL/agreements -X POST
curl -d@samples/enforcement04.xml -H "Content-type: application/xml" $SLA_MANAGER_URL/enforcements -X POST
curl $SLA_MANAGER_URL/enforcements/agreement04/start -X PUT

#
echo \#Add agreement05
#
curl -H "Content-type: application/xml" -d@samples/agreement05.xml $SLA_MANAGER_URL/agreements -X POST
curl -d@samples/enforcement05.xml -H "Content-type: application/xml" $SLA_MANAGER_URL/enforcements -X POST
#curl $SLA_MANAGER_URL/enforcements/agreement05/start -X PUT

