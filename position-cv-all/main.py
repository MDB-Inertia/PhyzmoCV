import argparse
import io
import os
from flask import jsonify
import json
import logging

def track_objects_gcs_all(request):
    # [START video_object_tracking_gcs_beta]
    
    # Initialize request
    gcs_uri = request.args.get('uri', '')
    if not gcs_uri:
        return jsonify({'error': 'uri parameter as input is needed'})
    logging.info('input: {}'.format(gcs_uri))
    
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

    #Array of JSON data by frame
    objectsData = {}

    # Get only the first annotation for demo purposes.
    
    for object_annotation in object_annotations:
        print('Entity id: {}'.format(object_annotation.entity.description))
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
        if object_annotation.entity.description not in objectsData:
            objectsData[object_annotation.entity.description] = []
        # Here we print only the bounding box of the first frame in this segment
        for frame in object_annotation.frames:
            box = frame.normalized_bounding_box
            time = frame.time_offset.seconds + frame.time_offset.nanos / 1e9
            print('Time offset of the first frame: {}s'.format(time))
            objectsData[object_annotation.entity.description].append({
                "time" : time,
                "left" : box.left,
                "top" : box.top,
                "right" : box.right,
                "bottom" : box.bottom
            })


    # [END video_object_tracking_beta]
    for obj in objectsData.keys():
        objectsData[obj] = sorted(objectsData[obj], key = lambda i: i['time']) #sort by time for each object
    print(objectsData.keys()) # Descriptions for all objects
    jsonData = json.dumps(objectsData)

    return jsonData