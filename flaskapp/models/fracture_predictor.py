import sys
import numpy as np
import cv2
import onnxruntime



def load_img(img_file, img_mean=0, img_scale=1/255):
    img = cv2.imread(img_file)[:, :, ::-1]
    img = cv2.resize(img, (640, 640), interpolation=cv2.INTER_LINEAR)
    img = (img - img_mean) * img_scale
    img = np.asarray(img, dtype=np.float32)
    img = np.expand_dims(img,0)
    img = img.transpose(0,3,1,2)
    return img

def model_inference(model_path, image_np):
    providers = ['CPUExecutionProvider']
    session = onnxruntime.InferenceSession(model_path, providers=providers)
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    output = session.run([output_name], {input_name: image_np})
    return output[0][:, :6]

def post_process(output, score_threshold=0.6):
    det_bboxes, det_scores, det_labels = output[:, 0:4], output[:, 4], output[:, 5]
    id2names = {
        0: "Bone Anomaly", 1: "Bone Lesion", 2: "Foreign Body", 
        3: "Fracture", 4: "Metal", 5: "Periosteal Reaction", 
        6: "Pronator Sign", 7:"Soft Tissue", 8:""
    }

    img_features = dict()
    for idx in range(len(det_bboxes)):
        if det_scores[idx]>score_threshold and int(det_labels[idx]) != 8:
            img_features[id2names[int(det_labels[idx])]] = max(img_features.get(id2names[int(det_labels[idx])], 0), det_scores[idx]*100)
    return img_features


MODEL_PATH = "models/yolov7-p6-bonefracture.onnx"

def fracture_predictor(img_path):
    img = load_img(img_path)
    out_txt = post_process(model_inference(MODEL_PATH, img))
    return out_txt

if __name__ == '__main__':
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        print( fracture_predictor(img_path) )