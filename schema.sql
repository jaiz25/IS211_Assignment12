DROP TABLE IF EXISTS students;
CREATE TABLE students (
  id integer primary key autoincrement,
  first_name text not null,
  last_name text not null
);

DROP TABLE IF EXISTS quizzes;
CREATE TABLE quizzes (
  id integer primary key autoincrement,
  subject text not null,
  number_of_questions integer not null,
  date_of_quiz date not null
);

DROP TABLE IF EXISTS student_result;
CREATE TABLE student_result (
  student_id integer,
  quiz_id integer,
  score integer,
  FOREIGN KEY (student_id) REFERENCES students(id),
  FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
);