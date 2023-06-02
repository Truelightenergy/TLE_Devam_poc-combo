#!/bin/bash -x

export DB_IP=localhost
export API_IP=127.0.0.1
export DB_USER=postgres
export PGPASSWORD=postgres


response=$(curl -d "email=ali.haider@techliance.com&password=admin&submit=Login" -s http://127.0.0.1:5555/login)
# Extract the authentication token from the response using grep and cut
token=$(echo "$response" | grep -o '"access_token":"[^"]*' | cut -d '"' -f 4)
# Print the authentication token
echo "Authentication token: $token"

# WARNING truncates table
truncate_nonenergy () {
  psql -h $DB_IP -U $DB_USER -c "truncate trueprice.$1_nonenergy;" trueprice
  psql -h $DB_IP -U $DB_USER -c "truncate trueprice.$1_nonenergy_history;" trueprice
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
  curl -sw "%{http_code}" "http://127.0.0.1:5555/get_data?start=20030301&end=20380301&iso=$1&strip=7x24&strip=7x8&strip=5x16&strip=2x16&curve_type=nonenergy&type=csv&history=false" > api_results.txt -H "Authorization: Bearer $token"
  if [[ $(wc -l api_results.txt | awk '{print $1}') -eq "62" ]]; then
    return 0
  fi
}

psql_history_check () {
  psql -h $DB_IP -U $DB_USER -c "select * from trueprice.$1_nonenergy_history;" trueprice > psql_results.txt
  if [[ $(wc -l psql_results.txt | awk '{print $1}') -eq "65" ]]; then
    return 0
  fi
}

upload_check () {
  # curl -s -o /dev/null -w "%{http_code}" -H "Content-Type: multipart/form-data" -F "file=@$1" http://$API_IP:5001/upload
  curl -v -X POST -H "Content-Type: multipart/form-data" -F "file=@$1" http://localhost:5555/upload_csv  -H "Authorization: Bearer $token"

}



truncate_nonenergy "ercot"

# upload 1
if ! upload_check "/home/alee/Documents/truelight/poc-combo/buildContext/good_test_data/nonenergy/NonEnergy_ERCOT_20230419_101010.csv"; then
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

if ! upload_check "/home/alee/Documents/truelight/poc-combo/buildContext/good_test_data/nonenergy/NonEnergy_ERCOT_20230419_101011.csv"; then
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
