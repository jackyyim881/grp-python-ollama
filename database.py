# database.py
import sqlite3
from config import Config
from logger import setup_logger

logger = setup_logger()


class DatabaseService:
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.conn.cursor()
            self.initialize_tables()
            logger.info("Database connected successfully.")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def initialize_tables(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS assessment_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    topic TEXT,
                    question TEXT,
                    user_answer TEXT,
                    correct_answer TEXT,
                    correct INTEGER,
                    explanation TEXT
                )
            ''')
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_logins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                login_time TEXT
            )
        ''')
            self.conn.commit()
            logger.info("Database tables initialized.")
        except sqlite3.Error as e:
            logger.error(f"Error initializing tables: {e}")
            raise

    def insert_result(self, username, topic, question, user_answer, correct_answer, correct, explanation):
        try:
            self.cursor.execute('''
                INSERT INTO assessment_results 
                (username, topic, question, user_answer, correct_answer, correct, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, topic, question, user_answer, correct_answer, correct, explanation))
            self.conn.commit()
            logger.info("Inserted assessment result.")
        except sqlite3.Error as e:
            logger.error(f"Database insertion error: {e}")

    def fetch_results(self, username):
        try:
            self.cursor.execute('''
                SELECT topic, question, user_answer, correct_answer, correct, explanation 
                FROM assessment_results WHERE username = ?
            ''', (username,))
            results = self.cursor.fetchall()
            logger.info("Fetched assessment results.")
            return results
        except sqlite3.Error as e:
            logger.error(f"Database fetch error: {e}")
            return []

    def update_explanation(self, username, topic, question, explanation):
        try:
            self.cursor.execute('''
                UPDATE assessment_results SET explanation = ?
                WHERE username = ? AND topic = ? AND question = ?
            ''', (explanation, username, topic, question))
            self.conn.commit()
            logger.info("Updated explanation in assessment results.")
        except sqlite3.Error as e:
            logger.error(f"Database update error: {e}")

    def insert_login_time(self, username, login_time):
        try:
            self.cursor.execute('''
                    INSERT INTO user_logins (username, login_time) VALUES (?, ?)
                ''', (username, login_time))
            self.conn.commit()
            logger.info("Inserted login time for user.")
        except sqlite3.Error as e:
            logger.error(f"Database insertion error: {e}")

    def get_login_count(self, username):
        try:
            self.cursor.execute('''
                SELECT COUNT(*) FROM user_logins WHERE username = ?
            ''', (username,))
            result = self.cursor.fetchone()
            count = result[0] if result else 0
            logger.info(f"Fetched login count for user {username}: {count}")
            return count
        except sqlite3.Error as e:
            logger.error(f"Database fetch error: {e}")
            return 0

    def get_total_questions_answered(self, username):
        try:
            self.cursor.execute('''
                SELECT COUNT(*) FROM assessment_results WHERE username = ?
            ''', (username,))
            result = self.cursor.fetchone()
            count = result[0] if result else 0
            logger.info(f"Fetched total questions answered for user {
                        username}: {count}")
            return count
        except sqlite3.Error as e:
            logger.error(f"Database fetch error: {e}")
            return 0

    def get_total_correct_answers(self, username):
        try:
            self.cursor.execute('''
                SELECT COUNT(*) FROM assessment_results WHERE username = ? AND correct = 1
            ''', (username,))
            result = self.cursor.fetchone()
            count = result[0] if result else 0
            logger.info(f"Fetched total correct answers for user {
                        username}: {count}")
            return count
        except sqlite3.Error as e:
            logger.error(f"Database fetch error: {e}")
            return 0

    def get_previous_login_time(self, username):
        try:
            self.cursor.execute('''
                SELECT login_time FROM user_logins WHERE username = ? ORDER BY id DESC LIMIT 1 OFFSET 1
            ''', (username,))
            result = self.cursor.fetchone()
            login_time = result[0] if result else None
            logger.info(f"Fetched previous login time for user {
                        username}: {login_time}")
            return login_time
        except sqlite3.Error as e:
            logger.error(f"Database fetch error: {e}")
            return None

    def get_student_performance(self, username):
        try:
            # Fetch total questions answered and total correct answers
            self.cursor.execute('''
                SELECT COUNT(*) FROM assessment_results WHERE username = ?
            ''', (username,))
            total_answered = self.cursor.fetchone()[0]

            self.cursor.execute('''
                SELECT COUNT(*) FROM assessment_results WHERE username = ? AND correct = 1
            ''', (username,))
            total_correct = self.cursor.fetchone()[0]

            # Fetch topics the student has attempted
            self.cursor.execute('''
                SELECT DISTINCT topic FROM assessment_results WHERE username = ?
            ''', (username,))
            topics_attempted = [row[0] for row in self.cursor.fetchall()]

            # Fetch topics where the student struggled (less than 50% correct)
            topics_struggled = []
            for topic in topics_attempted:
                self.cursor.execute('''
                    SELECT COUNT(*) FROM assessment_results WHERE username = ? AND topic = ?
                ''', (username, topic))
                topic_total = self.cursor.fetchone()[0]

                self.cursor.execute('''
                    SELECT COUNT(*) FROM assessment_results WHERE username = ? AND topic = ? AND correct = 1
                ''', (username, topic))
                topic_correct = self.cursor.fetchone()[0]

                if topic_total > 0 and (topic_correct / topic_total) < 0.5:
                    topics_struggled.append(topic)

            performance_data = {
                'total_answered': total_answered,
                'total_correct': total_correct,
                'topics_attempted': topics_attempted,
                'topics_struggled': topics_struggled
            }
            return performance_data
        except sqlite3.Error as e:
            logger.error(f"Database fetch error: {e}")
            return {}

    def close(self):
        try:
            self.conn.close()
            logger.info("Database connection closed.")
        except sqlite3.Error as e:
            logger.error(f"Error closing database connection: {e}")
