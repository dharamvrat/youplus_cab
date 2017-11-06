#!/usr/bin/python
from flask import Flask, request
from flask_restful import Resource, Api
import pymysql
from json import dumps
from flask_jsonpify import jsonify
from enum import Enum
import threading
import time

config = {
  'user': 'root',
  'password': 'root',
  'host': 'localhost',
  'database': 'youplus',
}
app = Flask(__name__)
api = Api(app)
MAX_PENDING_REQ = 10
FIVE_MIN_SECS = 300

class StartTripThread(threading.Thread):
    def __init__(self, driver_id, booking_id):
        threading.Thread.__init__(self)
        self.driver_id = driver_id
        self.booking_id = booking_id
    def run(self):
        start_trip(self.driver_id, self.booking_id);
        time.sleep(FIVE_MIN_SECS)
        end_trip(self.booking_id)

def start_trip(driver_id, booking_id):
    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    try:
        update_lock.acquire()
        cursor.execute("UPDATE booking SET pickup_at = CURRENT_TIMESTAMP, status = %s, driver_id = %s \
            WHERE id = %s", (BookingStatus.ONGOING, int(driver_id), int(booking_id)))
        conn.commit()
    except:
        conn.rollback()
    finally:
        update_lock.release()
        cursor.close()
        conn.close()

def end_trip(booking_id):
    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    try:
        update_lock.acquire()
        cursor.execute("UPDATE booking SET completed_at = CURRENT_TIMESTAMP, status = %s \
        WHERE id = %s", (BookingStatus.COMPLETED, int(booking_id)))
        conn.commit()
    except:
        conn.rollback()
    finally:
        update_lock.release()
        cursor.close()
        conn.close()

update_lock = threading.Lock()

class BookingStatus(Enum):
    WAITING = 'WAITING'
    ONGOING = 'ONGOING'
    COMPLETED = 'COMPLETED'

class BookingReq(Resource):
    def get(self, customer_id):
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        result = {}
        try:
            cursor.execute("SELECT COUNT(*) FROM booking WHERE status = %s", BookingStatus.WAITING)
            pending_req_count = cursor.fetchone()[0]
            if (int(pending_req_count) >= MAX_PENDING_REQ):
                result = {'status': 'Error', 'message':'All drivers busy, Maximum waiting list reached'}
            else:
                cursor.execute("INSERT INTO BOOKING(customer_id) VALUES(%s)" ,int(customer_id))
                conn.commit()
                result = {'status': 'Success', 'message': 'Booking successful, Waiting for driver'}
        except:
            conn.rollback()
            result = {'status': 'Error', 'message': 'Exception in connection to DB'}
        finally:
            cursor.close()
            conn.close()
            return jsonify(result)

class Dashboard(Resource):
    def get(self):
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        result = {}
        try:
            cursor.execute("SELECT id as request_id, customer_id, driver_id, \
            TIMESTAMPDIFF(SECOND, created_at, CURRENT_TIMESTAMP) as time_elapsed, status FROM booking")
            result = [dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
            result = {'status' : 'Success', 'message' : result}
        except:
            result = {'status': 'Error', 'message': 'Exception in connection to DB'}
        finally:
            cursor.close()
            conn.close()
            return jsonify(result)
        
class AcceptDriverReq(Resource):
    def get(self, driver_id, booking_id):
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        result = {}
        try:
            cursor.execute("SELECT * FROM booking WHERE id = %s and status = %s", (booking_id, BookingStatus.WAITING))
            if not cursor.rowcount:
                result = {'status': 'Error', 'message': 'Booking either Ongoing or Completed'}
            else:
                thread = StartTripThread(driver_id, booking_id)
                thread.start()
                result = {'status': 'Success', 'message' : 'Refresh to see current status'}
        except:
            result = {'status': 'Error', 'message': 'Exception Found'}
        finally:
            cursor.close()
            conn.close()
            return jsonify(result)

class DriverDashboard(Resource):
    def get(self, driver_id):
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        result = {}
        try:
            # this could be used when we want to implement login using driver id
            # cursor.execute("SELECT * FROM driver WHERE id = %s", int(driver_id))
            # if not cursor.rowcount:
            #    result = {'status': 'Error', 'result': 'driver id does not exist'}
            cursor.execute("SELECT id as request_id, customer_id, \
                TIMESTAMPDIFF(MINUTE, created_at, CURRENT_TIMESTAMP) as requested_min \
                FROM booking WHERE status = %s", BookingStatus.WAITING)
            waiting_req = [dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]

            cursor.execute("SELECT id as request_id, customer_id, \
                TIMESTAMPDIFF(MINUTE, created_at, CURRENT_TIMESTAMP) as requested_min, \
                TIMESTAMPDIFF(MINUTE, pickup_at, CURRENT_TIMESTAMP) as pickup_min \
                FROM booking WHERE status = %s and driver_id = %s", \
                (BookingStatus.ONGOING, int(driver_id)))
            ongoing_req = [dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
            
            cursor.execute("SELECT id as request_id, customer_id, \
                TIMESTAMPDIFF(MINUTE, created_at, CURRENT_TIMESTAMP) as requested_min, \
                TIMESTAMPDIFF(MINUTE, pickup_at, CURRENT_TIMESTAMP) as pickup_min, \
                TIMESTAMPDIFF(MINUTE, completed_at, CURRENT_TIMESTAMP) as completed_min \
                FROM booking WHERE status = %s and driver_id = %s", \
                (BookingStatus.COMPLETED, int(driver_id)))
            completed_req = [dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]

            result = {'waiting' : waiting_req, 'ongoing' : ongoing_req, 'completed' : completed_req}
            result = {'status' : 'Success', 'message' : result}
        except:
            result = {'status': 'Error', 'message': 'Exception in connection to DB'}
        finally:
            cursor.close()
            conn.close()
            return jsonify(result)

api.add_resource(BookingReq, '/customer/<customer_id>')
api.add_resource(Dashboard, '/dashboard')
api.add_resource(AcceptDriverReq, '/driver/<driver_id>/<booking_id>')
api.add_resource(DriverDashboard, '/driver/<driver_id>')

if __name__ == '__main__':
     app.run(port='8080')
