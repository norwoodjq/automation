# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 11:06:05 2017

@author: norwood
"""
# General
import os.path
import sys
from time import sleep
import datetime
from multiprocessing.dummy import Pool as ThreadPool
from threading import Lock

#from multiprocessing import Pool
#import itertools

class robot(object):
    def __init__(self, name):
        self.name = name
        self.available = True
        #  connect to robot
        pass
    def xfer(self, device1, device2, job):
        self.available = False

        if device1.status == 'xfer lock' and device2.status == 'xfer unlock':
            device1.status = 'xfer unlock'
            device2.status = 'xfer lock'
    #            log('\t\033[;32mxfer from:%s%d to: %s%d %s\033[00m' %(device1.type, device1.name, device2.type, device2.name, job.jobID))
            log('\txfer from: %s%d to: %s%d job:%s' %(device1.type, device1.name, device2.type, device2.name, job.jobID))
                # command to move robot
                # block till finished
            
                # log('\t\033[;32mfinished move from:%s%d to: %s%d %s\033[00m' %(device1.type, device1.name, device2.type, device2.name, job.jobID))   
            return True
        elif device2.type == 'storage':
            if device2.accessible:
                device1.status = 'xfer unlock'
#                    log('\t\033[;32mxfer from:%s%d to: %s%d %s\033[00m' %(device1.type, device1.name, device2.type, device2.name, job.jobID))
                log('\txfer from:%s%d to: %s%d job:%s' %(device1.type, device1.name, device2.type, device2.name, job.jobID))

                    # command to move robot
                    # block till finished                           
                return True
            else:
                log('storage not accessible')
                return False
        else:
            log('xfer status error %s%d:%s %s%d:%s' %(device1.type, device1.name, device1.status, device2.type, device2.name, device2.status))
            return False

    def pick(self, device, job): 
        self.available = False
        if device.type == 'storage': 
            if device.count<0:
                log('pick status error:', device.count)
                log('\t%s%d out of platforms job:%s' %(device.type, device.name, job.jobID))
                return
        elif device.status == 'xfer unlock':
            log('pick status error:', device.status)
            log('\t%s%d  has no platform job:%s' %(device.type, device.name, job.jobID))
            return
        else:
            device.status = 'xfer unlock'  # platform is removed by pick
#            log('\t\033[;32mrobot pick from: %s%d %s\033[00m' %(device.type, device.name, job.jobID))
            log('\trobot pick from: %s%d job:%s' %(device.type, device.name, job.jobID))
        device.accessible = True
        sleep(1)
  
#  issue robot pick command here
            
        return
            
    def place(self, device, job):        
        #  check device status should happen before place command
#        log('\t\033[;32mrobot place to: %s%d %s\033[00m' %(device.type, device.name, job.jobID))
        log('\trobot place to: %s%d job:%s' %(device.type, device.name, job.jobID))
        if device.status == 'xfer unlock':
            device.status = 'xfer lock'
            device.accessible = False
        else: 
            log('place status error: %s%d %s job:%s' %(device.type, device.name, device.status, job.jobID))
        sleep(1)
                  
    def move(self, device, job):
        self.available = False
        if device.accessible:
#            log('\t\033[;32mrobot move to: %s%d %s\033[00m' %(device.type, device.name, job.jobID))
            log('\trobot move to: %s%d %s' %(device.type, device.name, job.jobID))
            device.status = 'xfer lock'
            device.accessible = False
    def isMoveDone(self):
        # query robot to determine if move is complete
        return True
    
class deviceList(object):
    def __init__(self):
        self.robot = []
        self.device_with_door = []
        self.device_with_lifter = []
        self.entry = []
        self.inspector = []
        self.exit = []
        self.quarantine = []

#***************
# devices
#***************
class device(object):
    def __init__(self, name):
        self.type = None
        self.name = name
        self.accessible = True
    def isAvailable(self):
        return self.accessible

class device_with_door(device):
    def __init__(self, name):
        super().__init__(name)
        self.type = 'device_with_door'
        self.status = 'xfer unlock'
    def connect(self):
        # connect to device_with_door
        pass
    def getdevice_with_doorStatus(self):   # these need to match status from device_with_door
        # check actual device_with_door status
        return self.status  
    def openDoor(self):
        pass
    def isDoorOpen(self):
        # check status of door
  #      log('door is open')
        return True
    def closeDoor(self):
        pass
    def printIt(self,job):
        #send job to device_with_door
        sleep(job.protocol.steps[job.protocol.current].est_process_time)
        self.status = 'xfer lock'
        
class device_with_lifter(device):
    def __init__(self, name):
        super().__init__(name)
        self.status = 'xfer unlock'
        self.type = 'device_with_lifter'
        # connect to device_with_lifter
    def getdevice_with_lifterStatus(self):
        # check actual device_with_lift status
        return self.status
    def raiseLifter(self):
        pass
    def isLifterRaised(self):
 #       log('platform lifter is raised')
        return True
    def lowerLifter(self):
        pass
    def washIt(self, job):
        sleep(job.protocol.steps[job.protocol.current].est_process_time)
        self.status = 'xfer lock'
        
class inspector(device):
    def __init__(self, name):
        super().__init__(name)
        self.type = 'inspector'
        self.status = 'xfer unlock'
        # connect to camera
    def inspectIt(self, job):
        sleep(job.protocol.steps[job.protocol.current].est_process_time)
        
class storage(device):
    def __init__(self, name):
        super().__init__(name)
        self.type = 'storage'
        self.status = 'xfer unlock'
        self.count = 0  # the current number of platforms in storage'
    def storeIt(self, job):
        sleep(job.protocol.steps[job.protocol.current].est_process_time)
        self.count+=1
        self.status = 'xfer lock'
        if self.count >= PLATFORM_STORAGE_SIZE:
            self.accessible = False
            log('storage full')
            return False
        return True
            
    def removeIt(self, job): 
        sleep(job.protocol.steps[job.protocol.current].est_process_time)
        if self.count>0:
            self.count-=1
        else:
            self.accessible = False
            self.status = 'xfer unlock'
        return self.count
        
    def quarantineIt(self, job):
        sleep(job.protocol.steps[job.protocol.current].est_process_time)
        if job.DeviceList.robot[0].available:
            log('no platform in gripper')
        else:
            job.DeviceList.robot[0].place(job.DeviceList.quarantine[0], job)
            while not job.DeviceList.robot[0].isMoveDone():
                sleep(1)
            sleep(1)
            job.DeviceList.robot[0].available = True
            log('job quarantined', job.jobID)
      
#**************** 
# processes
#****************
class process(object):
    def __init__(self, job):
        self.msg = None
        self.est_process_time = 1
        self.sleepcycles = 0
    def runProcess(self, job):    # runs findAvailable, then runStep, then cleanup
#            log(datetime.datetime.now().isoformat(), '\033[;35m'+job.jobID+'\033[00m', '\033[;36m'+self.msg+'\033[00m')
#        log('%s\t%s\t%s' %(datetime.datetime.now().isoformat(), self.msg, job.jobID))
        try:
            self.sleepcycles=0
            while not self.findAvailable(job): 
#                    log('\twaiting for available\033[;35m'+job.jobID+'\033[00m', '\033[;36m'+self.msg+'\033[00m')
                log('\twaiting for %s device. job:%s' %(self.msg, job.jobID))
                sleep(5)  # wait five seconds before checking again for availability
                self.sleepcycles+=1
  # for debug only                  
                if self.sleepcycles>4:
                    log('deadlock timeout. exiting...')
                    deviceStatus(job)
                    sys.exit(0) 
  # end debug
        except Exception as e:
            log('failed resource assignment %s job:%s' %(self.msg,job.jobID))
            log(e.with_traceback)
            return False 
#        try: 
        goodrun = self.runStep(job)     # main process
        if not goodrun:
            log('run not good %s job:%s' %(self.msg, job.jobID))
            return False
#        except Exception as e:
#            log('failed process '+ job.jobID+ ' '+ self.msg)
#            log(e.with_traceback)
 #           return False
        try:
            goodend = self.cleanup(job)  # post-processing
            if goodend: 
 #                   log('finish', job.jobID, self.msg)
                pass
                return True
        except:
            log('failed cleanup %s, job:%s' %(self.msg, job.jobID))
            return False                        
    
class DoorDevice(process):
    def __init__(self, job):
        super().__init__(job)
        self.msg = 'DoorDevice'
        self.est_process_time = 5
    def findAvailable(self, job):
        for i in range (len(job.DeviceList.device_with_door)):
     #           log('\tfindAvailable device_with_door', job.jobID)
     #           log(job.DeviceList.device_with_door[i].getdevice_with_doorStatus())
            if job.DeviceList.device_with_door[i].accessible and job.DeviceList.device_with_door[i].getdevice_with_doorStatus()=='xfer unlock':
                job.DeviceList.device_with_door[i].openDoor()
                if not job.DeviceList.device_with_door[i].isDoorOpen():
                    job.DeviceList.device_with_door[i].openDoor()
                while not job.DeviceList.device_with_door[i].isDoorOpen():
                    sleep(1)
                if job.DeviceList.robot[0].available:
                    log('no platform in gripper')
                    return False
                else:
                    job.DeviceList.robot[0].place(job.DeviceList.device_with_door[i], job)   # robot moves platform
                    while not job.DeviceList.robot[0].isMoveDone():
                        sleep(1)
                        sleep(1)
                    job.DeviceList.robot[0].available = True
                    job.DeviceList.device_with_door[i].closeDoor()
                    job.position = job.DeviceList.device_with_door[i]       # update the position of the platform
                    job.DeviceList.device_with_door[i].accessible = False  # lock out device_with_door till post inspection
                    job.device_with_door = job.DeviceList.device_with_door[i]  # assign available device_with_door to job
                    return True
#       no device_with_door avialable
        log('\tNo device_with_door Available', job.jobID)
        return False

    def runStep(self, job):  
#        log('\trunning print job:', job.jobID)
        try:   
            job.device_with_door.printIt(job) # start the print
            return True
        except:
            return False
    def cleanup(self, job):
 #           log('\tpost print cleanup', job.jobID)
        try:
            return True
        except:
            return False
   
class LiftDevice(process):
    def __init__(self, job):
        super().__init__(job)
        self.msg = 'LiftDevice'
        self.est_process_time = 2
    def findAvailable(self, job):
        for i in range (len(job.DeviceList.device_with_lifter)):
            if job.DeviceList.device_with_lifter[i].accessible and job.DeviceList.device_with_lifter[i].status == 'xfer unlock':
                if not job.DeviceList.device_with_lifter[i].isLifterRaised():
                    job.DeviceList.device_with_lifter[i].raiseLifter()
                while not job.DeviceList.device_with_lifter[i].isLifterRaised():
                    sleep(1)
                while not job.DeviceList.robot[0].available:
                    sleep(1)
                job.DeviceList.robot[0].xfer(job.position, job.DeviceList.device_with_lifter[i], job)
                while not job.DeviceList.robot[0].isMoveDone():
                        sleep(1)
                sleep(1)
                job.DeviceList.robot[0].available = True
                job.position = job.DeviceList.device_with_lifter[i]       # update the position of the platform
                job.DeviceList.device_with_lifter[i].accessible = False  # lock out device_with_lifter 
                job.device_with_lifter = job.DeviceList.device_with_lifter[i]
                return True
            else: 
                return False
    def runStep(self, job):
#        log('\trunning wash job:', job.jobID)
        try:
            if not job.protocol.inspection:
                job.device_with_door.accessible = True
                log('\tProtocol does not include inspection, unlocking device_with_door%d job:%s' %(job.device_with_door.name, job.jobID))
            return True            
        except:
            log('exception in LiftDevice runStep')
            return False
    def cleanup(self, job):
#        log('\tpost wash cleanup', job.jobID)
        try:
            return True
        except:
            log('exception in wash cleanup')
            return False
        
class inspection(process):
    def __init__(self, job):
        super().__init__(job)
        self.msg = 'inspection'
        self.est_process_time = 1
    def test(self, job):
        test_result = True  #  this should be replaced with an actual test
        if test_result:
            log('\trunning inspection test to validate print', job.jobID)
            job.validation = True
            return True
        else:
            job.validation = False
            return False
    def findAvailable(self, job):
        if job.DeviceList.inspector[0].accessible and job.DeviceList.inspector[0].status == 'xfer unlock':
            while not job.DeviceList.robot[0].available:
                sleep(1)
            job.DeviceList.robot[0].xfer(job.position, job.DeviceList.inspector[0], job)  # robot grabs the platform from current position
            while not job.DeviceList.robot[0].isMoveDone():
                sleep(1)
            sleep(1)
            job.DeviceList.robot[0].available = True
            job.DeviceList.inspector[0].accessible = False  # lock out inspection
            job.DeviceList.inspector[0].status = 'xfer lock'
            job.position.accessible = True
            job.position.status = 'xfer unlock'
            job.position = job.DeviceList.inspector[0]
            return True
        else:
            return False
    def runStep(self, job):
        try:
            if self.test(job):
                job.device_with_door.accessible = True
                log('\tinspection complete, unlocking device_with_door%d job:%s' %(job.device_with_door.name, job.jobID))
                return True
        except:
            log('runStep exception during inspection')
            return False
    def cleanup(self, job):
 #           log('\tpost inspection cleanup', job.jobID)
        try:
            return True
        except:
            return False    
    
class entrance(process):
    def __init__(self, job):
        super().__init__(job)
        self.msg = 'retrieving empty platform'
        self.est_process_time = 1
    def findAvailable(self, job):
        try: # pulls next empty platform from entry storage position
            pass
 #           log('get next platform')
#          the entrance device is always available
#           check whether platforms are present in runStep method
            return True
        except Exception as e:
            log(e.with_traceback)
            return False
    def runStep(self, job):
        if job.DeviceList.entry[0].accessible:
            while not job.DeviceList.robot[0].available:
                sleep(1)            
            job.DeviceList.robot[0].pick(job.DeviceList.entry[0], job)
            while not job.DeviceList.robot[0].isMoveDone():
                sleep(1)
            sleep(1)
            platforms = job.DeviceList.entry[0].removeIt(job)
            log('\tRemoving platform. There are %d more. job:%s' %(platforms, job.jobID))
            return True
        else:
            log('entry[0] not accessible')
            return False
    def cleanup(self, job):
        try:
 #           log('post entrance cleanup')
            return True
        except:
            return False 

class egress(process):
    def __init__(self, job):
        super().__init__(job)
        self.msg = 'storing finished print'
        self.est_process_time = 1
    def findAvailable(self, job):
#           log('put platform in next empty spot', job.jobID)
        try: # pulls next empty platform from entry storage position
            return True
        except:
            return False
    def runStep(self, job):
        log('\trunning exit', job.jobID)
        try:
            if job.validation:
                job.DeviceList.exit[0].storeIt(job)
                while not job.DeviceList.robot[0].available:
                    sleep(1)   
                job.DeviceList.robot[0].xfer(job.position, job.DeviceList.exit[0], job)
                while not job.DeviceList.robot[0].isMoveDone():
                    sleep(1)
                job.DeviceList.robot[0].available = True
            else:
                job.DeviceList.quarantine[0].quarantineIt(job)
            if not job.position.type=='device_with_door':
                job.position.accessible = True
            return True
        except:
            return False
    def cleanup(self, job):
 #           log('\tpost exit cleanup', job.jobID)
        try:
            return True
        except:
            return False 

#******************
# protocols
#******************
class protocol(object):
    def __init__(self):
        self.steps = []
        self.current=0
        self.done = False
        self.inspection = False
        self.name = 'Unnamed'
    def runProtocol(self, job):
        stepindex = 0
        for step in self.steps:
            log('%s protocol %s step:%d %s job:%s' %(datetime.datetime.now().isoformat(), self.name, stepindex, self.steps[stepindex].msg, job.jobID))
            stepindex+=1
#                sleep(1)
            goodrun = step.runProcess(job)
            if goodrun:
                self.current+=1
            else:
                log('protocol error, step %d of %d' %(self.current+1, len(self.steps)))
        job.done = True
        self.done = True
        
class ProtocolWithInspection(protocol):
    def __init__(self, job):
        super().__init__()
        self.name = 'ProtocolWithInspection'
        self.inspection = True
        self.steps.append(entrance(job))
        self.steps.append(DoorDevice(job))
        self.steps.append(LiftDevice(job))
        self.steps.append(inspection(job))   
        self.steps.append(egress(job))
        
class RackDoorLiftRack(protocol):
    def __init__(self, job):
        super().__init__()
        self.name = 'RackDoorLiftRack'
        self.steps.append(entrance(job))
        self.steps.append(DoorDevice(job))
        self.steps.append(LiftDevice(job))  
        self.steps.append(egress(job))
    
#*******************
# jobs
#*******************
        
class job(object):
    def __init__(self, jobID, DeviceList):
        self.jobID = jobID
        self.protocol = None
        self.DeviceList = DeviceList     #list of all devices
        self.device_with_door = None        #device_with_door used for this job  
        self.device_with_lifter = None
        self.position = None   # the device where the platform currently sits
        self.validation = False
        self.done = False
  
class job_queue(object):
    def __init__(self, devices):
        self.queue = []
        self.devices = devices
        self.getQueue()
    def getQueue(self):
        NUMJOBS=5 
        for i in range(NUMJOBS):
            Job = job('job%02d' %(i), self.devices)  # test jobID as a string formated as 'jobXX'
#            Job.protocol = simpleProtocol(Job)      # this protocol requires validation
            Job.protocol = RackDoorLiftRack(Job)   # no validation in this protocol
            self.queue.append(Job)
        
def runJob(job):
    if not job.protocol.inspection:
        job.validation = True     # this will bypass inspection check in exit process
    job.position = job.DeviceList.entry[0]
    job.protocol.runProtocol(job)
    job.done = True
    log('job complete:%s' %(job.jobID))
    return

def deviceStatus(job):
    log('device status query...')
    for device in job.DeviceList:
        log('%s%d accessible: %s' %(device.type, device.status, device.accessible))
    return

#******************
# intialization vector
#******************

NUMBER_OF_DOORDEVICES = 3
NUMBER_OF_LIFTDEVICES = 1
PLATFORM_STORAGE_SIZE = 10

def initDevices(DeviceList):
    device_enumerator=0
    DeviceList.robot.append(robot('Robot0'))
 #   log('\033[;32mRobot0\033[00m')
    log('Robot0')
    DeviceList.entry.append(storage(0))
    DeviceList.entry[0].status = 'xfer lock'
    device_enumerator=0
#    log('\033[;33mEntry_storage\033[00m enumeration: {device_enumerator}'.format(**locals()))
    log('Entry_storage\t  enumeration: {device_enumerator}'.format(**locals()))
    for i in range(NUMBER_OF_DOORDEVICES):
        DeviceList.device_with_door.append(device_with_door(i))
        device_enumerator+=1
#        log('\033[;33mdevice_with_door{i}\033[00m\t enumeration: {device_enumerator}'.format(**locals()))   
        log('device_with_door{i}\t  enumeration: {device_enumerator}'.format(**locals()))   
    for i in range(NUMBER_OF_LIFTDEVICES):
        DeviceList.device_with_lifter.append(device_with_lifter(i))
        device_enumerator+=1
#        log('\033[;33mdevice_with_lifter{i}\033[00m\t enumeration: {device_enumerator}'.format(**locals()))
        log('device_with_lifter{i}\t\t  enumeration: {device_enumerator}'.format(**locals()))
#    DeviceList.inspector.append(inspector(0))
#    device_enumerator+=1
#    log('\033[;33mInspector{i}\033[00m    enumeration: {device_enumerator}'.format(**locals()))
#    log('Inspector{i}\t  enumeration: {device_enumerator}'.format(**locals()))
    DeviceList.exit.append(storage(1))
    device_enumerator+=1
#    log('\033[;33mQuarantine{i}\033[00m   enumeration: {device_enumerator}'.format(**locals()))
    log('Quarantine{i}\t  enumeration: {device_enumerator}'.format(**locals()))
    DeviceList.quarantine.append(storage(2))
    device_enumerator+=1
#    log('\033[;33mExit_storage{i}\033[00m enumeration: {device_enumerator}'.format(**locals()))
    log('Exit_storage{i}\t  enumeration: {device_enumerator}'.format(**locals()))
    return DeviceList

def sampleQueue():
    DeviceList = initDevices(deviceList())
    joblist = job_queue(DeviceList)  # builds a sample job queue with 5 jobs
    queue=[]
    log('')
#    log('\033[;34mjob queue\033[00m')
    log('job queue')
    log('-----------------------------')
    for Job in joblist.queue:
#        log('\033[;35m'+Job.jobID+'\033[00m')
        log('job: %s\t protocol: %s' %(Job.jobID, Job.protocol.name))
        Job.DeviceList.entry[0].storeIt(Job)
        Job.DeviceList.entry[0].status = 'xfer lock'
        queue.append(Job)
    log(DeviceList.entry[0].count,' platforms loaded')
    log('')
    return queue

def dothis():# test function runs one job, returns the job
    Queue = sampleQueue()
    runJob(Queue[0])
    return Queue[0]
    
def testHarness(f):
    # initialize devices
    log('')
#    log('\033[;34mdevice list\033[00m')
    log('device list')
    log('-----------------------------')
    Queue = sampleQueue()
    pool = ThreadPool(NUMBER_OF_DOORDEVICES) # number of device_with_doors limits simultaneous jobs
    pool.map(runJob, Queue)
    pool.close()
    pool.join()
    return

def log_init():
    save_path='C:/Automation/logs/'
    #os.makedirs(save_path, exist_ok=True)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    filename = 'log_'+str(datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) +'.txt'
    completefilename = os.path.join(save_path, filename)
    return completefilename

def job_queue_init():
    save_path='C:/Automation/jobs/'
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    jobqueue = os.path.join(save_path, 'job_queue.txt')
    jobspending = os.path.join(save_path, 'pending_jobs.txt')
    jobsdone = os.path.join(save_path, 'jobs_finished.txt')
    
 
MasterLock = Lock()
log_file = log_init()

def log(*args):
    text=''
    for arg in args:
        text+=str(arg)
    with MasterLock:
        print(text)
        with open(log_file, 'a') as f:
            f.write(text+'\n')

#******************
# main
#******************

if __name__ == "__main__":
    testHarness(log_file)
    pass