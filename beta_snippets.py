#!/usr/bin/env python

# Copyright 2019 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This application demonstrates speech transcription using the
Google Cloud API.
Usage Examples:
    python beta_snippets.py transcription \
        gs://python-docs-samples-tests/video/googlework_short.mp4
    python beta_snippets.py video-text-gcs \
        gs://python-docs-samples-tests/video/googlework_short.mp4
    python beta_snippets.py track-objects resources/cat.mp4
    python beta_snippets.py streaming-labels resources/cat.mp4
    python beta_snippets.py streaming-shot-change resources/cat.mp4
    python beta_snippets.py streaming-objects resources/cat.mp4
    python beta_snippets.py streaming-explicit-content resources/cat.mp4
    python beta_snippets.py streaming-annotation-storage resources/cat.mp4 \
    gs://mybucket/myfolder
    python beta_snippets.py streaming-automl-classification resources/cat.mp4 \
    $PROJECT_ID $MODEL_ID
"""

import argparse
import io
import cv2
import numpy as np
import os
import json


def track_objects_gcs(gcs_uri):
    # [START video_object_tracking_gcs_beta]
    """Object Tracking."""
    from google.cloud import videointelligence_v1p2beta1 as videointelligence

    # It is recommended to use location_id as 'us-east1' for the best latency
    # due to different types of processors used in this region and others.
    video_client = videointelligence.VideoIntelligenceServiceClient()
    features = [videointelligence.enums.Feature.OBJECT_TRACKING]
    operation = video_client.annotate_video(
        input_uri=gcs_uri, features=features, location_id='us-east1')
    print('\nProcessing video for object annotations.')

    result = operation.result(timeout=300)
    print('\nFinished processing.\n')

    # The first result is retrieved because a single video was processed.
    object_annotations = result.annotation_results[0].object_annotations

    # Get only the first annotation for demo purposes.
    object_annotation = object_annotations[0]
    # description is in Unicode
    print(u'Entity description: {}'.format(
        object_annotation.entity.description))
    if object_annotation.entity.entity_id:
        print('Entity id: {}'.format(object_annotation.entity.entity_id))

    print('Segment: {}s to {}s'.format(
        object_annotation.segment.start_time_offset.seconds +
        object_annotation.segment.start_time_offset.nanos / 1e9,
        object_annotation.segment.end_time_offset.seconds +
        object_annotation.segment.end_time_offset.nanos / 1e9))

    print('Confidence: {}'.format(object_annotation.confidence))

    # Here we print only the bounding box of the first frame in this segment
    frame = object_annotation.frames[0]
    box = frame.normalized_bounding_box
    print('Time offset of the first frame: {}s'.format(
        frame.time_offset.seconds + frame.time_offset.nanos / 1e9))
    print('Bounding box position:')
    print('\tleft  : {}'.format(box.left))
    print('\ttop   : {}'.format(box.top))
    print('\tright : {}'.format(box.right))
    print('\tbottom: {}'.format(box.bottom))
    print('\n')
    # [END video_object_tracking_gcs_beta]
    return object_annotations

def track_objects(path):
    # [START video_object_tracking_beta]
    """Object Tracking."""
    from google.cloud import videointelligence_v1p2beta1 as videointelligence

    video_client = videointelligence.VideoIntelligenceServiceClient()
    features = [videointelligence.enums.Feature.OBJECT_TRACKING]

    

    vid = cv2.VideoCapture(path)
    success,image = vid.read()
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    v = cv2.VideoWriter('slowed_video.mp4', fourcc, vid.get(cv2.CAP_PROP_FPS), (len(image[0]),len(image)), True)
    while success:      
        success,image = vid.read()
        print('Read a new frame: ', success)
        for _ in range(3):
            v.write(image)
    v.release()
    with io.open('slowed_video.mp4', 'rb') as file:
        input_content = file.read()
    cap = cv2.VideoCapture('slowed_video.mp4')
    numFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT)#count_frames(cap)
    cap.set(cv2.CAP_PROP_POS_AVI_RATIO,1)
    length = cap.get(cv2.CAP_PROP_POS_MSEC)/1000
    fps = cap.get(cv2.CAP_PROP_FPS)#numFrames/length
    print(fps)
    print(cap.get(cv2.CAP_PROP_FPS))
    print(length)
    try:
        #if not os.path.exists('data'):
        os.makedirs('data')
    except OSError:
        print ('Error: Creating directory of data')

    

    # When everything done, release the capture
    
    # It is recommended to use location_id as 'us-east1' for the best latency
    # due to different types of processors used in this region and others.
    operation = video_client.annotate_video(
        input_content=input_content, features=features, location_id='us-east1')
    print('\nProcessing video for object annotations.')

    result = operation.result(timeout=300)
    print('\nFinished processing.\n')

    cap.set(1,1);
    ret1, img1 = cap.read()
    #print(img1)
    y, x = len(img1), len(img1[0])
    print(str(x) + "x" + str(y))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    #cv2.VideoWriter_fourcc(*'avc1')
    video = cv2.VideoWriter('tracked_object.mp4', fourcc, 10, (x,y), True) # MUST CHANGE HARD-CODED 10 INTO WHATEVER GOOGLE'S FRAME PROCESSING EXACT RATE IS
    # The first result is retrieved because a single video was processed.
    object_annotations = result.annotation_results[0].object_annotations

    #Array of JSON data by frame
    frameData = {"frames": []}

    # Get only the first annotation for demo purposes.
    object_annotation = object_annotations[0]
    for o in object_annotations:
        print('Entity id: {}'.format(o.entity.description))
        print(o.entity.description == 'ball' or o.entity.description == 'basketball')
        if o.entity.description == 'ball' or o.entity.description == 'basketball':
            object_annotation = o
            # description is in Unicode
            print('Entity description: {}'.format(
                object_annotation.entity.description))
            if object_annotation.entity.entity_id:
                print('Entity id: {}'.format(object_annotation.entity.entity_id))

            print('Segment: {}s to {}s'.format(
                object_annotation.segment.start_time_offset.seconds +
                object_annotation.segment.start_time_offset.nanos / 1e9,
                object_annotation.segment.end_time_offset.seconds +
                object_annotation.segment.end_time_offset.nanos / 1e9))

            print('Confidence: {}'.format(object_annotation.confidence))
            #video = cv2.VideoWriter('video.avi',-1,1,(1920,1080))

            # Here we print only the bounding box of the first frame in this segment
            for frame in object_annotation.frames:
                box = frame.normalized_bounding_box
                time = frame.time_offset.seconds + frame.time_offset.nanos / 1e9
                print('Time offset of the first frame: {}s'.format(time))
                """print('Bounding box position:')
                print('\tleft  : {}'.format(box.left))
                print('\ttop   : {}'.format(box.top))
                print('\tright : {}'.format(box.right))
                print('\tbottom: {}'.format(box.bottom))
                print('\n')"""

                frameData["frames"].append({
                    "time" : time,
                    "left" : box.left,
                    "top" : box.top,
                    "right" : box.right,
                    "bottom" : box.bottom
                })
                frame_no = round(fps*time)
                print(str(fps) + " " + str(time) + " " + str(frame_no))
                total_frames = cap.get(7)
                cap.set(1,frame_no);
                ret, img = cap.read()

                name = './data/frame' + str(frame_no) + '.jpg'
                print ('Creating...' + name)
                print((box.left, box.top))
                cv2.rectangle(img,(int(box.left*x), int(box.top*y)),(int(box.right*x), int(box.bottom*y)),(0, 255, 0), 3)
                #print(img)
                #cv2.imwrite(name, img)
                video.write(img)

        # [END video_object_tracking_beta]
    
    with open("frameData.json", "w") as write_file:
        json.dump(frameData, write_file)

    cap.release()
    cv2.destroyAllWindows()
    video.release()
    vid.release()
    return object_annotations




if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest='command')

    
    video_object_tracking_gcs_parser = subparsers.add_parser(
        'track-objects-gcs', help=track_objects_gcs.__doc__)
    video_object_tracking_gcs_parser.add_argument('gcs_uri')

    video_object_tracking_parser = subparsers.add_parser(
        'track-objects', help=track_objects.__doc__)
    video_object_tracking_parser.add_argument('path')


    args = parser.parse_args()

    if args.command == 'track-objects-gcs':
        track_objects_gcs(args.gcs_uri)
    elif args.command == 'track-objects':
        track_objects(args.path)