from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.face import FaceClient
from azure.ai.vision.face.models import (
    FaceDetectionModel,
    FaceRecognitionModel,
    FaceAttributeTypeDetection03,
    FaceAttributeTypeRecognition04,
)

from config import Config


with FaceClient(endpoint=Config.AZURE_FACE_ENDPOINT, credential=AzureKeyCredential(Config.AZURE_FACE_KEY)) as face_client:
    sample_file_path = "jeff.jpg"
    with open(sample_file_path, "rb") as fd:
        file_content = fd.read()

    result = face_client.detect(
        file_content,
        # The latest detection model.
        detection_model=FaceDetectionModel.DETECTION03,
        # The latest recognition model.
        recognition_model=FaceRecognitionModel.RECOGNITION04,
        return_face_id=True,
        return_face_attributes=[
            FaceAttributeTypeDetection03.HEAD_POSE,
            FaceAttributeTypeDetection03.MASK,
            FaceAttributeTypeRecognition04.QUALITY_FOR_RECOGNITION,
        ],
        return_face_landmarks=True,
        return_recognition_model=True,
        face_id_time_to_live=120,
    )

    print(f"Detect faces from the file: {sample_file_path}")
    for idx, face in enumerate(result):
        print(f"----- Detection result: #{idx+1} -----")
        print(f"Face: {face.as_dict()}")
