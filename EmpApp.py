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


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


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

@app.route("/getemp", methods=['POST'])
def GetEmp():
    return render_template('GetEmp.html')

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

        s3 = boto3.resource('s3')
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)

        try:
            s3.Object(bucket_location, emp_image_file_name_in_s3).delete()
            
        except Exception as e:
            return str(e)

    finally:
        cursor.close()  

    return render_template('RemoveSuccessful.html', emp_id=emp_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
