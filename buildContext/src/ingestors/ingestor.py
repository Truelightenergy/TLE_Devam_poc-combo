import re
import os
import logging
import boto3
import datetime
from ingestors.nonenergy import NonEnergy
from ingestors.energy import Energy
from ingestors.rec import Rec
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)

class ParseError(Exception):
    pass

class ExistingDataError(Exception):
    pass

class SQLError(Exception):
    pass


class Ingestion:
    def __init__(self):

        self.non_energy = NonEnergy()
        self.energy = Energy()
        self.rec = Rec()

    def validate(self, file_name):
        """
        validates the incoming data file name
        """

        file_name_components_pattern = re.compile(".*/(.+?)_(.+?)_(.+?)_(.+)?.csv$") # len(5-6)
        
        matched = file_name_components_pattern.search(file_name)
        if matched == None:
            return ParseError(f"failed to parse {file_name} - regex")
        
        results = matched.groups()
        if len(results) != 4: # todo - confirm works with and without "_cob" extension in name
            return ParseError(f"failed to parse {file_name} - component count")

        # controlArea == iso
        # issue == curveTime
        (curveType, controlArea, curveDate, issue) = results    
        curveType = os.path.basename(curveType).replace("Curve","")

        # todo - should error if timestamp/date is missing or invalid instead of trying to fix here, so remove this block
        # add default value here for time, maybe not worth it, need to see how it flows
        timeComponent = None
        cob = None
        if issue is None:    
            timeComponent = "000000"
        else:
            timeStamp_cob = issue.split("_")
            if len(timeStamp_cob)==2:
                timeStamp, cob = timeStamp_cob # drop leading underscore; else fix regex above
                timeComponent = timeStamp
            elif int(timeStamp_cob[0]):
                timeComponent = timeStamp_cob[0]
            else:
                return ParseError(f"failed to parse {file_name} - time component")

        timestamp = datetime.datetime.strptime(curveDate+timeComponent, "%Y%m%d%H%M%S")

        logging.info(f"parsed file meta data: {file_name}, {curveType}, {controlArea}, {timestamp}")
        
        return TLE_Meta(file_name, curveType, controlArea, timestamp)

    def process(self, files, steps):
        """
        Performs the validation 
        """
        meta = None
        result = "Unable to perform Insertion"
        # validate
        valid = []
        for f in files:
            meta = steps["validate_data"](f)
            if meta is None or isinstance(meta, ParseError):
                return meta # all files must pass, in case systematic errors
            else:
                valid.append(meta)

        # ingestion to the database
        for m in valid:
            result = steps["ingestion"](m) # store before we place in db
            if result is not None:
                if result in ["Data Inserted", "Data updated"]:
                    continue
                else:
                    return result

        # insert db / api check each as we go (need to find way to redo/short-circuit/single file, etc.)
        for m in valid:
            result = steps["storage"](m) # insert/update db
            if result is not None:
                return result
            
        return result
    
    # todo - s3
    def storage(self, data):
        """
        store the data to s3 bucket
        """
        return self.upload_file(data.fileName)

    def upload_file(self, file_name, bucket='tle-trueprice-api-source-data', object_name=None):

        """
        Upload a file to an S3 bucket
        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)

        condition =(not "LOCALDEV" in os.environ)
        # upload file to s3
        s3_client = None
        if condition:
            s3_client = boto3.client('s3') # REAL
        else:
            # local minio -- http://127.0.0.1:9090/access-keys/new-account
            clientArgs = {
                'aws_access_key_id': '79ojwH4ClMDtwoT6',
                'aws_secret_access_key': 'dtgAbKEhaV2vgm02QH387C97hOPwCoo2',
                'endpoint_url': 'http://localhost:9000',
                'verify': False
            }
            s3_client = boto3.resource("s3", **clientArgs)

        try:        
            if condition: # prod
                response = s3_client.upload_file(file_name, bucket, object_name)
            else: # local dev, not sure why minio doesn't have upload_file and prod doesn't have Bucket
                
                response = s3_client.Bucket(bucket).upload_file(file_name, object_name)
                
        except Exception as e:
            logging.error(e)
            return "failed to upload to s3"
        logging.info(f"{file_name} uploaded to s3")
        return "Data Inserted"

    def validate_api(self, file_name):
        """
        validate api request
        """
        pass


    def call_ingestor(self,file):
        """
        performing several operations based on the file type
        """

        files = [file]
        result = None
        if re.search("nonenergy", file, re.IGNORECASE):
            result = self.process(files, {"validate_data":self.validate, "ingestion":self.non_energy.ingestion, "storage":self.storage, "validate_api": self.validate_api})
        elif re.search("energy", file, re.IGNORECASE):
            result = self.process(files, {"validate_data":self.validate, "ingestion":self.energy.ingestion, "storage":self.storage, "validate_api": self.validate_api})
        elif re.search("rec", file, re.IGNORECASE):
            result = self.process(files, {"validate_data":self.validate, "ingestion":self.rec.ingestion, "storage":self.storage, "validate_api": self.validate_api})
        else:
            result = "Shouldn't be here"
        

        return result

class TLE_Meta:
    def __init__(self, fileName, curveType, controlArea, curveTimestamp):
        self.fileName = fileName
        self.curveType = curveType.lower()
        self.controlArea = controlArea.lower()
        self.curveStart = curveTimestamp
    
    def snake_timestamp(self):
        return self.curveStart.strftime("%Y_%m_%d_%H_%M_%S")