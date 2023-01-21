#include <sqlite3.h>
#include <iostream>


extern "C"
void createTable() {
	int rc;
	sqlite3 *db;
	char *zErrMsg = 0;
	const char *sql;

	rc = sqlite3_open("candle.db", &db);

	if (rc) {
		std::cerr << "Can't open database: " << sqlite3_errmsg(db) << std::endl;
		return;
	} else {
		std::cout << "Opened database successfully" << std::endl;
	}


	// Create SQL statement
	sql = "CREATE TABLE IF NOT EXISTS requests("  \
      		"date TEXT NOT NULL," \
      		"url TEXT NOT NULL," \
      		"user TEXT NOT NULL);";

	rc = sqlite3_exec(db, sql, 0, 0, &zErrMsg);

	if (rc != SQLITE_OK) {
		std::cerr << "SQL error: " << zErrMsg << std::endl;
		sqlite3_free(zErrMsg);
	}

	sqlite3_close(db);
}

extern "C"
void saveToDB(char *url, char *user) {
	sqlite3 *db;
	char *sql;
	int rc;
	char *zErrMsg = 0;

	// Open database
	rc = sqlite3_open("candle.db", &db);

	if (rc) {
		std::cerr << "Can't open database: " << sqlite3_errmsg(db) << std::endl;
		return;
	} else {
		std::cout << "Opened database successfully" << std::endl;
	}

	// Create SQL statement
	sql = sqlite3_mprintf("INSERT INTO requests (date, url, user) VALUES (datetime('now'), '%q', '%q');", url, user);

	rc = sqlite3_exec(db, sql, 0, 0, &zErrMsg);

	if (rc != SQLITE_OK) {
		std::cerr << "SQL error: " << zErrMsg << std::endl;
		sqlite3_free(zErrMsg);
	}

	sqlite3_close(db);
}
	

