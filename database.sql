
-- Students Table
CREATE TABLE IF NOT EXISTS students (
    roll_no VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    class VARCHAR(10) NOT NULL
);




-- Attendance Table
CREATE TABLE IF NOT EXISTS attendance (
    student_id VARCHAR(20) PRIMARY KEY,
    date DATE NOT NULL,
    status ENUM('Present', 'Absent') NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(roll_no)
);




-- Marks Table
CREATE TABLE IF NOT EXISTS marks (
    student_id VARCHAR(20) PRIMARY KEY,
    subject VARCHAR(50) NOT NULL,
    marks INT NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(roll_no)
);
