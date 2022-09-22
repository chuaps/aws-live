from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'

# home
@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('Home.html')

# about
@app.route("/about", methods=['POST'])
def about():
    return render_template('')

# Redirect Add Employee
@app.route("/toAddEmp", methods=['GET', 'POST'])
def ToAddEmp():
    return render_template('AddEmp.html')

# Redirect Remove Employee
@app.route("/toRemEmp", methods=['GET', 'POST'])
def ToRemEmp():
    return render_template('RemEmp.html')

# Redirect Edit Employee
@app.route("/toEditEmp", methods=['GET', 'POST'])
def ToEditEmp():
    return render_template('EditEmp.html')

# Redirect Search Employee
@app.route("/toGetEmp", methods=['POST'])
def ToGetEmp():
    return render_template('GetEmp.html')

# Redirect Manage Employee
@app.route("/tomanageemp", methods=['GET', 'POST'])
def ToManEmp():
    return render_template('ManageEmployee.html')

# Redirect Attendance
@app.route("/tomanageattendance", methods=['GET', 'POST'])
def ToManageAttendance():
    return render_template('ManageAttendance.html')

# Redirect Attendance
@app.route("/toAttendance", methods=['GET', 'POST'])
def ToAttendance():
    return render_template('Attendance.html')

# Redirect Attendance
@app.route("/toRemAttendance", methods=['GET', 'POST'])
def ToRemAttendance():
    return render_template('RemAttendance.html')

# Redirect Attendance
@app.route("/toEditAttendance", methods=['GET', 'POST'])
def ToEditAttendance():
    return render_template('EditAttendance.html')

# Add Employee Function
@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location, emp_image_file))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)



@app.route("/fetchemp", methods=['POST'])
def FetchEmp():
    emp_id = request.form['emp_id']

    fetch_sql = "SELECT * FROM employee where emp_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(fetch_sql, (emp_id))
        db_conn.commit()
        results = cursor.fetchall()
        for row in results:
            emp_id = row[0]
            first_name = row[1]
            last_name = row[2]
            pri_skill = row[3]
            location = row[4]
            emp_image_file = row[5]

        s3 = boto3.resource('s3')
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"

        try:
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)
            
        except Exception as e:
            return str(e)
            
    except:
        print ("Error: unable to fecth data")    

    print("Employee Searched")
    return render_template('GetEmpOutput.html', id=emp_id, fname=first_name, lname=last_name, interest=pri_skill, location=location, image_url=object_url)
    

@app.route("/listemp", methods=['GET'])
def ListEmp():
    fetch_sql = "SELECT * FROM employee"
    cursor = db_conn.cursor()

    try:
        cursor.execute(fetch_sql)
        db_conn.commit()
        results = cursor.fetchall()
                 

    except:
        print ("Error: unable to fecth data")

    return render_template('ListEmp.html', results=results)
    

@app.route("/rememp", methods=['POST'])
def RemEmp():

    emp_id = request.form['emp_id']
    
    fetch_sql = "DELETE FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(fetch_sql, (emp_id))
        db_conn.commit()

        s3 = boto3.client('s3')
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"

        try:
            s3.delete_object(Bucket='chuaphingswen-employee', Key=emp_image_file_name_in_s3)
            
        except Exception as e:
            return str(e)

    finally:
        cursor.close()  

    return render_template('RemEmpOutput.html', emp_id=emp_id)

@app.route("/searcheditemp", methods=['POST', 'GET'])
def SearchEditEmp():
    emp_id = request.form['emp_id']

    fetch_sql = "SELECT * FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(fetch_sql, (emp_id))
        db_conn.commit()
        results = cursor.fetchall()

    except:
        print ("Error: unable to fecth data")

    return render_template('EditEmpForm.html', results=results)

@app.route("/editemp", methods=['POST', 'GET'])
def EditEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    fetch_sql = "UPDATE employee SET first_name=%s, last_name=%s, pri_skill=%s, location=%s, emp_image_file=%s where emp_id = %s"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(fetch_sql, (first_name, last_name, pri_skill, location, emp_image_file, emp_id))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('EditEmpOutput.html', fname=first_name,lname=last_name)

# Add Attendance
@app.route("/addattendance", methods=['POST'])
def addAttend():
    duty_id = request.form['duty_id']
    emp_id = request.form['emp_id']
    date = request.form['date']
    duration = request.form['duration']

    insert_attendance = "INSERT INTO duty VALUES (%s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_attendance, (duty_id, emp_id, date, duration))
        db_conn.commit()

    except:
        print ("Error: unable to fecth data")

    return render_template('AttendanceOutput.html', id=emp_id, date=date)

# View Attendance
@app.route("/viewattendance", methods=['POST'])
def ViewAttend():
    cur = db_conn.cursor()
    cur.execute("SELECT * FROM duty")
    results = cur.fetchall()
    return render_template('ListAttendance.html', results=results) 

# Remove Attendance
@app.route("/remattendance", methods=['POST'])
def RemAttend():

    duty_id = request.form['duty_id']
    
    fetch_sql = "DELETE FROM duty WHERE duty_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(fetch_sql, (duty_id))
        db_conn.commit()

    finally:
        cursor.close()  

    return render_template('RemAttendanceOutput.html', duty_id=duty_id)

# Edit Attendance
@app.route("/searcheditattendance", methods=['POST', 'GET'])
def SearchEditAttend():
    duty_id = request.form['duty_id']

    fetch_sql = "SELECT * FROM duty WHERE duty_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(fetch_sql, (duty_id))
        db_conn.commit()
        results = cursor.fetchall()

    except:
        print ("Error: unable to fecth data")

    return render_template('EditAttendanceForm.html', results=results)

@app.route("/editattendance", methods=['POST', 'GET'])
def EditAttend():
    duty_id = request.form['duty_id']
    emp_id = request.form['emp_id']
    date = request.form['date']
    duration = request.form['duration']

    fetch_sql = "UPDATE duty SET emp_id=%s, date=%s, duration=%s where duty_id = %s"
    cursor = db_conn.cursor()

    try:

        cursor.execute(fetch_sql, (emp_id, date, duration, duty_id))
        db_conn.commit()
        
    finally:
        cursor.close()

    print("all modification done...")
    return render_template('EditAttendanceOutput.html', duty_id=duty_id)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
