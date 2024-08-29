"""
Handles the operations of the endpoints
"""

import os
import sys
import re
import shutil
import time
import zipfile
from datetime import datetime
import utils.trueprice_database as tpdb
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, url_for, flash, render_template, Response, session, jsonify, make_response
from flask import render_template
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import logging
from .auth_model import AuthUtil
from blueprints.notifier.job_notifier import Process_Notifier as Notification_Process_Notifier
from blueprints.notifier.util import Util as Notification_Util




class Util:
    """
    Handles all the api calls 
    """

    def __init__(self, secret_key, secret_salt):
        """
        all the intializers will be handled here
        """
        
        self.auth_util = AuthUtil(secret_key, secret_salt)

    def is_valid_email(self, email):
        """
        Returns True if the given string is a valid email address, otherwise False.
        """
        pattern = r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?" 
        pattern = re.compile(pattern)
        if re.match(pattern, email):
            return True
        return False


    def validate_input(self, email, pswd, prv_level):
        """
        validate user's input
        """
        levels = ['read_only_user', 'admin', 'read_write_user']
        flag = True
        if prv_level not in levels:
            flag = False
        
        if len(pswd)==0:
            flag = False
        if not self.is_valid_email(email):
            flag = False
        
        return flag


    def signup(self, email, pswd, prv_level="read_only_user"):
        """
        create user
        """           
        
        if self.validate_input(email, pswd, prv_level):
            response = self.auth_util.create_user(email, pswd, prv_level)
            if response:
                logging.info(f"User Created with email {email}")
                return {"flash_message": True, "message_toast":"User Created", "message_flag":"success"},200
            
            else:
                logging.error(f"Unable to Creat User with email {email}")
                return {"flash_message": True, "message_toast":"Unable to create user", "message_flag":"error"},200
        else:
            logging.error(f"Unable to Creat User with email {email}")
            return {"flash_message": True, "message_toast":"Unable to create user", "message_flag":"error"},200

    def login(self, email, pswd):
        """
        login to the application
        """
        
        # if request.method == 'POST':
        
        

        auth_flag, prv_level = self.auth_util.authenticate_user(email, pswd)
        if auth_flag:
            _, jwt_token = self.auth_util.encode_auth_token(email, pswd, prv_level)
            session["jwt_token"] = jwt_token
            session["user"] = email
            session["level"] = prv_level
            logging.info(f"{session['user']}: User Logged In SUCCESSFULLY")
            return {"msg":"Logged In Successfully", "message_flag":"success", "access_token":jwt_token},200
        else:
            logging.error(f"{email}: User Logged In FAILED")
            return {"message_toast":"Login Failed", "flash_message":True, "message_flag":"error"},200

    
    def logout(self):
        """
        logout the application
        """
        logging.info(f"{session['user']}: User Logged Out")
        session["jwt_token"] = None
        session["user"] = None
        session["level"] = None
        session.clear()
        return {"msg":"User Logged Out", "message_flag":"success"}, 200
    
    def application_startup(self):
        """
        starts the application
        """
        return redirect(url_for('auths.home'))
    
    def create_user(self, email, pswd, prv_level):
        """
        create user
        """           
        
        if self.validate_input(email, pswd, prv_level):
            response = self.auth_util.create_user(email, pswd, prv_level)
            if response:
                logging.info(f"{session['user']}: User Created with email {email}")
                return {"flash_message": True, "message_toast":"User Created", "message_flag":"success"},200
            
            else:
                logging.error(f"{session['user']}: Unable to Creat User with email {email}")
                return {"flash_message": True, "message_toast":"Unable to create user", "message_flag":"error"},200
        else:
            logging.error(f"{session['user']}: Unable to Creat User with email {email}")
            return {"flash_message": True, "message_toast":"Unable to create user", "message_flag":"error"},200
        

    def view_user(self):
        """
        view user of applications
        """
        records = self.auth_util.get_all_users()
        return {"data":records},200
    

    def enable_disable_user(self, user_id, status):
        """
        delete user of applications
        """
        flag = self.auth_util.enable_disable_user(user_id, status)
        if flag:
            logging.info(f"{session['user']}: user {status} with User id {user_id}")
            return {"flash_message": True, "message_toast":f"User {status}", "message_flag":"success"},200
        else:
            logging.error(f"{session['user']}: user not {status} with User id {user_id}")
            return {"flash_message": True, "message_toast": f"user not {status}", "message_flag":"error"},200
        
    def enable_disable_user_from_api(self, user_email, status):
        """
        enable diable user
        """

        flag = self.auth_util.enable_disable_user_using_email(user_email, status)
        if flag:
            logging.info(f"{session['user']}: user {status} with User email {user_email}")
            return {"flash_message": True, "message_toast": f"user {status}", "message_flag":"success"},200
        else:
            logging.error(f"{session['user']}: user not {status} with User id {user_email}")
            return {"flash_message": True, "message_toast": f"user not {status}", "message_flag":"error"},200


    def update_user(self, user_id, prv_level):
        """
        update user of applications
        """

                   
        flag = self.auth_util.update_user(user_id, prv_level)
        records = self.auth_util.get_all_users()

        if flag:
            logging.info(f"{session['user']}: User's privileged level updated successfully with user id {user_id}")
            return {"flash_message": True, "message_toast":f"User Updated", "message_flag":"success"},200
        else:
            logging.error(f"{session['user']}: Unable to Update User's privileged level with user id {user_id}")
            return {"flash_message": True, "message_toast": f"Unable to Update User", "message_flag":"error"},200
        

    def update_user_from_api(self):
        """
        update user of applications
        """
        levels = ['read_only_user', 'admin', 'read_write_user']
        if not (request.args.get("email") and request.args.get("prv_level")):
            return {"error": "Incorrect Params"}, 400
        
        email, prv_level = request.args.get('email'), request.args.get('prv_level')
        if prv_level in levels:
            flag = self.auth_util.update_user_using_email(email, prv_level)
            if flag:
                logging.info(f"{session['user']}: User's privileged level updated successfully with user email {email}")
                return {"flash_message": True, "message_toast":"User updated", "message_flag":"success"},200
            else:
                logging.error(f"{session['user']}: Unable to Update User's privileged level with user email {email}")
                return {"flash_message": True, "message_toast":"Unable to update user", "message_flag":"error"},200
        return {"flash_message": True, "message_toast":"Privileged level is not available", "message_flag":"error"},200
    
    def reset_password(self, user_id):
        """
        reset user's password of applications
        """
        email = self.auth_util.get_user_email(user_id)
        if email:
            flag = self.auth_util.reset_user_password(user_id, email)
        else:
            logging.error(f"{session['user']}: Unable to Reset password for user {user_id}")
            return {"flash_message": True, "message_toast": f"Unable to Reset Password", "message_flag":"error"},200

        if flag:
            logging.info(f"{session['user']}: Password Reset for user {email}")
            return {"flash_message": True, "message_toast":f"Password Reset", "message_flag":"success"},200
        else:
            logging.error(f"{session['user']}: Unable to Reset password for user {email}")
            return {"flash_message": True, "message_toast": f"Unable to Reset Password", "message_flag":"error"},200
        

    def reset_password_from_api(self, email):
        """
        reset user's password from api
        """

        flag = self.auth_util.reset_user_password_for_api(email)

        if flag:
            logging.info(f"{session['user']}: Password Reset for user {email}")
            return {"flash_message": True, "message_toast":f"Password Reset", "message_flag":"success"},200
        else:
            logging.error(f"{session['user']}: Unable to Reset password for user {email}")
            return {"flash_message": True, "message_toast": f"Unable to Reset Password", "message_flag":"error"},200
    

    def update_password(self, email, old_pswd, new_pswd):
        """
        update your password
        """
        
        flag = self.auth_util.update_password(old_pswd, new_pswd, email)

        if flag:
            logging.info(f"{session['user']}: User Updated his password successfully")
            return {"flash_message": True, "message_toast":"password updated", "message_flag":"success"},200
        else:
            logging.error(f"{session['user']}: User Unable Updated his password")
            return {"flash_message": True, "message_toast":"unable to update password", "message_flag":"error"},200
    
    def setup_notification(self,):
        """
        setup_notification
        """
        print("setup_notification trigered")
        util = Notification_Util()
        util.setup_notifications()
    
    def send_notification(self,):
        """
        send_notification
        """
        print("send_notification trigered")
        notifier = Notification_Process_Notifier()
        notifier.process_notification()
    