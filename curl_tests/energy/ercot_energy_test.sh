#!/bin/bash -x

export DB_IP=localhost
export API_IP=127.0.0.1
export DB_USER=postgres
export PGPASSWORD=postgres

# WARNING truncates table
truncate_energy () {
  psql -h $DB_IP -U $DB_USER -c "truncate trueprice.$1_energy;" trueprice
  psql -h $DB_IP -U $DB_USER -c "truncate trueprice.$1_energy_history;" trueprice
}

# $1 == "iso"
psql_check () {
  psql -h $DB_IP -U $DB_USER -c "select * from trueprice.$1_energy;" trueprice > psql_results.txt
  if [[ $(wc -l psql_results.txt | awk '{print $1}') -eq "65" ]]; then
    return 0
  fi
}

# $1 == "iso"
api_check () {
  curl -sw "%{http_code}" "http://$API_IP:5555/get_data?start=20230301&end=20280301&iso=$1&strip=7x8&curve_type=forwardcurve&type=csv" > api_results.txt
  if [[ $(wc -l api_results.txt | awk '{print $1}') -eq "62" ]]; then
    return 0
  fi
}

psql_history_check () {
  psql -h $DB_IP -U $DB_USER -c "select * from trueprice.$1_energy_history;" trueprice > psql_results.txt
  if [[ $(wc -l psql_results.txt | awk '{print $1}') -eq "65" ]]; then
    return 0
  fi
}

upload_check () {
  # curl -s -o /dev/null -w "%{http_code}" -H "Content-Type: multipart/form-data" -F "file=@$1" http://$API_IP:5001/upload
  curl -v -X POST -H "Content-Type: multipart/form-data" -F "file=@$1" http://localhost:5555/upload_csv
}

# $1 == "iso"
# api_history_check () {
#   curl -sw "%{http_code}" "http://$API_IP:5001/get_data?start=20230101&end=20291231&iso=$1&strip=5x16&curve_type=forwardcurve&type=csv" > api_results.txt
#   if [[ $(wc -l api_results.txt | awk '{print $1}') -eq "62" ]]; then
#     return 0
#   fi
# }

truncate_energy "ercot"

# upload 1
if ! upload_check "buildContext/good_test_data/energy/Energy_ERCOT_20230330_083040.csv"; then
  printf "error upload_check"
fi

# check existance via psql
if ! psql_check "ercot"; then
  printf "error psql_check"
fi

# check existance via api
if ! api_check "ercot"; then
  printf "error api_check"
fi

if ! upload_check "buildContext/good_test_data/energy/Energy_ERCOT_20230330_113740.csv"; then
  printf "error upload_check, intraday update"
fi

# check existance via psql
if ! psql_check "ercot"; then
  printf "error psql_check"
fi

# check existance via api
if ! api_check "ercot"; then
  printf "error api_check"
fi

# add history table versus current table
if ! psql_history_check "ercot"; then
  printf "error api_history_check"
fi