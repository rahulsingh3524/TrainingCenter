Example for adding data to this API using POST

curl -X POST http://127.0.0.1:5000/training-center ^
-H "Content-Type: application/json" ^
-d "{\"center_name\": \"IoT Training Center\", \"center_code\": \"IOTC12345678\", \"address\": {\"detailed_address\": \"44 IoT Avenue\", \"city\": \"Bangalore\", \"state\": \"Karnataka\", \"pincode\": \"560002\"}, \"student_capacity\": 140, \"courses_offered\": [\"IoT\", \"Embedded Systems\"], \"contact_email\": \"iot@example.com\", \"contact_phone\": \"9876543220\"}"


Example to fatch data using GET

curl -X GET http://127.0.0.1:5000/training-centers
