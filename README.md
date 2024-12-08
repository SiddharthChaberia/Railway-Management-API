# Railway-Management-API
This API provides endpoints for user authentication, train management, and seat booking for a railway management system.

## Quick Setup Using Docker (check next block to setup manually)
If you have docker installed in your system, you can setup quickly with the following commands
```bash
git clone https://github.com/SiddharthChaberia/Railway-Management-API/
cd Railway-Management-API
```
```bash
docker build -t railway-management-api .
```
```bash
docker run -d -p 5000:5000 --name railway-api railway-management-api
```
If the docker runs succesfully, then the API would be live at http://127.0.0.1:5000 <br>
Skip to the 'Testing The API' part.

## Setup For Those Not Having Docker (Skip if you have finished setup using docker)
1. Clone the repository and navigate to the project directory:
   ```bash
   git clone https://github.com/SiddharthChaberia/Railway-Management-API
   cd Railway-Management-API
   ```
2. Install the necessary modules to run this code:
    ```bash
    pip install -r requirements.txt
    ```
3. Create and configure the .ENV file:
   ```bash
   JWT_SECRET_KEY=<your_jwt_token_here>
   admin_auth_key=<your_admin_auth_key_here>
   ```
4. Initialize the database: 
    - ensure you have latest version of MySQL (8.0) on your device installed and ready to connect
    - check the schema.sql file and set your database accordingly
    - alternatively, you can just run the following program in your cmd to initialize your database with the required configurations
    ```bash
    python initializeDB.py
    ```
5. For testing purpose, you can generate a 32-bit JWT token using the following command in your terminal:
   ```bash
   python JWTTokenGen.py
   ```

## Run The Program

1.Start the API server
  ```bash
  python app.py
  ```
2. If all the insallation steps are executed without errors, then the API would be live at http://127.0.0.1:5000

## Testing the API 
Use tools like postman to test the endpoints
- Register A User (/register)
- Login User (/login)
- Add a New Train (/trains)
- Get Seat Availability (/trains/availability)
- Book a Seat (/bookings)
- Get Specific Booking Details (/bookings/<int:book_id>)
Refer to the code files, to have better understanding of the endpoints

Feel free to submit issues or pull requests to improve this API. Was just learning about flask and dockerfiles.

**Connect with me on**:
* [Linkedin](https://www.linkedin.com/in/siddharth-chaberia/)
* [Telegram](https://t.me/SiddharthChaberia)
* [Facebook](https://www.facebook.com/chaberia.siddharth/)
* [Instagram](https://www.instagram.com/siddharth_chaberia_02/)
* [Twitter](https://x.com/03Chaberia)
