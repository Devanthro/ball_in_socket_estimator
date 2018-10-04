#!/usr/bin/env python
import numpy as np
from keras.models import Sequential
import numpy as np
import pandas
import rospy
import tensorflow
import tf
import geometry_msgs.msg
from pyquaternion import Quaternion
from keras.layers import Dense, Activation
from keras.models import model_from_json
import pandas
import rospy
import tf
import geometry_msgs.msg
from pyquaternion import Quaternion
from roboy_communication_middleware.msg import MagneticSensor
from visualization_msgs.msg import Marker
import sys, select
from pyquaternion import Quaternion
import matplotlib.pyplot as plt
import numpy
import itertools

def main():

    # load json and create model
    json_file = open('/home/letrend/workspace/roboy_middleware/src/ball_in_socket_estimator/python/model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    # load weights into new model
    model.load_weights("/home/letrend/workspace/roboy_middleware/src/ball_in_socket_estimator/python/model.h5")
    print("Loaded model from disk")

    rospy.init_node('replay')
    listener = tf.TransformListener()
    broadcaster = tf.TransformBroadcaster()

    magneticSensor_pub = rospy.Publisher('roboy/middleware/MagneticSensor', MagneticSensor, queue_size=1)

    dataset = pandas.read_csv("/home/letrend/workspace/roboy_middleware/src/roboy_controller/scripts/data.log", delim_whitespace=True, header=1)
    dataset = dataset.values[1:,0:]
    quaternion_set = dataset[0:,1:5]
    sensors_set = dataset[0:,8:]
    samples = len(sensors_set[:, 0])
    t = 0
    t0 = rospy.Time.now()

    for (q, s) in itertools.izip(quaternion_set, sensors_set):
        s_input = s.reshape((1,9))/1000
        quat = model.predict(s_input)
        rospy.loginfo_throttle(1, (quat[0,0],quat[0,1],quat[0,2],quat[0,3]))
        norm = numpy.linalg.norm(quat)
        quat = (quat[0,0]/norm,quat[0,1]/norm,quat[0,2]/norm,quat[0,3]/norm)
        if(t%1==0):
            broadcaster.sendTransform((0, 0, 0),
                                      q,
                                      rospy.Time.now(),
                                      "tracker_1",
                                      "world")
            broadcaster.sendTransform((0, 0, 0),
                                      quat,
                                      rospy.Time.now(),
                                      "predict",
                                      "world")
            msg = MagneticSensor()
            msg.id = 5
            msg.sensor_id = [0, 1, 2]
            msg.x = [s[0], s[3], s[6]]
            msg.y = [s[1], s[4], s[7]]
            msg.z = [s[2], s[5], s[8]]
            magneticSensor_pub.publish(msg)
            print("%d/%d\t\t%.3f%%" % (t, samples, (t/float(samples))*100.0))
            t0 = rospy.Time.now()
        t = t + 1

    # for


    # Signal handler
    rospy.spin()


if __name__ == '__main__':
    main()
