# Classroom50
#### Video demo:  https://youtu.be/SkWuqCN2KT4
#### Description:
Classroom50 is a web-based application that allows teachers and students to collaborate together.
## Features
Here are the features that Classroom50 provides:
#### Register and Login
Users can register and login.
#### User profile
Users can view their profile and change their passwords.
#### Create and join classrooms
Teachers can create classrooms and invite other teachers and students to join their classrooms through a code.
#### Posts and comments
Posts and comments can be created by all users in the classroom which allows users to communicate with one another.
#### Assignments
Assignments can be created by teachers. Assignments can have a deadline (20 minutes minimum) or no deadline at all. Students can submit an assignment which in turn can be downloaded and graded by the teacher who created the assignment.
#### Members
Users can view the classroom members and owners can remove users from the classroom.
#### Manage classrooms
Owners of classrooms can manage their classrooms. This includes resetting the classroom code and deleting the classroom.
## Implementation
- /classroom50
  - /static
    - favicon.ico (Application icon)
    - navbar.js (Contains the functionality used to implement active links in the navigation bars)
    - styles.css (Contains the CSS styles)
    - toggle_password.js (Contains the functionality used to toggle the visibility of passwords)
  - /templates
    - /auth
      - login.html (Login template)
      - register.html (Register template)
    - /classroom
      - assignments.html (Assignments template)
      - create_assignment.html (Create assignment template)
      - home.html (Classroom home template)
      - members.html (Members template)
      - post.html (Post template)
      - settings.html (Settings template)
      - submission.html (Submission template)
    - /layout
      - base.html (Base layout template)
      - classroom.html (Classroom layout template)
    - /main
      - create.html (Create classroom template)
      - join.html (Join classroom template)
    - /profile
      - profile.html (Profile template)
  - /views
    - assignments.py (Contains the assignments list, create and delete assignment, submission, submit and delete submission, download and grade submission views)
    - auth.py (Contains the register and login views, a before app request function which loads a user before every request and decorators used to check if a user is logged in, student, teacher and owner)
    - classroom.py (Parent blueprint of all classroom blueprints and contains a before app request function used to check if a user is allowed to access a classroom and loads the classroom owner id if allowed)
    - home.py (Contains the classroom home, create and delete posts and comments views)
    - main.py (Contains the index, create and join classroom views)
    - manage.py (Contains the reset code and delete classroom views)
    - members.py (Contains the members and remove user views)
    - profile.py (Contains the profile view)
  - \_\_init\_\_.py (Contains the application factory and it tells Python that the classroom50 directory should be treated as a package)
  - db.py (Contains the functions used to connect to, initialize and access the database)
  - schema.sql (Contains the schema of the database)
- README.md
- requirements.txt (Contains the application requirements)
## Instructions
You should be in the top-level `project` directory before running the commands.
#### Initialize the database
`$ python -m flask --app classroom50 init-db`
#### Run the application
`$ python -m flask --app classroom50 run`